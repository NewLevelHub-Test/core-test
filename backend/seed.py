import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def run_seed():
    db_url = os.getenv("DATABASE_URL")
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES ('admin', 'admin@example.com', 'pbkdf2:sha256:260000$randomhash')
            ON CONFLICT (username) DO NOTHING;
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("Done")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_seed()