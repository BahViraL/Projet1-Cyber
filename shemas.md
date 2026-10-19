```mermaid
graph TD
  A[Machine Kali Linux] -->|Attaques| B[Serveur Web DVWA]
  B -->|Trafic reseau| C[Snort IDS]
  C -->|Alertes| D[syslog-ng]
  D -->|Logs JSON| E[Elasticsearch]
  E -->|Visualisation| F[Kibana]
  C -->|Notifications| G[Slack via Python]
