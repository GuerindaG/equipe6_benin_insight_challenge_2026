# equipe6_benin_insight_challenge_2026
Analyse des événements et tendances médiatiques au Bénin (2025-2026) via la base de données mondiale GDELT. Projet réalisé dans le cadre du Hackathon iSHEERO x DataCamp 2026.

## Structure du dépôt



## Extraction des données

Requête SQL utilisée sur BigQuery pour extraire les événements liés au Bénin en 2025 :

```sql
SELECT *
FROM `gdelt-bq.gdeltv2.events`
WHERE SQLDATE BETWEEN 20250101 AND 20251231
AND (
    ActionGeo_CountryCode = 'BN'
    OR Actor1CountryCode = 'BJ'
    OR Actor2CountryCode = 'BJ'
)
```

**info :**

Dans GDELT, le Bénin est identifié par deux codes principaux  :

- FIPS Country Code : BN (Utilisé pour la géolocalisation des événements).

- ISO Country Code : BJ (Utilisé pour identifier les acteurs béninois).

#

## Installation et lancement

1-Cloner le projet
2-Installer les bibliothèques via :  pip install -r requirements.txt
3-Executer la commande suivante : python main.py
