# Système de détection d'anomalies et de gestion de logs

Projet réalisé dans le cadre du cours de cybersécurité. Chaîne complète de
détection d'intrusion et de visualisation des alertes, construite sur une
VM Ubuntu Server dédiée.

## Architecture

    Kali (attaquant) --> réseau privé --> VM défenseur
                                            |-- Snort (détection réseau)
                                            |-- syslog-ng (collecte et parsing)
                                            |-- Elasticsearch (stockage/index)
                                            |-- Kibana (visualisation)
                                            `-- DVWA (application cible vulnérable)

## Scénarios d'intrusion couverts

1. Reconnaissance — scan de ports (nmap)
2. Force brute — authentification SSH (hydra)
3. Injection SQL (DVWA)
4. Traversée de répertoire — lecture de /etc/passwd (DVWA)
5. Exécution de commande à distance — RCE (DVWA)

## Structure du dépôt

- INSTALLATION.md — mise en place de l'environnement, pas à pas
- CONFIGURATION.md — configuration de Snort, syslog-ng, Elasticsearch, Kibana
- GUIDE_UTILISATION.md — comment relancer et tester les scénarios
- SCENARIOS.md — description et justification de chaque scénario
- ANALYSE_ET_CONCLUSION.md — limites, difficultés rencontrées, perspectives
- snort/ — règles locales et seuils d'alerte
- syslog-ng/ — configuration de collecte et d'envoi vers Elasticsearch
- elasticsearch/ — rôle, utilisateur, modèle d'index
- screenshots/ — captures justificatives
- point_bonus/ — améliorations additionnelles

