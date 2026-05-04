# equipe6_benin_insight_challenge_2026
Analyse des événements et tendances médiatiques au Bénin (2025-2026) via la base de données mondiale GDELT. Projet réalisé dans le cadre du Hackathon iSHEERO x DataCamp 2026.

## Installation et lancement

1- Créer un projet sur Google Cloud (console.cloud.google.com)
2- Activer l'API BigQuery sur votre projet
3- Créer un Service Account avec le rôle "Utilisateur BigQuery"
4- Télécharger la clé JSON et la renommer key.json
5- Cloner le projet 
6- Installer les bibliothèques : pip install -r requirements.txt
7- Créer un fichier .env à la racine du projet :
        GCP_PROJECT_ID=votre-project-id
        GOOGLE_APPLICATION_CREDENTIALS=./key.json
8- Placer le fichier key.json à la racine du projet
9- Exécuter : python main.py
## Extraction des données

Requête SQL utilisée sur BigQuery pour extraire les événements liés au Bénin en 2025 :

```sql
SELECT
    *
FROM
    `gdelt-bq.gdeltv2.events`
WHERE
    ActionGeo_CountryCode = 'BN'
    AND SQLDATE BETWEEN 20250101 AND 20251231
```

#
