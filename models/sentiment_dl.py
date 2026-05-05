"""
Analyse de sentiment Deep Learning - Modele BERT multilingue (1-5 etoiles)
Scrape le contenu des articles via SOURCEURL pour une analyse semantique riche.
Mappe les etoiles en 3 classes : positif (4-5), neutre (3), negatif (1-2).
"""

from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
import html2text
from transformers import pipeline
import matplotlib.pyplot as plt
import seaborn as sns

# chargements des sources
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "benin_cleaned_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "models" / "outputs"
CACHE_PATH = OUTPUT_DIR / "scraped_articles.csv"
MAX_ARTICLE_CHARS = 2000
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Encoding": "gzip, deflate",
}


# chargement des données
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Day"])
    print(f"Donnees chargees : {len(df)} evenements")
    return df


# Texte de secours
def _build_fallback_text(row: pd.Series) -> str:
    """Texte de secours base sur les metadonnees si le scraping echoue."""
    parts = []
    if pd.notna(row.get("Actor1Name")):
        parts.append(str(row["Actor1Name"]))
    if pd.notna(row.get("Actor2Name")):
        parts.append(f"interacted with {row['Actor2Name']}")
    if pd.notna(row.get("ActionGeo_FullName")):
        parts.append(f"in {row['ActionGeo_FullName']}")
    return " ".join(parts) if parts else "event in Benin"


# chargement de cache (les données deja scrappés)
def _load_scrape_cache() -> dict[str, str]:
    if CACHE_PATH.exists():
        cached = pd.read_csv(CACHE_PATH)
        return {
            row["url"]: (row["text"] if pd.notna(row["text"]) else "")
            for _, row in cached.iterrows()
        }
    return {}


def _save_scrape_cache(cache: dict[str, str]) -> None:
    pd.DataFrame({"url": list(cache.keys()), "text": list(cache.values())}).to_csv(
        CACHE_PATH, index=False
    )


def scrape_article(url: str, cache: dict[str, str]) -> str:
    """Scrape le contenu d'un article, avec cache."""
    if url in cache:
        return cache[url]

    text = ""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript"]):
            tag.decompose()
        container = soup.find("article") or soup.find("main") or soup.find("body") or soup

        converter = html2text.HTML2Text()
        converter.body_width = 0
        converter.ignore_links = False
        converter.ignore_images = True
        converter.ignore_emphasis = False
        converter.baseurl = url
        text = converter.handle(str(container)).strip()[:MAX_ARTICLE_CHARS]

        if len(text) < 50:
            text = ""
    except Exception as e:
        print(f"  Erreur scraping {url}: {e}")

    cache[url] = text
    return text


def build_event_text(df: pd.DataFrame) -> pd.Series:
    """Scrape les articles via SOURCEURL avec fallback sur les metadonnees."""
    cache = _load_scrape_cache()
    texts = []
    scraped = 0
    fallback = 0

    for _, row in df.iterrows():
        url = row.get("SOURCEURL", "")
        if pd.notna(url) and isinstance(url, str) and url.startswith("http"):
            article = scrape_article(url, cache)
            if article:
                texts.append(article)
                scraped += 1
                continue
        texts.append(_build_fallback_text(row))
        fallback += 1

    _save_scrape_cache(cache)
    print(f"Articles : {scraped} scrapes, {fallback} via metadonnees ({len(cache)} en cache)")
    return pd.Series(texts, index=df.index)


def classify_sentiment(texts: list[str], batch_size: int = 16) -> list[list[dict]]:
    """Classifie le sentiment en etoiles (1-5) avec BERT multilingue."""
    clean_texts = []
    for t in texts:
        if not isinstance(t, str) or not t.strip():
            clean_texts.append("event in Benin")
        else:
            clean_texts.append(t)

    print("Chargement du modele BERT multilingue (nlptown/bert-base-multilingual-uncased-sentiment)...")
    classifier = pipeline(
        "sentiment-analysis",
        model="nlptown/bert-base-multilingual-uncased-sentiment",
        device=-1,
        truncation=True,
        top_k=None,
    )
    print(f"Classification de {len(clean_texts)} textes...")
    return classifier(clean_texts, batch_size=batch_size)


