""" Initialize database """
import sqlite3
from src.utility.utils import get_project_path


if __name__ == '__main__':
    project_path = get_project_path()
    init_db_sql = project_path + 'src/database/create_tables.sql'
    with open(init_db_sql, 'r') as f:
        script = f.read()

    db = project_path + 'data/db/billing.db'
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.executescript(script)
