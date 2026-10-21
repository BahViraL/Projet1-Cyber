# Conclusion et analyse

L'objectif de ce projet était donc de construire un environnement supervisant la sécurité informatique contre des actes malveillants.

En partant d'une architecture simple, un serveur vulnérable scanné par des outils de détection pris d'attaque, nous avons mis en place des scénarios plosibles en situation réelle pour en analyser les effets sur le système. 

## Objectif des scénarios 

Les scénarios ont pour objectif de montrer que notre système permet bien de reconnaître des vecteurs d'attaques de détecter des intrusions et des exploitation critiques. 

# Résultats des scénarios 

## Reconnaissance — scan de ports (nmap)

Ce scénario s'intéressait au scan de paquets SYN avec Nmap permettant de reconnaître les ports et les services accessibles. Par la suite Snort avait pour objectif de protéger le système d'attaques DDOS en déclenchant sa défense s'il détecte plus de 20 paquets SYN en 5 secondes. 

Malgré le fait de son bon fonctionnement dans le cas précis la limite que nous avons constaté est le fait qu'il soit lent et qu'il ne permet pas une défense concluante dans le cas d'une distribution entre plusieurs sources dans un délai plus long que cinq secondes.

## Force brute — authentification SSH (hydra)

Dans ce scénario, Hydra tente des connexions SSH. Le système surveille quant à lui les ouvertures de connexion TCP sur le port 22 avec un seuil de trois connexions en 30 secondes.

En limite, nous pouvons relevé le fait que Snort n'observe pas les échecs d'authentification. Une analyse des journeaux pourrait permettre un renforcement de la sécurité du système.

## Injection SQL (DVWA)

Dans ce cas, une requête HTTP GET est dirigée vers DVWA. le système cherche un motif de requête afin de signaler une tentative d'injection SQL.

L'amélioration pourrait ici être portée sur le fait de pouvoir repérer des signatures avec d'autres formes de requêtes. De plus, l'analyse du système peut aboutir à la production de faux positifs.

## Traversée de répertoire — lecture de /etc/passwd (DVWA)

Avec ce vecteur d'attaque on attend de Snort d'être en capacité de détecter les requêtes tentant d'accéder à /etc/passwd par reconnaissance des chaînes. 

Dans son état actuel, notre règle ne permet pas de détecter beaucoup de variantes d'encodage ou de chemins alternatifs.

## Exécution de commande à distance — RCE (DVWA)

Dans ce dernier scénario, une requête HTTP POST vise le formulaire d'éxecution de commande de DVWA. Le système a pour règle de détecter un paramètre IP et un motif encodé associé à un séparateur de commande. 

Pour aller plus loin nous pourrions travailler sur la capacité de notre détection à prouver qu'une commande a été exécutée et/ou qu'on a une compromission du serveur. 

# Conclusion générale sur le système

Malgré des points d'améliorations possibles constatés avec les différents scénarios, le système possède déjà une chaîne de détection compréhensible et modulable grâce à l'utilisation de Snort pour les alertes, de syslog-ng qui les collectent et les structurent ainsi que de Elasticsearch et Kibana permettant une indexation claire et leur consultation.

Ce projet nous a donc permis de mettre en place et d'analyer les éléments d'une chaîne de supervision de sécurité sur plusieurs domaines essentiels à la sécurité informatique. 