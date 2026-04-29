import pandas as pd
from datetime import datetime
from pipeline.extract import download_gdelt_file
from pipeline.transform import clean_data
from pipeline.processing import create_features


# Configuration
COLNAMES = [
    'GlobalEventID', 'Day', 'MonthYear', 'Year', 'FractionDate',
    'Actor1Code', 'Actor1Name', 'Actor1CountryCode', 'Actor1KnownGroupCode', 'Actor1EthnicCode', 'Actor1Religion1Code', 'Actor1Religion2Code', 'Actor1Type1Code', 'Actor1Type2Code', 'Actor1Type3Code',
    'Actor2Code', 'Actor2Name', 'Actor2CountryCode', 'Actor2KnownGroupCode', 'Actor2EthnicCode', 'Actor2Religion1Code', 'Actor2Religion2Code', 'Actor2Type1Code', 'Actor2Type2Code', 'Actor2Type3Code',
    'IsRootEvent', 'EventCode', 'EventBaseCode', 'EventRootCode', 'QuadClass', 'GoldsteinScale', 'NumMentions', 'NumSources', 'NumArticles', 'AvgTone',
    'Actor1Geo_Type', 'Actor1Geo_FullName', 'Actor1Geo_CountryCode', 'Actor1Geo_ADM1Code', 'Actor1Geo_Lat', 'Actor1Geo_Long', 'Actor1Geo_FeatureID',
    'Actor2Geo_Type', 'Actor2Geo_FullName', 'Actor2Geo_CountryCode', 'Actor2Geo_ADM1Code', 'Actor2Geo_Lat', 'Actor2Geo_Long', 'Actor2Geo_FeatureID',
    'ActionGeo_Type', 'ActionGeo_FullName', 'ActionGeo_CountryCode', 'ActionGeo_ADM1Code', 'ActionGeo_Lat', 'ActionGeo_Long', 'ActionGeo_FeatureID',
    'DATEADDED', 'SOURCEURL'
]

def run_pipeline(days=365):
    print(f"--- Démarrage du pipeline pour les {days} derniers jours ---")
    dates = pd.date_range(end=datetime.now(), periods=days).strftime('%Y%m%d')
    
    all_data = []
    for d in dates:
        day_df = download_gdelt_file(d, COLNAMES)
        if not day_df.empty:
            all_data.append(day_df)
            print(f"Date {d} récupérée.")

    if not all_data:
        print("Aucune donnée trouvée.")
        return

    # CONSOLIDATION 
    full_df = pd.concat(all_data)
    
    # Nettoyage des données 
    clean_df = clean_data(full_df)
    clean_df.to_csv("data/processed/benin_cleaned_data.csv", index=False)
    print("Fichier nettoyé avec succès.")

    # Transformation  pour Data Scientist / ML
    upated_df = create_features(clean_df)
    upated_df.to_csv("data/processed/benin_trends.csv", index=False)
    print("Fichier mis à jour .")

if __name__ == "__main__":
    run_pipeline(days=3) # Mettre le nombre de jour qu'on désire