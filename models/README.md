# Analyse de sentiment - Modèle Deep Learning

Ce dossier contient le modèle d'analyse de sentiment pour les événements médiatiques au Bénin (2025-2026).

## Modèle : `sentiment_dl.py`

### Principe
Le modèle utilise **BERT multilingue** (`nlptown/bert-base-multilingual-uncased-sentiment`) pour analyser le sentiment des articles de presse liés aux événements GDELT.

### Pipeline
1. **Scraping** : Extraction du contenu textuel des articles via les URLs (`SOURCEURL`) du dataset GDELT
2. **Classification** : Attribution d'une note de 1 à 5 étoiles par le modèle BERT
3. **Mapping** : Conversion en 3 classes :
   - **Positif** (4-5 étoiles, score pondéré ≥ 3.5)
   - **Neutre** (3 étoiles, score entre 2.5 et 3.5)
   - **Négatif** (1-2 étoiles, score ≤ 2.5)

### Sorties générées (dans `outputs/`)
- **`sentiment_dl.csv`** : Résultats agrégés journaliers (sentiment moyen, proportions, nombre d'événements)
- **`sentiment_dl_histogram.png`** : Répartition globale des sentiments
- **`sentiment_dl_timeseries.png`** : Évolution temporelle du sentiment au fil du temps
- **`scraped_articles.csv`** : Cache des articles déjà scrapés pour éviter les requêtes redondantes

### Utilisation
```bash
python models/sentiment_dl.py
```

Le script lit les données nettoyées dans `data/processed/benin_cleaned_data.csv` et produit les visualisations dans `models/outputs/`.
