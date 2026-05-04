# Bénin Vision Dashboard

Observatoire de l’Attractivité et de Vigilance Cyber 

## Lancement rapide

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

## Structure du projet

```text
project_root/
├── dashboard/
│   ├── app.py
│   ├── README.md
│   └── .streamlit/
│       └── config.toml
├── data/
│   └── processed/
│       └── benin_trends.csv
├── notebooks/
├── models/
└── requirements.txt
```

## Visualisations prévues

| # | Visualisation                      | Objectif                                                |
| - | ---------------------------------- | ------------------------------------------------------- |
| 1 | Série temporelle volume + tonalité | Identifier pics médiatiques et variations de perception |
| 2 | Carte géographique des événements  | Localiser hotspots et concentration des événements      |
| 3 | Répartition thématique             | Identifier thèmes dominants                             |
| 4 | Distribution AvgTone               | Observer perception globale                             |
| 5 | Réseau d’acteurs / relations       | Identifier acteurs les plus mentionnés                  |
| 6 | Indice composite                   | Synthèse d’attractivité / risque                        |

## Données

Phase 1 :

* utilisation de données simulées intégrées dans `dashboard/app.py`

Phase 2 :

* remplacement par lecture du dataset final :
  `data/processed/benin_trends.csv`

## Branche de développement

feature/data_analyst
