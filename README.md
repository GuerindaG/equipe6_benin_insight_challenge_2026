# equipe6_benin_insight_challenge_2026
Analyse des événements et tendances médiatiques au Bénin (2025-2026) via la base de données mondiale GDELT. Projet réalisé dans le cadre du Hackathon iSHEERO x DataCamp 2026.

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
