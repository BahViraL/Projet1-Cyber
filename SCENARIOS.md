# Scénarios d'Attaque et Détection (IDS/IPS)

Ce document détaille les 5 scénarios d'intrusion mis en place sur notre infrastructure (ciblant la machine hébergeant DVWA), la justification de ces choix, et la manière dont notre sonde Snort les détecte.

---

## Scénario 1 – Reconnaissance : Scan de ports furtif (Nmap SYN)

### Justification du choix
La phase de reconnaissance est la première étape de la "Cyber Kill Chain". Un scan SYN (Half-Open) est utilisé par les attaquants car il est plus discret qu'un scan TCP complet. Il est indispensable pour un SOC de repérer cette phase avant que l'attaque réelle ne commence.

### Menace représentée
L'attaquant cartographie la surface d'attaque (ports ouverts, services actifs) pour identifier les vulnérabilités exploitables.

### Règle Snort implémentée
```text
alert tcp any any -> $HOME_NET any (msg:"LAB Scan de ports TCP SYN detecte"; flags\:S; detection_filter\:track by_src, count 20, seconds 5; classtype\:network-scan; priority:3; sid:1000002; rev:2;)
```

### Exemple de log (Alerte Snort)
`[**] [1:1000002:2] LAB Scan de ports TCP SYN detecte [**] [Classification: Attempted Information Leak] [Priority: 3] {TCP} 192.168.56.101:45322 -> 192.168.56.10:80`

---

## Scénario 2 – Intrusion : Attaque par Force Brute (SSH)

### Justification du choix
Le port 22 (SSH) est une cible privilégiée. L'utilisation d'outils automatisés (comme Hydra) avec des dictionnaires de mots de passe courants (RockYou) reste l'une des méthodes de compromission les plus fréquentes sur les serveurs exposés.

### Menace représentée
Une élévation de privilèges non autorisée. Si l'attaque réussit, l'attaquant obtient un accès terminal direct au serveur avec les droits de l'utilisateur compromis.

### Règle Snort implémentée
```text
alert tcp any any -> $HOME_NET 22 (msg:"LAB SSH brute force detecte"; flags\:S; detection_filter\:track by_src, count 3, seconds 30; classtype\:attempted-admin; priority:2; sid:1000003; rev:2;)
```

### Exemple de log (Alerte Snort)
`[**] [1:1000003:2] LAB SSH brute force detecte [**] [Classification: Attempted Administrator Privilege Gain] [Priority: 2] {TCP} 192.168.56.101:51204 -> 192.168.56.10:22`

---

## Scénario 3 – Web : Injection SQL (SQLi)

### Justification du choix
Classée en permanence dans le Top 10 OWASP, l'injection SQL cible le cœur de l'application web. C'est une attaque applicative critique qui échappe aux pare-feux réseaux classiques (L3/L4) et nécessite une inspection de payload (L7) par l'IDS.

### Menace représentée
Exfiltration de données sensibles (vol de mots de passe, données clients), modification de la base de données, ou contournement des portails d'authentification.

### Règle Snort implémentée
```text
alert tcp any any -> $HOME_NET 80 (msg:"LAB Injection SQL detectee"; content:"GET "; depth:4; content:"id="; distance:0; content:"%27"; distance:0; within:40; nocase; classtype\:web-application-attack; priority:1; sid:1000004; rev:2;)
```

### Exemple de log (Alerte Snort)
`[**] [1:1000004:2] LAB Injection SQL detectee [**] [Classification: Web Application Attack] [Priority: 1] {TCP} 192.168.56.101:48112 -> 192.168.56.10:80`

---

## Scénario 4 – Web : Path Traversal (Lecture de /etc/passwd)

### Justification du choix
L'inclusion de fichier local (LFI) et la traversée de répertoire exploitent une mauvaise validation des entrées utilisateurs. C'est une technique de post-exploitation web classique pour énumérer le système sous-jacent.

### Menace représentée
La lecture du fichier `/etc/passwd` permet à l'attaquant de lister les comptes utilisateurs de la machine Linux, préparant le terrain pour des attaques de force brute ciblées ou des escalades de privilèges.

### Règle Snort implémentée
```text
alert tcp any any -> $HOME_NET 80 (msg:"LAB Traversee de repertoire etc-passwd detectee"; content:"GET "; depth:4; content:"etc"; distance:0; nocase; content:"passwd"; distance:0; nocase; classtype\:web-application-attack; priority:2; sid:1000005; rev:2;)
```

### Exemple de log (Alerte Snort)
`[**] [1:1000005:2] LAB Traversee de repertoire etc-passwd detectee [**] [Classification: Web Application Attack] [Priority: 2] {TCP} 192.168.56.101:48115 -> 192.168.56.10:80`

---

## Scénario 5 – Web : Exécution de Commande à Distance (RCE)

### Justification du choix
La RCE est la vulnérabilité web la plus critique. Elle survient lorsqu'une application exécute une entrée utilisateur directement dans un shell système. Nous ciblons ici une méthode HTTP `POST`, typique des soumissions de formulaires masquant les payloads.

### Menace représentée
Compromission totale du système. L'attaquant peut déployer un reverse shell, installer des malwares (ex: botnets, mineurs de cryptomonnaie) ou pivoter vers d'autres machines du réseau interne.

### Règle Snort implémentée
```text
alert tcp any any -> $HOME_NET 80 (msg:"LAB Execution de commande a distance detectee"; content:"POST "; depth:5; content:"ip="; distance:0; content:"%3"; within:40; classtype\:web-application-attack; priority:1; sid:1000006; rev:2;)
```

### Exemple de log (Alerte Snort)
`[**] [1:1000006:2] LAB Execution de commande a distance detectee [**] [Classification: Web Application Attack] [Priority: 1] {TCP} 192.168.56.101:49220 -> 192.168.56.10:80`
