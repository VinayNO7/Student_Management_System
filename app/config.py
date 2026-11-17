import os
import urllib.parse

# Load .env file with graceful fallback if python-dotenv is not installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Manual .env parser fallback
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "student_management_db")
FALLBACK_TO_SQLITE = os.getenv("FALLBACK_TO_SQLITE", "True").lower() in ("true", "1", "yes")

APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# Determine active database engine
db_info = {
    "engine": "unknown",
    "host": DB_HOST,
    "port": DB_PORT,
    "user": DB_USER,
    "database": DB_NAME,
    "connected": False,
    "message": ""
}

def resolve_database_url() -> str:
    """
    Attempts to connect to MySQL and ensure the database exists.
    If MySQL connection succeeds, returns the MySQL connection string.
    If MySQL fails and FALLBACK_TO_SQLITE is enabled, returns SQLite connection string.
    """
    global db_info
    escaped_password = urllib.parse.quote_plus(DB_PASSWORD)
    mysql_server_url = f"mysql+pymysql://{DB_USER}:{escaped_password}@{DB_HOST}:{DB_PORT}/"
    mysql_db_url = f"{mysql_server_url}{DB_NAME}?charset=utf8mb4"

    try:
        import pymysql
        # Attempt connection to MySQL server to check if it's up
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=3
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.close()

        db_info["engine"] = "mysql"
        db_info["connected"] = True
        db_info["message"] = f"Successfully connected to MySQL database '{DB_NAME}' on {DB_HOST}:{DB_PORT}."
        print(f"[Database] {db_info['message']}")
        return mysql_db_url

    except Exception as e:
        error_msg = str(e)
        if FALLBACK_TO_SQLITE:
            sqlite_url = "sqlite:///./student_management.db"
            db_info["engine"] = "sqlite"
            db_info["connected"] = True
            db_info["message"] = (
                f"MySQL connection to {DB_HOST}:{DB_PORT} failed ({error_msg}). "
                "Operating in SQLite mode (./student_management.db). "
                "Configure your MySQL credentials in .env to use MySQL."
            )
            print(f"[Database Warning] {db_info['message']}")
            return sqlite_url
        else:
            db_info["engine"] = "mysql"
            db_info["connected"] = False
            db_info["message"] = f"MySQL connection failed: {error_msg}"
            raise ConnectionError(f"Cannot connect to MySQL database at {DB_HOST}:{DB_PORT}: {error_msg}")

DATABASE_URL = resolve_database_url()

