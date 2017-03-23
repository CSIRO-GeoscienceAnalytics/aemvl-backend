import sqlite3
from pathlib import Path

DB_FILE_PATH =  'skeleton.db'
SQL_FILE_PATH = 'skeleton.sql'

def create_skeleton_db():
    db_file = Path(DB_FILE_PATH)
    if db_file.is_file():
        db_file.unlink()

    with open(SQL_FILE_PATH, 'r') as sql_file:
        sql = sql_file.read()

    with sqlite3.connect(DB_FILE_PATH) as connection:
        cursor = connection.cursor()
        cursor.executescript(sql)

if __name__ == "__main__":
    create_skeleton_db()
