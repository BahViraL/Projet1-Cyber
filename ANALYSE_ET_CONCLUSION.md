# Conclusion et analyse

L'objectif de ce projet était de construire un environnement supervisant la sécurité informatique contre des actes malveillants. En partant d'une architecture simple (un serveur vulnérable scanné par des outils de détection pris d'attaque), nous avons mis en place des scénarios plausibles en situation réelle pour en analyser les effets sur le système.

## Objectif des scénarios

Les scénarios ont pour objectif de montrer que notre système permet bien de reconnaître des vecteurs d'attaques, de détecter des intrusions et des exploitations critiques.

## Résultats des scénarios et limites identifiées

### Reconnaissance — scan de ports (nmap)
Ce scénario s'intéressait au scan de paquets SYN avec Nmap permettant de reconnaître les ports et les services accessibles. Par la suite, Snort avait pour objectif de protéger le système d'attaques DDoS en déclenchant l'alerte s'il détecte plus de 20 paquets SYN en 5 secondes.
* **Limite :** Malgré son bon fonctionnement dans ce cas précis, la limite que nous avons constatée est sa lenteur. Le système ne permet pas une détection concluante dans le cas d'une attaque distribuée entre plusieurs sources sur un délai plus long que cinq secondes.

### Force brute — authentification SSH (hydra)
Dans ce scénario, Hydra tente des connexions SSH. Le système surveille quant à lui les ouvertures de connexion TCP sur le port 22 avec un seuil de trois connexions en 30 secondes.
* **Limite :** Nous pouvons relever le fait que Snort n'observe pas les échecs d'authentification. Une analyse croisée des journaux systèmes permettrait un renforcement de la sécurité du système.

### Injection SQL (DVWA)
Dans ce cas, une requête HTTP GET est dirigée vers DVWA. Le système cherche un motif de requête afin de signaler une tentative d'injection SQL.
* **Limite :** L'amélioration pourrait ici être portée sur la capacité à repérer des signatures avec d'autres formes de requêtes (variantes d'encodage). De plus, l'analyse statique du système peut aboutir à la production de faux positifs.

### Traversée de répertoire — lecture de /etc/passwd (DVWA)
Avec ce vecteur d'attaque, on attend de Snort d'être en capacité de détecter les requêtes tentant d'accéder à `/etc/passwd` par reconnaissance des chaînes.
* **Limite :** Dans son état actuel, notre règle ne permet pas de détecter beaucoup de variantes d'encodage ou de chemins alternatifs complexes.

### Exécution de commande à distance — RCE (DVWA)
Dans ce dernier scénario, une requête HTTP POST vise le formulaire d'exécution de commande de DVWA. Le système a pour règle de détecter un paramètre IP et un motif encodé associé à un séparateur de commande.
* **Limite :** Pour aller plus loin, nous pourrions travailler sur la capacité de notre détection à prouver qu'une commande a été effectivement exécutée et/ou qu'il y a une compromission réelle du serveur (par exemple en surveillant le trafic sortant).

## Limites globales de l'architecture

Au-delà des règles spécifiques, notre infrastructure présente des limites inhérentes à sa conception :

* **Mode passif (IDS) vs bloquant (IPS) :** Snort fonctionne ici en écoute réseau. Il détecte l'attaque et alerte l'administrateur en temps réel sur Slack, mais il ne bloque pas le paquet malveillant à la volée pour protéger la cible.
* **Aveuglement face au trafic chiffré (HTTPS) :** Nos règles applicatives inspectent le contenu des requêtes en clair sur le port 80. En environnement de production, le trafic web est chiffré en HTTPS (port 443). Sans mécanisme de déchiffrement en amont, Snort ne pourrait pas inspecter la charge utile.

## Améliorations et Perspectives (Veille technologique)

Pour faire évoluer ce projet vers une architecture SOC (Security Operations Center) industrielle, plusieurs axes d'amélioration se dégagent :

1. **Évolution vers Suricata ou couplage NIDS + HIDS (Wazuh) :** Passer à Suricata permettrait de bénéficier de l'analyse native des protocoles applicatifs (TLS, HTTP). L'ajout d'un agent HIDS comme Wazuh sur le serveur cible permettrait de corréler nos alertes réseau Snort avec les événements internes du système (modifications de fichiers, logs d'authentification).
2. **Passage en mode IPS et réponse active :** Coupler notre script Python de notification à des outils de pare-feu ou utiliser Snort en mode *inline* permettrait de bannir dynamiquement l'adresse IP attaquante dès la première alerte critique confirmée.

## Conclusion générale sur le système

Malgré des points d'améliorations possibles constatés avec les différents scénarios, le système possède déjà une chaîne de détection compréhensible et modulable grâce à l'utilisation de Snort pour les alertes, de `syslog-ng` qui les collecte et les structure, ainsi que de Elasticsearch et Kibana permettant une indexation claire et leur consultation.

Ce projet nous a donc permis de mettre en place et d'analyser les éléments d'une chaîne de supervision de sécurité sur plusieurs domaines essentiels à la sécurité informatique.
