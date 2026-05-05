import os
import pandas as pd
from dotenv import load_dotenv

from pipeline.extract import download_data
from pipeline.transform import clean_data
from pipeline.processing import create_features

load_dotenv()


def run_pipeline(
    date_start: int,
    date_end: int,
    limit: int | None,
):
    print(f"\n{'='*55}")
    print(f"  PIPELINE GDELT — Bénin Insights Challenge 2026")
    print(f"  Période : {date_start} - {date_end}")
    print(f"{'='*55}\n")

    # Extraction                                                    
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError(
            "GCP_PROJECT_ID non défini. "
            "Vérifiez votre fichier .env."
        )

    raw_df = download_data(
        project_id=project_id,
        date_start=date_start,
        date_end=date_end,
        limit=limit,
    )

    if raw_df.empty:
        print("Aucune donnée trouvée.")
        return


    # Sauvegarde brute 
    os.makedirs("data/raw", exist_ok=True)
    raw_df.to_csv("data/raw/benin_raw.csv", index=False)
    print(f"fichier sauvegardé - data/processed/benin_raw.csv\n")

    # Nettoyage        
    os.makedirs("data/processed", exist_ok=True)                                 
    clean_df = clean_data(raw_df)
    clean_df.to_csv("data/processed/benin_cleaned_data.csv", index=False)
    print(f" Fichier nettoyé et sauvegardé - data/processed/benin_cleaned_data.csv\n")

    # Agrégation  journalière 
    trends_df = create_features(clean_df)
    trends_df.to_csv("data/processed/benin_trends.csv", index=False)
    print(f"Tendances sauvegardées - data/processed/benin_trends.csv\n")

    print("Pipeline terminé avec succès !")
    print(f"\nFichiers produits :")
    print(f" data/processed/benin_raw.csv          — données brutes ")
    print(f" data/processed/benin_cleaned_data.csv — dataset nettoyé ")
    print(f" data/processed/benin_trends.csv       — agrégat journalier ")


if __name__ == "__main__":
    run_pipeline(
        date_start=20250101,
        date_end=20251231,
        limit=1_000,# None = tout prendre, un nombre = limiter
    )