import pandas as pd

def clean_data(df):
    """Nettoyage des types et suppression des doublons."""
    if df.empty:
        return df
    
    # Conversion date
    df['Day'] = pd.to_datetime(df['Day'], format='%Y%m%d', errors='coerce')
    
    # Suppression des colonnes 100% vides 
    df = df.dropna(axis=1, how='all')
    
    # Remplissage des valeurs numériques nulles
    cols_to_fix = ['GoldsteinScale', 'AvgTone', 'NumMentions']
    for col in cols_to_fix:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df.drop_duplicates(subset=['GlobalEventID'])