import requests
import pandas as pd

API_URL = "https://www.donneesquebec.ca/recherche/api/3/action/datastore_search"
RESOURCE_ID = "b256f87f-40ec-4c79-bdba-a23e9c50e741"


def fetch_data(limit: int = 500) -> list[dict]:
    response = requests.get(
        API_URL,
        params={
            "resource_id": RESOURCE_ID,
            "limit": limit
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data["result"]["records"]






def full_run(datas: pd.DataFrame ):
    print ('dans full run')
    #Si aucune ligne à traiter, on ne fait rien
    #Si au moins une ligne, on va chercher la colonne   df["Mise_a_jour"] 
    #du premier enregistrement du dataFrame