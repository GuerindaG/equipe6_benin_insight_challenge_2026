import os
import pandas as pd
from google.cloud import bigquery


def get_bigquery_client(project_id: str) -> bigquery.Client:
    """
    Crée un client BigQuery.
    L'authentification est gérée via GOOGLE_APPLICATION_CREDENTIALS dans .env.
    """
    return bigquery.Client(project=project_id)


def download_data(
   project_id: str,
    date_start: int,
    date_end: int,
    limit: int | None, 
) -> pd.DataFrame:
    
    """Télécharge les événements GDELT concernant le Bénin via BigQuery."""
    client = get_bigquery_client(project_id)

    year = int(str(date_start)[:4])

    limit_clause = f"LIMIT {limit}" if limit is not None else ""

    query = f"""
        SELECT  globaleventid,
                sqldate,
                actor1name, actor1countrycode, actor1type1code,
                actor2name, actor2countrycode, actor2type1code,
                isrootevent,
                eventcode, eventbasecode, eventrootcode,
                quadclass,
                goldsteinscale, nummentions, numsources, numarticles, avgtone,
                actiongeo_fullname, actiongeo_countrycode,
                actiongeo_lat, actiongeo_long,
                sourceurl
        FROM `gdelt-bq.gdeltv2.events`
        WHERE YEAR = {year}
          AND SQLDATE BETWEEN {date_start} AND {date_end}
          AND (
              ActionGeo_CountryCode = 'BN'
              OR Actor1CountryCode  = 'BJ'
              OR Actor2CountryCode  = 'BJ'
          )
        ORDER BY SQLDATE ASC
        {limit_clause}
    """

    print(f"Requête  en cours ({date_start} - {date_end}, limit={limit:,})…")
    df = client.query(query).to_dataframe()
    print(f"{len(df):,} lignes récupérées avec succès.")
    return df