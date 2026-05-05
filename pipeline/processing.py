def create_features(df):
    """Crée des indicateurs agrégés par jour pour le ML."""
    if df.empty:
        return df
        
    features_df = df.groupby('Day').agg({
        'GlobalEventID': 'count',
        'GoldsteinScale': 'mean',
        'AvgTone': 'mean',
        'NumArticles': 'sum'
    }).rename(columns={'GlobalEventID': 'event_count'})
    
    # Calcul d'une moyenne mobile sur 7 jours pour voir la tendance
    features_df['event_volatility_7d'] = features_df['event_count'].rolling(window=7).std()
    
    return features_df.reset_index()