# Configuration des outils

## 1. Snort — règles locales

Toutes les règles personnalisées sont dans `snort/local.rules`. Chacune suit le même principe : repérer un comportement ou un motif associé à une attaque, tout en évitant de se déclencher sur un usage normal. Les règles sont hiérarchisées selon 3 niveaux de priorité (1 pour critique, 2 pour moyen, 3 pour faible).

### Règle de test initiale (sid 1000001)

    alert icmp any any -> $HOME_NET any (msg:"LAB ICMP echo request detecte"; itype:8; classtype:attempted-recon; priority:3; sid:1000001; rev:2;)

Détecte un simple ping. Cette règle a servi à valider que toute la chaîne (Snort -> syslog-ng -> Elasticsearch -> Kibana) fonctionnait avant de passer aux scénarios réels.

### Scénario 1 — scan de ports (sid 1000002)

    alert tcp any any -> $HOME_NET any (msg:"LAB Scan de ports TCP SYN detecte"; flags:S; detection_filter:track by_src, count 20, seconds 5; classtype:network-scan; priority:3; sid:1000002; rev:2;)

- `flags:S` : ne retient que les paquets SYN purs (début de connexion).
- `detection_filter count 20, seconds 5` : se déclenche seulement après 20 tentatives de connexion depuis la même source en 5 secondes, pour ne pas confondre un usage normal avec un scan.
- Un filtre d'événement associé (`threshold.conf`) limite ensuite à une alerte toutes les 10 secondes par source, pour éviter d'inonder l'index d'alertes identiques pendant un scan de plusieurs centaines de ports.

### Scénario 2 — force brute SSH (sid 1000003)

    alert tcp any any -> $HOME_NET 22 (msg:"LAB SSH brute force detecte"; flags:S; detection_filter:track by_src, count 3, seconds 30; classtype:attempted-admin; priority:2; sid:1000003; rev:2;)

Le seuil a été mesuré avec `tcpdump` : un outil de force brute avec 4 connexions en parallèle ouvre en pratique environ 5 connexions quasi simultanées plutôt qu'une par tentative. Le seuil a donc été fixé à 3 pour rester fiable, après un premier essai à 5 qui ne se déclenchait pas de façon certaine.

### Scénario 3 — injection SQL (sid 1000004)

    alert tcp any any -> $HOME_NET 80 (msg:"LAB Injection SQL detectee"; content:"GET "; depth:4; content:"id="; distance:0; content:"%27"; within:40; nocase; classtype:web-application-attack; priority:1; sid:1000004; rev:2;)

Cherche une requête GET contenant le paramètre `id=` suivi, dans une fenêtre de 40 octets, d'une apostrophe encodée (`%27`), signe classique d'une tentative d'injection SQL. La limite `within` évite qu'une apostrophe présente ailleurs dans la requête (en-tête Referer, cookie) ne déclenche une fausse alerte.

### Scénario 4 — traversée de répertoire (sid 1000005)

    alert tcp any any -> $HOME_NET 80 (msg:"LAB Traversee de repertoire etc-passwd detectee"; content:"GET "; depth:4; content:"etc"; distance:0; nocase; content:"passwd"; distance:0; nocase; classtype:web-application-attack; priority:2; sid:1000005; rev:2;)

Cherche la présence de "etc" suivi de "passwd" dans une requête GET, ce qui couvre les variantes d'encodage utilisées pour remonter dans l'arborescence du serveur (`../../../etc/passwd` ou sa version encodée).

### Scénario 5 — exécution de commande à distance (sid 1000006)

    alert tcp any any -> $HOME_NET 80 (msg:"LAB Execution de commande a distance detectee"; content:"POST "; depth:5; content:"ip="; distance:0; content:"%3"; within:40; classtype:web-application-attack; priority:1; sid:1000006; rev:2;)

Contrairement aux scénarios 3 et 4, le formulaire de la page "Command Injection" de DVWA envoie sa requête en POST plutôt qu'en GET. La règle cherche le paramètre `ip=` suivi d'un caractère de séparation de commande encodé (`%3` couvre à la fois `%3B` pour `;` et d'autres variantes commençant par `%3`).

## 2. Seuils d'événements (threshold.conf)

Pour les scénarios 1 et 2, un filtre d'événement limite le nombre d'alertes identiques générées sur une courte période, une fois le seuil de détection franchi :

    event_filter gen_id 1, sig_id 1000002, type limit, track by_src, count 1, seconds 10
    event_filter gen_id 1, sig_id 1000003, type limit, track by_src, count 1, seconds 30

## 3. HOME_NET

Le réseau local surveillé par Snort est fixé explicitement dans `/etc/snort/snort.conf` :

    ipvar HOME_NET 192.168.56.0/24

Cette valeur est reprise par le service via l'option `-S` passée au démarrage (configurée par `/etc/snort/snort.debian.conf`), pour que Snort sache distinguer le réseau à protéger du reste du trafic.

## 4. syslog-ng — collecte et transfert vers Elasticsearch

La configuration complète est dans `syslog-ng/snort.conf`[cite: 7]. Elle comprend trois blocs :

- **source** : lit en continu le fichier d'alertes de Snort (`/var/log/snort/snort.alert.fast`).
- **parser** : découpe chaque ligne d'alerte en champs nommés (`snort.sid`, `snort.msg`, `snort.priority`, `snort.src_ip`, `snort.dst_ip`, etc.) à l'aide d'une expression régulière avec groupes nommés.
- **destination** : envoie chaque alerte, au format JSON, vers Elasticsearch en HTTPS, authentifié avec un compte dédié (voir `elasticsearch/setup.md`).

Point de vigilance rencontré : la première version du template ne créait pas de champ `@timestamp` (elle essayait de copier un champ du même nom qui n'existait pas). Sans horodatage, Kibana n'affichait aucun document. La correction consiste à construire ce champ explicitement à partir de la date de réception par syslog-ng :

    --pair @timestamp=${ISODATE}

## 5. Elasticsearch — sécurité et modèle d'index

Voir `elasticsearch/setup.md` pour le détail des requêtes. Résumé :

- Un rôle dédié (`syslogng_writer`) limite les droits au strict nécessaire : créer et écrire dans les index `snort-*`, rien de plus.
- Un compte dédié (`syslogng`) porte ce rôle, plutôt que d'utiliser le compte administrateur `elastic` dans la configuration de `syslog-ng`.
- Un modèle d'index (`snort`) type correctement les champs IP, les ports et la priorité en entiers, ce qui permet les filtres et les agrégations dans Kibana.

## 6. Kibana — vue de données

Une vue de données a été créée avec le motif d'index `snort-*` et le champ d'horodatage `@timestamp`, permettant d'explorer les alertes dans *Discover* et de construire des visualisations dans *Lens*[cite: 7].
