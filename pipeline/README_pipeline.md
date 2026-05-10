Ce pipeline permet de récupérer, nettoyer et structurer les données GDELT liées au Bénin afin de produire un dataset exploitable pour l’analyse, le dashboard et le machine learning.


## Fonctionnement du pipeline

Le pipeline exécute 3 étapes principales :

### 1. Extraction

Téléchargement des données GDELT sur une période définie .

### 2. Nettoyage

* Suppression des données invalides
* Harmonisation des colonnes
* Filtrage géographique et/ou acteur (selon configuration)

### 3. Feature Engineering

* Création de variables analytiques (tendances, indicateurs, agrégations)
* Préparation des données pour analyse et modélisation

---

## Installation et Lancement du pipeline
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

## Outputs générés

Le pipeline produit deux datasets :

* `data/processed/benin_cleaned_data.csv`
  → données nettoyées

* `data/processed/benin_trends.csv`
  → données enrichies pour analyse & dashboard

---

## Logique de filtrage 
Selon les objectifs business, le filtrage peut inclure :

### Option 1 : Strict (localisation uniquement)

```text
ActionGeo_CountryCode == 'BN'
```

- événements se déroulant uniquement au Bénin

---

### Option 2
```text
ActionGeo_CountryCode == 'BN'
OR Actor1CountryCode == 'BJ'
OR Actor2CountryCode == 'BJ'
```

 inclut :

* événements au Bénin
* acteurs béninois à l’international
* relations internationales


## Remarque 

Le dataset final dépend directement du choix de filtrage dans `clean_data()` :

* il doit être aligné avec les questions business
* tous les membres doivent utiliser le même dataset de référence





