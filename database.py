import os
import pymysql
from dotenv import load_dotenv

load_dotenv("tesi_env/.env")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))

def get_db_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT,
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id VARCHAR(36) PRIMARY KEY,
                    html_content LONGTEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.close()
        print("[DATABASE] Connessione a MySQL riuscita e tabella 'reports' verificata.")
    except Exception as e:
        print(f"[DATABASE ERR] Errore di connessione a MySQL: {e}")

def salva_report_html(report_id: str, html_content: str):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        sql = "INSERT INTO reports (id, html_content) VALUES (%s, %s)"
        cursor.execute(sql, (report_id, html_content))
    conn.close()

def ottieni_report_html(report_id: str):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        sql = "SELECT html_content FROM reports WHERE id = %s"
        cursor.execute(sql, (report_id,))
        row = cursor.fetchone()       # estrae la prima riga
    conn.close()
    return row["html_content"] if row else None