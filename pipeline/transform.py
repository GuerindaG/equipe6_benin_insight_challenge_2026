import pandas as pd
import numpy as np


# Colonnes numériques 
NUMERIC_COLS = [
    'goldsteinscale', 'avgtone', 'nummentions', 'numsources', 'numarticles',
    'actor1geo_lat', 'actor1geo_long', 'actor2geo_lat', 'actor2geo_long',
    'actiongeo_lat', 'actiongeo_long',
]

# Colonnes texte 
TEXT_COLS = [
    'actor1name', 'actor1countrycode', 'actor1type1code',
    'actor2name', 'actor2countrycode', 'actor2type1code',
    'eventcode', 'eventbasecode', 'eventrootcode',
    'actiongeo_fullname', 'actiongeo_countrycode',
    'sourceurl',
]

# Colonnes finales 
FINAL_COLS = [
    'globaleventid', 'sqldate', 'day', 'month', 'year', 'quarter',
    'actor1name', 'actor1countrycode', 'actor1type1code',
    'actor2name', 'actor2countrycode', 'actor2type1code',
    'eventcode', 'eventbasecode', 'eventrootcode', 'quadclass',
    'goldsteinscale', 'avgtone', 'nummentions', 'numsources', 'numarticles',
    'actiongeo_fullname', 'actiongeo_countrycode',
    'actiongeo_lat', 'actiongeo_long',
    'sentimentlabel', 'goldsteincategory', 'isrootevent',
    'sourceurl',
]


# suppression des doublons
def remove_duplicates_data(df: pd.DataFrame) -> pd.DataFrame:

    data_to_clean = len(df)
    df = df.drop_duplicates()
    if 'globaleventid' in df.columns:
        df = df.drop_duplicates(subset=['globaleventid'], keep='first')
    print(f"  [doublons]  {data_to_clean - len(df):,} lignes supprimées  {len(df):,} restantes")
    return df


# Standardiser les types numériques et convertir sqldate en datetime
def fix_types(df: pd.DataFrame) -> pd.DataFrame:

    # Colonne date principale
    if 'sqldate' in df.columns:
        df['day'] = pd.to_datetime(
            df['sqldate'].astype(str), format='%Y%m%d', errors='coerce'
        )

    # Colonnes numériques
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # globaleventid en entier
    if 'globaleventid' in df.columns:
        df['globaleventid'] = pd.to_numeric(df['globaleventid'], errors='coerce').astype('Int64')

    # isrootevent en booléen
    if 'isrootevent' in df.columns:
        df['isrootevent'] = df['isrootevent'].astype(bool)

    print(f"  [types]     conversion datetime et numériques effectuée")
    return df


# Valeurs manquantes
def handle_missing(df: pd.DataFrame) -> pd.DataFrame:

    # Suppression des colonnes entièrement vides
    before_cols = df.shape[1]
    df = df.dropna(axis=1, how='all')
    dropped = before_cols - df.shape[1]
    if dropped:
        print(f"  [manquants] {dropped} colonnes 100% vides supprimées")

    # Scores  médiane
    for col in ['goldsteinscale', 'avgtone']:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # Comptages
    for col in ['nummentions', 'numsources', 'numarticles']:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # Texte  'Unknown'
    for col in TEXT_COLS:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')

    missing_value = df.isnull().mean().mul(100).round(1)
    cols_with_missing = missing_value[missing_value > 0]
    if not cols_with_missing.empty:
        print(f"  [manquants] valeurs restantes (géo intentionnellement conservées) :")
        for c, pct in cols_with_missing.items():
            print(f"              {c}: {pct}%")

    return df


# Features dérivées
def add_features(df: pd.DataFrame) -> pd.DataFrame:

    # --- Temporelles ---
    if 'day' in df.columns:
        df['month']   = df['day'].dt.month
        df['quarter'] = df['day'].dt.quarter.map(
            {1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4'}
        )

    # --- Sentiment (avgtone) ---
    if 'avgtone' in df.columns:
        df['sentimentlabel'] = pd.cut(
            df['avgtone'],
            bins=[-np.inf, -5, 0, 0.001, 5, np.inf],
            labels=['Très négatif', 'Négatif', 'Neutre', 'Positif', 'Très positif'],
            right=False,
        ).astype(str)

    # --- Stabilité (goldsteinscale) ---
    if 'goldsteinscale' in df.columns:
        df['goldsteincategory'] = pd.cut(
            df['goldsteinscale'],
            bins=[-np.inf, -5, 0, 0.001, 5, np.inf],
            labels=[
                'Très déstabilisant', 'Déstabilisant',
                'Neutre',
                'Stabilisant', 'Très stabilisant',
            ],
            right=False,
        ).astype(str)

    print(f"  [features]  sentimentlabel, goldsteincategory, month, quarter ajoutés")
    return df


# Sélection des colonnes finales
def select_final_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Garde uniquement les colonnes utiles pour le dashboard et le ML."""
    cols = [c for c in FINAL_COLS if c in df.columns]
    df = df[cols]
    print(f"  [colonnes]  {len(cols)} colonnes conservées sur {df.shape[1]}")
    return df


# Fonction principale
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Pipeline de nettoyage"""
    if df.empty:
        print(" DataFrame vide, aucun traitement effectué.")
        return df

    # On s'assure que toutes les colonnes sont bien en minuscules 
    df.columns = df.columns.str.lower()

    print("\n Nettoyage des données…")
    df = remove_duplicates_data(df)
    df = fix_types(df)
    df = handle_missing(df)
    df = add_features(df)
    df = select_final_columns(df)
    print(f"Dataset final : {len(df):,} lignes × {df.shape[1]} colonnes\n")
    return df