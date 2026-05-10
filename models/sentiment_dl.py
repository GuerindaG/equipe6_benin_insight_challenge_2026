#!/usr/bin/env python3
"""
sentiment_dl.py
===============
Analyse de sentiment des articles GDELT liés au Bénin via un modèle
BERT multilingue (nlptown/bert-base-multilingual-uncased-sentiment).

Entrée  : models/outputs/scraped_articles.csv (produit par scrapping.py)
Sorties :
    • models/outputs/sentiment_dl.csv            — résultats agrégés journaliers
    • models/outputs/sentiment_dl_histogram.png   — distribution globale
    • models/outputs/sentiment_dl_timeseries.png  — évolution temporelle

Usage :
    python models/sentiment_dl.py
"""

import warnings
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tqdm.auto import tqdm

try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    TRANSFORMERS_OK = True
except ImportError:
    TRANSFORMERS_OK = False
    warnings.warn(
        "transformers/torch non installés. "
        "Installez-les : pip install transformers torch"
    )

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_CSV = PROJECT_ROOT / "models" / "outputs" / "scraped_articles.csv"
OUTPUT_DIR = PROJECT_ROOT / "models" / "outputs"
CHUNK_SIZE = 512           # tokens max pour BERT (~1000 caractères en moy.)
BATCH_SIZE = 16            # inférence par batch
MAX_TEXT_LEN = 2000        # tronque les articles trop longs pour alléger

# Étoiles BERT → labels métier
STAR_TO_LABEL = {1: "Négatif", 2: "Négatif", 3: "Neutre",
                  4: "Positif", 5: "Positif"}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def chunkify(text: str, chunk_size: int = 2000) -> List[str]:
    """Découpe un texte long en chunks de ~chunk_size caractères."""
    if not text or pd.isna(text):
        return []
    text = str(text).strip()
    parts = []
    for i in range(0, len(text), chunk_size):
        t = text[i:i + chunk_size].strip()
        if len(t) > 30:          # ignore les morceaux trop courts
            parts.append(t)
    return parts


def aggregate_stars(stars: List[int]) -> dict:
    """Agrège une liste d'étoiles (1-5) en statistiques finales."""
    if not stars:
        return {"sentiment_label": "Neutre", "sentiment_score": 3.0,
                "positif": 0.0, "negatif": 0.0, "neutre": 0.0}
    arr = np.array(stars)
    mean_star = float(np.mean(arr))

    # Seuils pour classer l'ensemble de l'article
    if mean_star >= 3.5:
        label = "Positif"
    elif mean_star <= 2.5:
        label = "Négatif"
    else:
        label = "Neutre"

    total = len(arr)
    return {
        "sentiment_label": label,
        "sentiment_score": round(mean_star, 2),
        "positif": round(int(np.sum(arr >= 4)) / total, 3),
        "negatif": round(int(np.sum(arr <= 2)) / total, 3),
        "neutre": round(int(np.sum(arr == 3)) / total, 3),
    }


