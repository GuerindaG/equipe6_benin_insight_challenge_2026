"""
Topic modeling offline avec BERTopic sur les articles scrapés.
Génère les fichiers de sortie utilisés par le dashboard.
"""
import pandas as pd
import numpy as np
import re
from pathlib import Path

from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).parent.parent
INPUT_PATH = ROOT / "models/outputs/scraped_articles.csv"
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
FIG_DIR = ROOT / "outputs/figures"
FIG_DIR.mkdir(exist_ok=True)


def preprocess_text(text):
    if pd.isna(text):
        return ""
    t = str(text).lower()
    t = re.sub(r'https?://\S+', '', t)
    t = re.sub(r'[^\w\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def main():
    print("Chargement des articles...")
    df = pd.read_csv(INPUT_PATH, engine='python', on_bad_lines='skip')
    df = df.dropna(subset=["text"])
    df["text_clean"] = df["text"].apply(preprocess_text)
    df = df[df["text_clean"].str.len() > 20]
    df["SQLDATE"] = pd.to_datetime(df["SQLDATE"], format="%Y-%m-%d", errors="coerce")
    df = df.dropna(subset=["SQLDATE"])

    # Échantillon représentatif (max 8000 pour performance)
    n = len(df)
    if n > 8000:
        df = df.sample(n=8000, random_state=42).sort_values("SQLDATE").reset_index(drop=True)
        print(f"Échantillon de {len(df)} articles (stratifié aléatoire)")
    else:
        print(f"Utilisation des {n} articles disponibles")

    docs = df["text_clean"].tolist()
    dates = df["SQLDATE"].tolist()

    print("Entraînement BERTopic...")
    vectorizer = CountVectorizer(stop_words="english", ngram_range=(1, 2), min_df=3)
    embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    topic_model = BERTopic(
        embedding_model=embedding_model,
        vectorizer_model=vectorizer,
        min_topic_size=15,
        verbose=True,
    )
    topics, probs = topic_model.fit_transform(docs)

    # Sauvegarde infos topics
    topic_info = topic_model.get_topic_info()
    topic_info.to_csv(OUTPUT_DIR / "topics_info.csv", index=False)

    # Sauvegarde articles avec leur topic
    df["topic"] = topics
    df["topic_prob"] = probs if probs is not None else np.nan
    df[["GLOBALEVENTID", "SQLDATE", "SOURCEURL", "text", "topic", "topic_prob"]].to_csv(
        OUTPUT_DIR / "topics_per_article.csv", index=False
    )

    # Évolution temporelle
    print("Évolution temporelle...")
    topics_over_time = topic_model.topics_over_time(docs, dates)
    topics_over_time.to_csv(OUTPUT_DIR / "topics_over_time.csv", index=False)

    # Visualisations
    print("Sauvegarde des figures...")
    try:
        fig = topic_model.visualize_topics()
        fig.write_html(str(FIG_DIR / "bertopic_topics.html"))
    except Exception as e:
        print(f"Fig topics ignorée: {e}")

    try:
        fig_t = topic_model.visualize_topics_over_time(topics_over_time)
        fig_t.write_html(str(FIG_DIR / "bertopic_topics_over_time.html"))
    except Exception as e:
        print(f"Fig over_time ignorée: {e}")

    try:
        fig_b = topic_model.visualize_barchart(top_n_topics=10)
        fig_b.write_html(str(FIG_DIR / "bertopic_barchart.html"))
    except Exception as e:
        print(f"Fig barchart ignorée: {e}")

    # Labels générés
    labels = topic_model.generate_topic_labels()
    pd.DataFrame({"topic": range(len(labels)), "label": labels}).to_csv(
        OUTPUT_DIR / "topic_labels.csv", index=False
    )

    print("Topic modeling terminé. Fichiers sauvegardés dans outputs/")


if __name__ == "__main__":
    main()
