# Guide de démarrage : Dashboard Bénin Insight Challenge

## Prérequis

Python 3.9 ou plus récent.

## Installation des dépendances

Ouvrez un terminal et exécutez :

```bash
pip install streamlit pandas plotly numpy
```

## Lancement du dashboard

```bash
streamlit run dashboard_benin.py
```

Une fenêtre s'ouvrira automatiquement dans votre navigateur à l'adresse :
http://localhost:8501

---

## Structure du dashboard

Le dashboard est organisé en 5 galeries accessibles depuis la barre latérale :

1. **Vue d'ensemble** : KPIs globaux, évolution temporelle, répartition des thèmes, sentiment, acteurs clés
2. **Rayonnement Digital & Innovation** : Indice de Confiance Tech, évolution des articles Tech, Top articles relayés
3. **Emergence Touristique** : Baromètre d'attractivité, carte interactive, part de voix Culture vs Nature
4. **Diplomatie Active** : Diagramme de Sankey, répartition linguistique des sources, interactions par pays
5. **Cyber-Vigilance & Désinformation** : Détection de pics anormaux, GoldsteinScale, analyse des sources

Un filtre de période (dates) est disponible dans la barre latérale pour toutes les galeries.

---

## Source des données

GDELT Project : https://www.gdeltproject.org/
Données extraites via BigQuery pour le Bénin (janvier 2025- Décembre 2025).
