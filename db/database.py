import psycopg2
from psycopg2 import sql
from config import DB_CONFIG


def get_connection():
    """Create and return a new database connection."""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Database connection failed: {e}")
        return None


def test_connection():
    """Test if the database connection works."""
    conn = get_connection()
    if conn:
        print("✅ Connected to PostgreSQL successfully!")
        conn.close()
        return True
    else:
        print("❌ Failed to connect to PostgreSQL.")
        return False


if __name__ == "__main__":
    test_connection()