# ---------------------------------------------------------------------------
# PIPELINE BERT
# ---------------------------------------------------------------------------
class SentimentAnalyzer:
    def __init__(self, model_name: str = "nlptown/bert-base-multilingual-uncased-sentiment"):
        if not TRANSFORMERS_OK:
            raise RuntimeError("transformers/torch sont requis pour SentimentAnalyzer")

        print(f"Chargement du modèle {model_name} …")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.classifier = pipeline(
            "sentiment-analysis",
            model=self.model,
            tokenizer=self.tokenizer,
            device=-1,            # CPU (mettre 0 si GPU disponible)
            truncation=True,
            max_length=CHUNK_SIZE,
        )
        print("Modèle prêt.")

    def predict_text(self, text: str) -> List[int]:
        """Retourne la liste des étoiles prédites pour chaque chunk du texte."""
        chunks = chunkify(text, MAX_TEXT_LEN)
        if not chunks:
            return []
        results = self.classifier(chunks, batch_size=BATCH_SIZE)
        stars = []
        for r in results:
            label = r["label"]
            # label = "1 star", "2 stars", …, "5 stars"
            star = int(label.split()[0])
            stars.append(star)
        return stars

    def run(self, csv_path: Path) -> pd.DataFrame:
        if not csv_path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {csv_path}")

        df = pd.read_csv(csv_path, parse_dates=["SQLDATE"])
        required = {"GLOBALEVENTID", "SQLDATE", "text"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Colonnes manquantes dans {csv_path} : {missing}")

        print(f"\nAnalyse de sentiment sur {len(df):,} articles …")
        records = []
        for _, row in tqdm(df.iterrows(), total=len(df), desc="BERT"):
            stars = self.predict_text(row["text"])
            agg = aggregate_stars(stars)
            agg["GLOBALEVENTID"] = int(row["GLOBALEVENTID"])
            agg["SQLDATE"] = row["SQLDATE"]
            records.append(agg)

        return pd.DataFrame.from_records(records)


# ---------------------------------------------------------------------------
# VISUALISATIONS
# ---------------------------------------------------------------------------
def plot_histogram(df: pd.DataFrame, out_path: Path):
    fig, ax = plt.subplots(figsize=(7, 4))
    order = ["Négatif", "Neutre", "Positif"]
    counts = df["sentiment_label"].value_counts().reindex(order, fill_value=0)

    bars = ax.bar(counts.index, counts.values, color=["#e15759", "#f28e2b", "#59a14f"])
    ax.set_title("Distribution globale des sentiments (BERT)", fontsize=12, weight="bold")
    ax.set_ylabel("Nombre d'articles")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{int(height)}", xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    fontsize=9)
    plt.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Histogramme : {out_path}")


def plot_timeseries(df: pd.DataFrame, out_path: Path):
    df = df.copy()
    df["date"] = pd.to_datetime(df["SQLDATE"])
    daily = df.groupby("date").agg(
        mean_score=("sentiment_score", "mean"),
        n=("sentiment_score", "count"),
    ).reset_index()

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(daily["date"], daily["mean_score"], color="#4e79a7", linewidth=1.2)
    ax.axhline(3.0, color="grey", linestyle="--", linewidth=0.8, alpha=0.7)
    ax.fill_between(daily["date"], daily["mean_score"], 3.0,
                    where=daily["mean_score"] >= 3.0, color="#59a14f", alpha=0.15)
    ax.fill_between(daily["date"], daily["mean_score"], 3.0,
                    where=daily["mean_score"] < 3.0, color="#e15759", alpha=0.15)
    ax.set_title("Évolution temporelle du sentiment (score moyen journalier)",
                 fontsize=12, weight="bold")
    ax.set_ylabel("Score moyen (1-5)")
    ax.set_xlabel(None)
    ax.set_ylim(1, 5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Série temporelle : {out_path}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    if not TRANSFORMERS_OK:
        print("ERREUR : installez transformers et torch pour exécuter ce script.")
        print("   pip install transformers torch tqdm")
        return

    analyzer = SentimentAnalyzer()
    results = analyzer.run(INPUT_CSV)

    # Agrégation journalière
    daily = results.copy()
    daily["date"] = pd.to_datetime(daily["SQLDATE"]).dt.date
    daily_agg = daily.groupby("date").agg(
        sentiment_moyen=("sentiment_score", "mean"),
        nb_articles=("sentiment_score", "count"),
        pct_positif=("positif", "mean"),
        pct_neutre=("neutre", "mean"),
        pct_negatif=("negatif", "mean"),
        sentiment_dominant=("sentiment_label", lambda s: s.mode().iloc[0] if not s.mode().empty else "Neutre"),
    ).round(3).reset_index()

    csv_out = OUTPUT_DIR / "sentiment_dl.csv"
    daily_agg.to_csv(csv_out, index=False)
    print(f"\nRésultats agrégés : {csv_out}")

    plot_histogram(results, OUTPUT_DIR / "sentiment_dl_histogram.png")
    plot_timeseries(results, OUTPUT_DIR / "sentiment_dl_timeseries.png")
    print("\nAnalyse terminée.")


if __name__ == "__main__":
    main()
