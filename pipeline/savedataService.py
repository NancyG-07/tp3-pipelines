import os
from datetime import datetime, timezone

import psycopg
from dotenv import load_dotenv

import pandas as pd



load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

def ensureDatabase():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        
                CREATE TABLE IF NOT EXISTS pipeline_extract_log (
                    id BIGSERIAL PRIMARY KEY,                   
                    Mise_a_jour TEXT NOT NULL
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS occupation_hopitaux (
                    id SERIAL PRIMARY KEY,

                    nom_etablissement TEXT NOT NULL,
                    region TEXT,
                    nom_installation TEXT,

                    nombre_civieres_fonctionnelles INTEGER,
                    nombre_civieres_occupees INTEGER,
                    nombre_patients_attente INTEGER,
                    nombre_patients_24h INTEGER,
                    nombre_patients_48h INTEGER,
                    nombre_patients_urgence INTEGER,
                    nombre_patients_attente_pec INTEGER,

                    

                    mise_a_jour TIMESTAMP NOT NULL,

                    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

                   
                );
                        """)

def isInDB( records : list[dict]):
    if not records:
        return False

    premiere_date = records[0]["Mise_a_jour"]

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM pipeline_extract_log
                WHERE mise_a_jour = %s
                LIMIT 1
                """,
                (premiere_date,)
            )

            resultat= cur.fetchone() is not None
            

            return resultat




def transform_data(records: list[dict]) -> list[dict]:
    df = pd.DataFrame(records)

    numeric_columns = [
        "Nombre_de_civieres_fonctionnelles",
        "Nombre_de_civieres_occupees",
        "Nombre_de_patients_sur_civiere_plus_de_24_heures",
        "Nombre_de_patients_sur_civiere_plus_de_48_heures",
        "Nombre_total_de_patients_presents_a_lurgence",
        "Nombre_total_de_patients_en_attente_de_PEC",
        "DMS_sur_civiere",
        "DMS_ambulatoire"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["Mise_a_jour"] = pd.to_datetime(df["Mise_a_jour"], errors="coerce")

    df["est_total_regional"] = df["Nom_installation"].eq("Total régional")
    df["est_total_quebec"]= df["Nom_installation"].eq("Ensemble du Québec")
  
    liste = df.to_dict("records")
    liste = filtrer_records(liste)
    print(liste)
    
    return liste

def filtrer_records(records: list[dict]) -> list[dict]:
    exclusions = {"total régional", "ensemble du québec"}

    return [
        record for record in records
        if str(record.get("Nom_etablissement", "")).strip().lower() not in exclusions
    ]

def to_int_or_none(value):
    try:
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()

            if value == "":
                return None

            if "pas d'information disponible" in value.lower():
                return None

        return int(value)

    except (ValueError, TypeError):
        return None
    
def mapOccupationRecord(record: dict) -> dict:
    return {
        "nom_etablissement": record.get("Nom_etablissement"),
        "region": record.get("Region"),
        "nom_installation": record.get("Nom_installation"),

        "nombre_civieres_fonctionnelles": to_int_or_none(
            record.get("Nombre_de_civieres_fonctionnelles")
        ),

        "nombre_civieres_occupees": to_int_or_none(
            record.get("Nombre_de_civieres_occupees")
        ),

        "nombre_patients_24h": to_int_or_none(
            record.get("Nombre_de_patients_sur_civiere_plus_de_24_heures")
        ),

        "nombre_patients_48h": to_int_or_none(
            record.get("Nombre_de_patients_sur_civiere_plus_de_48_heures")
        ),

        "nombre_patients_urgence": to_int_or_none(
            record.get("Nombre_total_de_patients_presents_a_lurgence")
        ),

        "nombre_patients_attente_pec": to_int_or_none(
            record.get("Nombre_total_de_patients_en_attente_de_PEC")
        ),


        "mise_a_jour": record.get("Mise_a_jour"),
    }

def saveOccupation(records: list[dict], premiere_date):
    if not records:
        print("Aucun record à sauvegarder.")
        return

    mapped_records = [mapOccupationRecord(record) for record in records]


    
    print(mapped_records)
    insert_sql = """
        INSERT INTO occupation_hopitaux (
            nom_etablissement,
            region,
            nom_installation,
            nombre_civieres_fonctionnelles,
            nombre_civieres_occupees,
            nombre_patients_24h,
            nombre_patients_48h,
            nombre_patients_urgence,
            nombre_patients_attente_pec,
            
            mise_a_jour
        )
        VALUES (
            %(nom_etablissement)s,
            %(region)s,
            %(nom_installation)s,
            %(nombre_civieres_fonctionnelles)s,
            %(nombre_civieres_occupees)s,
            %(nombre_patients_24h)s,
            %(nombre_patients_48h)s,
            %(nombre_patients_urgence)s,
            %(nombre_patients_attente_pec)s,
           
            %(mise_a_jour)s
        );
        
    """

    with psycopg.connect(os.environ["DATABASE_URL"], prepare_threshold=False) as conn:
        with conn.cursor() as cur:
            cur.executemany(insert_sql, mapped_records)
            
            cur.execute(
                    """
                    insert into pipeline_extract_log(mise_a_jour)
                    values(%s)
                    """,(premiere_date,)

                )

        conn.commit()

    print(f"{len(mapped_records)} records traités.")  


def saveData(records : list[dict]):
    ensureDatabase();

    if not isInDB(records):
        premiere_date = records[0]["Mise_a_jour"]
        records = transform_data(records)
        saveOccupation(records, premiere_date)
        print('pas là')
        #On ajoute à la table des données enregistrées
        #On transforme les données
        #On ajoute chaque ligne à la table des lignes 

    else:
        print('dejà là')

    

