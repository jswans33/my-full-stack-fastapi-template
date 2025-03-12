import psycopg


def check_postgres_connection():
    try:
        # Using the same connection parameters from .env
        conn = psycopg.connect(
            host="localhost",
            port=5432,
            dbname="app",
            user="postgres",
            password="o2NS8ZROp9MCyZoFtjwxrA",
        )
        conn.close()
        print("Successfully connected to PostgreSQL!")
        return True
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        return False


if __name__ == "__main__":
    check_postgres_connection()
