#!/usr/bin/env python3
import sys
import json
import urllib.request

SLACK_WEBHOOK_URL = "URL"

# Explications et actions pour l'administrateur systeme selon le SID Snort
EXPLICATIONS_ADMIN = {
    "1000004": {
        "menace": "Injection SQL (SQLi) sur l'application web DVWA.",
        "impact": "Critique : risque d'exfiltration, de modification ou de suppression de la base MariaDB.",
        "action": "1. Bloquer l'IP source\n2. Inspecter les logs\n3. Utiliser des requêtes préparées dans le code PHP."
    },
    "1000006": {
        "menace": "Exécution de commande à distance (RCE) via formulaire POST.",
        "impact": "Critique : compromission du serveur sous l'utilisateur `www-data`.",
        "action": "1. Isoler la machine ou bloquer l'IP source immédiatement\n2. Vérifier les processus actifs et connexions \n"
    },
    "1000003": {
        "menace": "Attaque par force brute sur le service SSH (port 22).",
        "impact": "Moyen : tentative de prise de contrôle d'un compte par dictionnaire.",
        "action": "1. Vérifier `/var/log/auth.log`\n2. Désactiver l'authentification par mot de passe au profit des clés SSH."
    },
    "1000005": {
        "menace": "Traversée de répertoire (Path Traversal) visant `/etc/passwd`.",
        "impact": "Moyen : divulgation de la liste des comptes du système Linux.",
        "action": "1. Vérifier les logs Apache\n2. Filtrer les séquences `../`"
    }
}

def envoyer_slack(message_texte):
    if not SLACK_WEBHOOK_URL in SLACK_WEBHOOK_URL:
        return
    payload = json.dumps({"text": message_texte}).encode("utf-8")
    req = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req, timeout=5)

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            snort = data.get("snort", {})
            sid = str(snort.get("sid", "Inconnu"))
            msg = snort.get("msg", "Alerte Snort")
            prio = str(snort.get("priority", "1"))
            classtype = snort.get("classification", "Non classifié")
            src_ip = snort.get("src_ip", "Inconnue")
            src_port = snort.get("src_port", "N/A")
            dst_ip = snort.get("dst_ip", "Inconnue")
            dst_port = snort.get("dst_port", "N/A")
            proto = snort.get("proto", "TCP")
            timestamp = data.get("@timestamp", "N/A")

            info = EXPLICATIONS_ADMIN.get(sid, {
                "menace": "Activité réseau anormale détectée par Snort.",
                "impact": "Risque potentiel pour la sécurité du service ciblé.",
                "action": "Analyser l'événement dans Kibana."
            })

            action_personnalisee = info["action"].replace("<src_ip>", src_ip)

            texte_slack = (
                f"*[ALERTE SOC - PRIORITÉ {prio}] {msg}*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• *Date :* `{timestamp}`\n"
                f"• *Signature :* `{msg}` (SID: `{sid}` | `{classtype}`)\n"
                f"• *Flux réseau :* `{src_ip}:{src_port}` ➔ `{dst_ip}:{dst_port}` ({proto})\n\n"
                f"*Explication à l'administrateur :*\n"
                f"• *Nature de la menace :* {info['menace']}\n"
                f"• *Impact potentiel :* {info['impact']}\n\n"
                f"*Actions recommandées :*\n"
                f"{action_personnalisee}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )

            envoyer_slack(texte_slack)

            # Trace locale pour verification
            with open("/var/log/snort/slack_notifications.log", "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] Alerte Slack envoyee pour SID {sid} ({src_ip} -> {dst_ip})\n")

        except Exception as e:
            with open("/var/log/snort/slack_error.log", "a", encoding="utf-8") as err:
                err.write(f"Erreur script Slack : {e}\n")

if __name__ == "__main__":
    main()
