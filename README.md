# 🇧🇯 GDELT Benin Data Pipeline

## Objectif

Ce pipeline permet de récupérer, nettoyer et structurer les données GDELT liées au Bénin afin de produire un dataset exploitable pour l’analyse, le dashboard et le machine learning.

---

## Fonctionnement du pipeline

Le pipeline exécute 3 étapes principales :

### 1. Extraction

Téléchargement des données GDELT sur une période définie (en jours).

### 2. Nettoyage

* Suppression des données invalides
* Harmonisation des colonnes
* Filtrage géographique et/ou acteur (selon configuration)

### 3. Feature Engineering

* Création de variables analytiques (tendances, indicateurs, agrégations)
* Préparation des données pour analyse et modélisation

---

## Lancement du pipeline

```bash
python main.py
```

ou avec période personnalisée :

```python
run_pipeline(days=365)
```

---

## Outputs générés

Le pipeline produit deux datasets :

* `data/processed/benin_cleaned_data.csv`
  → données nettoyées

* `data/processed/benin_trends.csv`
  → données enrichies pour analyse & dashboard

---

## Logique de filtrage (important)

Selon les objectifs business, le filtrage peut inclure :

### Option 1 : Strict (localisation uniquement)

```text
ActionGeo_CountryCode == 'BN'
```

- événements se déroulant uniquement au Bénin

---

### Option 2 — Étendu (recommandé pour votre projet)

```text
ActionGeo_CountryCode == 'BN'
OR Actor1CountryCode == 'BJ'
OR Actor2CountryCode == 'BJ'
```

 inclut :

* événements au Bénin
* acteurs béninois à l’international
* relations internationales

---

## Période d’analyse

La période est dynamique :

```python
run_pipeline(days=N)
```

Exemples :

* `days=30` → 1 mois
* `days=90` → 3 mois
* `days=365` → 12 mois

---

## Remarque 

Le dataset final dépend directement du choix de filtrage dans `clean_data()` :

* il doit être aligné avec les questions business
* tous les membres doivent utiliser le même dataset de référence
