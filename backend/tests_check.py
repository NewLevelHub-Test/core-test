import os
import psycopg2
import chess.engine
from dotenv import load_dotenv

load_dotenv()

def run_tests():
    try:
        db_url = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE username='admin';")
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user:
            print("Database: Connection successful. User 'admin' found.")
        else:
            print("Database: Connection successful, but user 'admin' not found.")
    except Exception as e:
        print(f"Database: Connection error: {e}")

    sf_path = os.getenv("STOCKFISH_PATH")
    if os.path.exists(sf_path):
        try:
            engine = chess.engine.SimpleEngine.popen_uci(sf_path)
            board = chess.Board()
            info = engine.analyse(board, chess.engine.Limit(time=0.1))
            engine.quit()
            print(f"Stockfish: Engine is working. Score: {info['score']}")
        except Exception as e:
            print(f"Stockfish: Found, but failed to start: {e}")
    else:
        print(f"Stockfish: File not found at {sf_path}")

if __name__ == "__main__":
    run_tests()