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

    # ------------------------------------------------------------------
    # 1. EXTRACTION
    # ------------------------------------------------------------------
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
    raw_path = "data/raw/benin_raw.csv"
    raw_df.to_csv(raw_path, index=False)
    print(f"Fichier sauvegardé — {raw_path}\n")

    # ------------------------------------------------------------------
    # 2. TRANSFORMATION
    # ------------------------------------------------------------------
    os.makedirs("data/processed", exist_ok=True)
    clean_df = clean_data(raw_df)
    clean_path = "data/processed/benin_cleaned_data.csv"
    clean_df.to_csv(clean_path, index=False)
    print(f"Fichier nettoyé et sauvegardé — {clean_path}\n")

    # ------------------------------------------------------------------
    # 3. AGRÉGATION
    # ------------------------------------------------------------------
    trends_df = create_features(clean_df)
    trends_path = "data/processed/benin_trends.csv"
    trends_df.to_csv(trends_path, index=False)
    print(f"Tendances sauvegardées — {trends_path}\n")

    # ------------------------------------------------------------------
    # RÉCAPITULATIF
    # ------------------------------------------------------------------
    print("Pipeline terminé avec succès !")
    print(f"\nFichiers produits :")
    print(f"  {raw_path:<45} — données brutes")
    print(f"  {clean_path:<45} — dataset nettoyé")
    print(f"  {trends_path:<45} — agrégat journalier")


if __name__ == "__main__":
    run_pipeline(
        date_start=20250101,
        date_end=20251231,
        limit=1_000,  # None = tout prendre
    )
