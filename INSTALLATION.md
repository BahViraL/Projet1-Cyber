# Installation de l'environnement

## 1. Architecture générale

Deux machines sur un réseau privé isolé :

    Kali (attaquant, hôte)          192.168.56.1
    VM "defenseur" (Ubuntu Server)  192.168.56.102

La VM défenseur a deux cartes réseau :
- Adaptateur 1 : NAT (accès Internet pour les mises à jour et installations)
- Adaptateur 2 : réseau privé hôte VirtualBox (vboxnet0), interface enp0s8
  côté VM. C'est ce réseau que Snort surveille, pour ne détecter que le
  trafic d'attaque et non le bruit d'Internet.

## 2. Machine virtuelle

- Logiciel : VirtualBox, installé sur Kali (hôte, dual boot avec Windows)
- Système : Ubuntu Server 24.04 LTS (image live-server)
- Ressources allouées : 2 CPU, 4623 Mo de RAM (maximum disponible sur la
  machine hôte), 25 Go de disque dynamique
- Nom de machine : defenseur
- OpenSSH server installé dès l'installation du système


## 3. Mémoire et swap

La VM dispose de 4,3 Go de RAM, ce qui est juste pour faire tourner Snort,
syslog-ng, Elasticsearch, Kibana et une application web cible en même
temps. Deux mesures ont été prises :

- La mémoire d'Elasticsearch a été limitée à 1 Go (voir CONFIGURATION.md)
- 2 Go de swap ont été ajoutés comme filet de sécurité :

      sudo fallocate -l 2G /swapfile
      sudo chmod 600 /swapfile
      sudo mkswap /swapfile
      sudo swapon /swapfile
      echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

## 4. Mise à jour du système

    sudo apt update && sudo apt upgrade -y

## 5. Installation de Snort (IDS) et syslog-ng (collecte de logs)

    sudo apt install -y snort syslog-ng

Pendant l'installation de Snort, deux choix ont été faits :
- Interface à surveiller : enp0s8 (le réseau privé uniquement)
- Plage d'adresses locales (HOME_NET) : 192.168.56.0/24

Vérification de la version installée et de la configuration :

    snort -V
    sudo snort -T -c /etc/snort/snort.conf -i enp0s8

La sortie doit se terminer par "Snort successfully validated the
configuration!".

## 6. Installation d'Elasticsearch et de Kibana

Ajout du dépôt officiel Elastic (branche 8.x, choisie pour sa stabilité et
sa compatibilité avec la documentation disponible) :

    sudo apt install -y curl gpg ca-certificates apt-transport-https
    curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
    sudo apt update

Installation d'Elasticsearch :

    sudo apt install -y elasticsearch

Limitation de la mémoire à 1 Go :

    echo -e "-Xms1g\n-Xmx1g" | sudo tee /etc/elasticsearch/jvm.options.d/heap.options

Démarrage :

    sudo systemctl daemon-reload
    sudo systemctl enable --now elasticsearch

Installation de Kibana :

    sudo apt install -y kibana
    echo "--max-old-space-size=1024" | sudo tee -a /etc/kibana/node.options

Connexion de Kibana à Elasticsearch, via un jeton d'enrôlement généré côté
Elasticsearch :

    sudo /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana
    sudo /usr/share/kibana/bin/kibana-setup --enrollment-token <jeton>

Kibana est configuré pour n'écouter que sur l'IP du réseau privé, afin de
ne pas être exposé sur la carte NAT :

    sudo sed -i 's|^#server.host:.*|server.host: "192.168.56.102"|' /etc/kibana/kibana.yml
    sudo systemctl daemon-reload
    sudo systemctl enable --now kibana

Kibana est accessible depuis le navigateur à l'adresse :
http://192.168.56.102:5601

## 7. Installation de la cible web vulnérable (DVWA)

Pour démontrer les scénarios d'attaque applicative (injection SQL,
traversée de répertoire, exécution de commande), une application web
volontairement vulnérable est installée sur la même VM :

    sudo apt install -y apache2 php php-mysqli php-gd libapache2-mod-php mariadb-server
    sudo systemctl enable --now apache2 mariadb
    cd /var/www/html
    sudo rm -f index.html
    sudo git clone https://github.com/digininja/DVWA.git .
    sudo chown -R www-data:www-data /var/www/html
    sudo mysql -e "CREATE DATABASE dvwa; CREATE USER 'dvwa'@'localhost' IDENTIFIED BY 'dvwa_password_labo'; GRANT ALL ON dvwa.* TO 'dvwa'@'localhost'; FLUSH PRIVILEGES;"
    sudo cp /var/www/html/config/config.inc.php.dist /var/www/html/config/config.inc.php
    sudo sed -i "s/'p@ssw0rd'/'dvwa_password_labo'/" /var/www/html/config/config.inc.php

Initialisation via le navigateur : http://192.168.56.102/setup.php, puis
clic sur "Create / Reset Database". Connexion par défaut : admin / password.
Le niveau de sécurité de DVWA est réglé sur "Low" dans le menu
"DVWA Security", pour permettre une démonstration claire des vulnérabilités.

## 8. Vérifications finales

    systemctl is-enabled snort syslog-ng elasticsearch kibana apache2 mariadb

Les six services doivent répondre "enabled", ce qui garantit que
l'ensemble de la chaîne redémarre automatiquement avec la VM.