def map_to_three_classes(scores: list[dict]) -> str:
    """Mappe les etoiles (1-5) vers positif/neutre/negatif via score pondere.
    Calcule un score continu (1-5) et classe :
    - score >= 3.5 -> positif
    - score <= 2.5 -> negatif
    - entre les deux -> neutre
    """
    star_map = {"1 star": 1, "2 stars": 2, "3 stars": 3, "4 stars": 4, "5 stars": 5}
    weighted = sum(star_map[s["label"]] * s["score"] for s in scores)
    if weighted >= 3.5:
        return "positif"
    if weighted <= 2.5:
        return "negatif"
    return "neutre"


def analyze(df: pd.DataFrame) -> pd.DataFrame:
    """Pipeline complete d'analyse de sentiment."""
    texts = build_event_text(df)
    all_scores = classify_sentiment(texts.tolist())

    df = df.copy()
    df["sentiment"] = [map_to_three_classes(scores) for scores in all_scores]

    star_weights = [{s["label"]: s["score"] for s in scores} for scores in all_scores]
    df["pos_score"] = [w.get("4 stars", 0) + w.get("5 stars", 0) for w in star_weights]
    df["neu_score"] = [w.get("3 stars", 0) for w in star_weights]
    df["neg_score"] = [w.get("1 star", 0) + w.get("2 stars", 0) for w in star_weights]
    df["sentiment_num"] = df["sentiment"].map(
        {"positif": 1, "neutre": 0, "negatif": -1}
    )
    return df


def aggregate_temporal(df: pd.DataFrame) -> pd.DataFrame:
    """Agregation journaliere du sentiment."""
    daily = (
        df.groupby(df["Day"].dt.date)
        .agg(
            event_count=("GlobalEventID", "count"),
            sentiment_mean=("sentiment_num", "mean"),
            sentiment_std=("sentiment_num", "std"),
            pct_positif=("sentiment", lambda s: (s == "positif").mean()),
            pct_negatif=("sentiment", lambda s: (s == "negatif").mean()),
            avg_tone=("AvgTone", "mean"),
        )
        .reset_index()
        .rename(columns={"Day": "date"})
    )
    return daily


def plot_results(df: pd.DataFrame, daily: pd.DataFrame) -> None:
    """Genere les visualisations."""
    sns.set_theme(style="whitegrid")

    fig, ax = plt.subplots(figsize=(8, 5))
    order = ["positif", "neutre", "negatif"]
    palette = {"positif": "#2ecc71", "neutre": "#95a5a6", "negatif": "#e74c3c"}
    sns.countplot(
        data=df, x="sentiment", hue="sentiment",
        order=order, palette=palette, legend=False, ax=ax,
    )
    ax.set_title("Repartition du sentiment mediatique (BERT multilingue)")
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Nombre d'evenements")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "sentiment_dl_histogram.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    axes[0].plot(daily["date"], daily["sentiment_mean"], marker="o", color="#3498db")
    axes[0].fill_between(
        daily["date"],
        daily["sentiment_mean"] - daily["sentiment_std"].fillna(0),
        daily["sentiment_mean"] + daily["sentiment_std"].fillna(0),
        alpha=0.2,
        color="#3498db",
    )
    axes[0].axhline(0, color="gray", linestyle="--", linewidth=0.8)
    axes[0].set_title("Evolution du sentiment mediatique (BERT multilingue)")
    axes[0].set_ylabel("Sentiment moyen")

    axes[1].bar(daily["date"], daily["pct_positif"], color="#2ecc71", label="Positif")
    axes[1].bar(
        daily["date"],
        -daily["pct_negatif"],
        color="#e74c3c",
        label="Negatif",
    )
    axes[1].axhline(0, color="gray", linewidth=0.5)
    axes[1].set_title("Proportion positif / negatif par jour")
    axes[1].set_ylabel("Proportion")
    axes[1].legend()

    plt.xticks(rotation=45)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "sentiment_dl_timeseries.png", dpi=150)
    plt.close(fig)

    print(f"Visualisations sauvegardees dans {OUTPUT_DIR}")


def main():
    df = load_data(DATA_PATH)
    df = analyze(df)
    daily = aggregate_temporal(df)

    output_path = OUTPUT_DIR / "sentiment_dl.csv"
    daily.to_csv(output_path, index=False)
    print(f"Resultats sauvegardes : {output_path}")

    counts = df["sentiment"].value_counts()
    print(f"\nResume du sentiment :")
    for s in ["positif", "neutre", "negatif"]:
        n = counts.get(s, 0)
        print(f"  {s:8s} : {n:3d} ({n / len(df) * 100:.1f}%)")

    plot_results(df, daily)


if __name__ == "__main__":
    main()