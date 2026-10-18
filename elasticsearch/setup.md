# Configuration Elasticsearch — rôle et utilisateur dédiés à syslog-ng

Exécuté dans Kibana → Management → Dev Tools.

## Rôle (écriture seule sur les index du projet)

    PUT _security/role/syslogng_writer
    {
      "indices": [
        { "names": ["snort-*"], "privileges": ["create_index", "write"] }
      ]
    }

## Utilisateur

    PUT _security/user/syslogng
    {
      "password": "monMDP",
      "roles": ["syslogng_writer"]
    }

## Modèle d'index (typage des champs pour Kibana)

    PUT _index_template/snort
    {
      "index_patterns": ["snort-*"],
      "template": {
        "mappings": {
          "properties": {
            "@timestamp": { "type": "date" },
            "snort": {
              "properties": {
                "src_ip": { "type": "ip" },
                "dst_ip": { "type": "ip" },
                "src_port": { "type": "integer" },
                "dst_port": { "type": "integer" },
                "priority": { "type": "integer" },
                "sid": { "type": "keyword" },
                "msg": { "type": "keyword" },
                "classification": { "type": "keyword" },
                "proto": { "type": "keyword" }
              }
            }
          }
        }
      }
    }

## Justification

Le compte elastic est un super-administrateur. Pour respecter le principe
du moindre privilège, syslog-ng utilise un compte dédié qui ne peut qu'écrire
dans les index snort-*. Si ce mot de passe fuitait (il est stocké en clair
dans la configuration de syslog-ng), l'attaquant n'aurait accès qu'à ces
index, pas au cluster entier.
