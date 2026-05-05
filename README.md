# Bénin Insights Challenge 2026  
## Hackathon iSHEERO x DataCamp Donates

## Présentation du projet

Dans le cadre du Hackathon **iSHEERO x DataCamp 2026**, notre équipe a développé une solution d’analyse de données basée sur **GDELT** afin de transformer des données médiatiques mondiales en insights stratégiques sur le Bénin.

Notre projet explore la manière dont le Bénin est représenté dans les médias internationaux au cours des **12 derniers mois**, avec un focus sur :

- l’attractivité du pays ;
- les relations diplomatiques et géopolitiques ;
- la perception médiatique internationale ;
- les signaux de vigilance informationnelle et stratégique.

L’objectif est de produire des analyses utiles pour :
- journalistes,
- chercheurs,
- décideurs publics,
- analystes OSINT.

---

## Problématique

Comment exploiter les données GDELT pour :

1. identifier les principaux sujets associés au Bénin ;
2. analyser l’évolution de la couverture médiatique ;
3. mesurer la tonalité des publications ;
4. détecter des pics d’attention médiatique ;
5. cartographier les relations du Bénin avec les autres pays.

---

## Approche méthodologique

Notre workflow s’est articulé en 4 étapes principales.

### 1. Extraction des données

Source : **GDELT BigQuery**

Nous avons interrogé les événements liés au Bénin via Google BigQuery.

Filtre principal :

```sql
SELECT *
FROM `gdelt-bq.gdeltv2.events`
WHERE ActionGeo_CountryCode = 'BC'
AND YEAR >= 2025
LIMIT 10000
```

Objectif :
- limiter le coût BigQuery ;
- récupérer les événements sur une période fixe (janvier 2025 - Décembre 2025) .

---

### 2. Pipeline de traitement

Le pipeline de preprocessing comprend :

- nettoyage des colonnes inutiles ;
- gestion des valeurs manquantes ;
- standardisation des dates ;
- filtrage thématique via regex ;
- export des datasets nettoyés.

Scripts : `pipeline/`

---

### 3. Analyse exploratoire

Notebook principal : `notebooks/`

Analyses réalisées :

- distribution des événements ;
- évolution temporelle ;
- analyse de sentiment via `AvgTone` ;
- top pays mentionnant le Bénin ;
- top acteurs internationaux ;
- détection de pics médiatiques.

Visualisations :
- séries temporelles ;
- histogrammes ;
- heatmaps ;
- bar charts ;
- nuages de mots.

---

### 4. Dashboard interactif

Dashboard développé avec **Streamlit**.

Fonctionnalités :

- filtres temporels ;
- exploration des événements ;
- visualisation des tendances ;
- navigation simplifiée pour utilisateurs non techniques.

Lancement :

```bash
streamlit run dashboard/dashboard_benin.py
```

---

## Axes analytiques retenus

### Axe 1 — Attractivité nationale

Inspiré de :
- [Open Data France](https://data.education.gouv.fr/pages/dataviz-list/)

Analyse :
- digitalisation ;
- économie ;
- tourisme ;
- innovation ;
- perception internationale.

---

### Axe 2 — Vigilance Cyber 

Inspiré de :
- [World Monitor](https://www.worldmonitor.app/?lat=20.0000&lon=0.0000&zoom=1.00&view=global&timeRange=7d&layers=conflicts%2Cbases%2Chotspots%2Cnuclear%2Csanctions%2Cweather%2Ceconomic%2Cwaterways%2Coutages%2Cmilitary%2Cnatural%2CiranAttacks) :
- méthodologies de veille stratégique

Analyse :
- signaux faibles ;
- désinformation ;
- instabilité régionale ;
- perception diplomatique.

---

## Utilisation de l’intelligence artificielle

Conformément au règlement du challenge, nous déclarons l’usage d’IA dans le projet.

Outil principal :
- **Google Gemini**

Utilisations :

### Documentation
Gemini nous a aidés à :

- structurer et améliorer le README ;
- clarifier la documentation technique ;
- organiser les livrables.

### Qualité du code
Gemini a servi pour :

- commenter certaines sections de code ;
- améliorer la lisibilité des scripts ;
- proposer des optimisations sur certaines fonctions.

### Notebook
Gemini a été utilisé pour :

- améliorer les explications markdown ;
- renforcer la narration analytique ;
- corriger certaines visualisations.

### Storytelling
Gemini a assisté dans :

- la structuration du pitch ;
- la reformulation des insights ;
- l’amélioration du langage non technique.

**Important :**
Toutes les décisions analytiques, validations métier et interprétations finales ont été réalisées par l’équipe.

---

## Structure du dépôt

```bash
.
├── dashboard/          # Application Streamlit
├── data/
│   ├── raw/            # Données brutes
│   └── processed/      # Données nettoyées
├── docs/               # Documentation complémentaire
├── models/             # Scripts ML / sentiment
│   └── outputs/
├── notebooks/          # Analyse exploratoire
├── pipeline/           # Scripts ETL / preprocessing
├── main.py
├── requirements.txt
└── README.md
```

---

## Installation

Cloner le projet :

```bash
git clone <repo_url>
cd project
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

---

## Reproduction du projet

### Exécuter le pipeline

```bash
python main.py
```

### Ouvrir le notebook

Lancer les notebooks dans :

```bash
notebooks/
```

### Lancer le dashboard

```bash
streamlit run dashboard/app.py
```

---

## Sources d’inspiration

Données :
- GDELT Project
- Google BigQuery

Technologies :
- Pandas
- Plotly
- Streamlit
- Scikit-learn

---

## Livrables

Conformément aux exigences du challenge :

- dépôt GitHub public
- notebook reproductible
- dashboard interactif
- vidéo pitch
- résumé exécutif

---

## Équipe

**Groupe 04 – Équipe 6**

- **Data Engineer** : pipeline et extraction
- **Data Analyst** : dashboard et visualisation
- **ML Engineer** : analyse de sentiment / modèles
- **Data Scientist** : cadrage analytique, insights et pitch

---

## Notes

- Projet développé dans le cadre du hackathon uniquement.
- Données issues de GDELT.
- Usage d’IA déclaré conformément au règlement.
