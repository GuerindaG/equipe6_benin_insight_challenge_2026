"""
Scraping des articles GDELT via SOURCEURL.
Sauvegarde incrementielle dans scraped_articles.csv.
Colonnes : GLOBALEVENTID, SQLDATE, SOURCEURL, text.
"""

import re
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
import html2text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "bq-results-20260502-112631-1777721378470.csv"
OUTPUT_DIR = PROJECT_ROOT / "models" / "outputs"
OUTPUT_PATH = OUTPUT_DIR / "scraped_articles.csv"
MAX_CHARS = 4000
SAVE_EVERY = 100

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Encoding": "gzip, deflate",
}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["SQLDATE"])
    print(f"Donnees chargees : {len(df)} evenements")
    return df


def _load_existing() -> dict[int, str]:
    if OUTPUT_PATH.exists():
        existing = pd.read_csv(OUTPUT_PATH)
        return {
            int(row["GLOBALEVENTID"]): str(row["text"])
            for _, row in existing.iterrows()
            if pd.notna(row["text"]) and str(row["text"]).strip()
        }
    return {}


def clean_text(text: str) -> str:
    """Supprime les URLs et liens du texte extrait."""
    if not text:
        return ""
    # Supprime les liens markdown [text](url)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Supprime les URLs brutes (http, https, ftp)
    text = re.sub(
        r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?",
        "",
        text,
        flags=re.IGNORECASE,
    )
    # Supprime les URLs sans protocole (www.example.com)
    text = re.sub(r"www\.\S+\.\S+", "", text)
    # Nettoyage des espaces multiples et lignes vides
    text = re.sub(r"\n\s*\n", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def scrape(url: str) -> str:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript"]):
            tag.decompose()
        container = soup.find("article") or soup.find("main") or soup.find("body") or soup
        c = html2text.HTML2Text()
        c.body_width = 0
        c.ignore_links = False
        c.ignore_images = True
        c.ignore_emphasis = False
        text = c.handle(str(container)).strip()
        text = clean_text(text)[:MAX_CHARS]
        return text if len(text) >= 50 else ""
    except Exception as e:
        print(f"  Erreur {url[:80]}: {e}")
        return ""


def run() -> pd.DataFrame:
    df = load_data(DATA_PATH)
    existing = _load_existing()
    already_done = set(existing.keys())
    total = len(df)

    rows = []
    scraped = reused = failed = 0

    for i, (_, row) in enumerate(df.iterrows()):
        gid = int(row["GLOBALEVENTID"])
        sqldate = row["SQLDATE"]
        url = row.get("SOURCEURL", "")

        if gid in already_done:
            rows.append([gid, sqldate, url if pd.notna(url) else "", existing[gid]])
            reused += 1
            continue

        text = scrape(url) if (pd.notna(url) and isinstance(url, str) and url.startswith("http")) else ""
        rows.append([gid, sqldate, url if pd.notna(url) else "", text])
        if text:
            scraped += 1
        else:
            failed += 1

        # Sauvegarde incrementielle
        if (i + 1) % SAVE_EVERY == 0:
            pd.DataFrame(rows, columns=["GLOBALEVENTID", "SQLDATE", "SOURCEURL", "text"]).to_csv(
                OUTPUT_PATH, index=False
            )
            print(f"  [{i + 1}/{total}] {scraped} OK, {reused} cache, {failed} echecs", flush=True)

    # Sauvegarde finale
    result = pd.DataFrame(rows, columns=["GLOBALEVENTID", "SQLDATE", "SOURCEURL", "text"])
    result.to_csv(OUTPUT_PATH, index=False)
    print(f"\n=== TERMINE : {scraped} scrapes, {reused} reutilises, {failed} echecs ===")
    print(f"Sortie : {OUTPUT_PATH}")
    return result


if __name__ == "__main__":
    run()
