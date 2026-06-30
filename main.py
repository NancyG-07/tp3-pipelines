import os
from datetime import datetime, timezone

import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


def main():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_ping_log (
                    id BIGSERIAL PRIMARY KEY,
                    called_at_utc TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    source TEXT NOT NULL
                );
            """)

            cur.execute("""
                INSERT INTO pipeline_ping_log (called_at_utc, source)
                VALUES (%s, %s);
            """, (
                datetime.now(timezone.utc),
                "local-ubuntu-supabase"
            ))

            cur.execute("""
                SELECT id, called_at_utc, source
                FROM pipeline_ping_log
                ORDER BY id DESC
                LIMIT 5;
            """)

            rows = cur.fetchall()

        conn.commit()

    print("Connexion réussie.")
    print("Dernières lignes :")

    for row in rows:
        print(row)


if __name__ == "__main__":
    main()