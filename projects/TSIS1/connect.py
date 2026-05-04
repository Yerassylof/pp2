import psycopg2
from config import DB_CONFIG

def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(**DB_CONFIG)

if __name__ == "__main__":
    try:
        conn = get_connection()
        print("CONNECTED successfully!")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")