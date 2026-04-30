import pandas as pd
import requests
import io
import zipfile
import os

def download_gdelt_file(date, colnames, output_dir="data/raw"):
    """Téléchargement des données par rapport à une période donnée."""
    base_url = "http://data.gdeltproject.org/events/"
    url = f"{base_url}{date}.export.CSV.zip"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                df = pd.read_csv(z.open(z.namelist()[0]), sep='\t', header=None, 
                                 names=colnames, low_memory=False)
                
                # On filtre par rapport au benin
                benin_df = df[df['ActionGeo_CountryCode'] == 'BN'].copy()
                return benin_df
        return pd.DataFrame()
    except Exception as e:
        print(f"Erreur sur {date}: {e}")
        return pd.DataFrame()