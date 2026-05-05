import pandas as pd
import numpy as np


def create_features(df: pd.DataFrame) -> pd.DataFrame:
   
    if df.empty:
        print("DataFrame vide, aucune feature créée.")
        return df

    print("Création des features agrégées par jour…")

    # --- Agrégations numériques ---
    agg = df.groupby('day').agg(
        event_count=('globaleventid', 'count'),
        goldsteinscale_mean=('goldsteinscale', 'mean'),
        goldsteinscale_min=('goldsteinscale', 'min'),
        avgtone_mean=('avgtone', 'mean'),
        numarticles_sum=('numarticles', 'sum'),
        numsources_sum=('numsources', 'sum'),
    ).round(3)

    # --- Sentiment dominant ---
    if 'sentimentlabel' in df.columns:
        sentiment_mode = (
            df.groupby('day')['sentimentlabel']
            .agg(lambda x: x.mode()[0] if not x.mode().empty else 'Unknown')
            .rename('dominant_sentiment')
        )
        agg = agg.join(sentiment_mode)

    # --- QuadClass dominant ---
    if 'quadclass' in df.columns:
        quadclass_map = {
            1: 'Coopération verbale',
            2: 'Coopération matérielle',
            3: 'Conflit verbal',
            4: 'Conflit matériel',
        }
        quad_mode = (
            df.groupby('day')['quadclass']
            .agg(lambda x: x.mode()[0] if not x.mode().empty else np.nan)
            .map(quadclass_map)
            .rename('dominant_quadclass')
        )
        agg = agg.join(quad_mode)

    # --- Indicateurs glissants (7 jours) ---
    agg = agg.sort_index()
    agg['event_volatility_7d'] = agg['event_count'].rolling(window=7, min_periods=1).std().round(3)
    agg['tone_ma_7d']          = agg['avgtone_mean'].rolling(window=7, min_periods=1).mean().round(3)

    result = agg.reset_index()
    print(f" Features créées : {len(result):,} jours couverts, {result.shape[1]} colonnes\n")
    return result