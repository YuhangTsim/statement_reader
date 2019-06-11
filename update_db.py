import sqlite3
from src.utility.utils import get_project_path

DB_LOC = '/data/db/billing.db'

if __name__ == '__main__':
    project_path = get_project_path(__file__)
    try:
        db_loc = project_path + DB_LOC
        conn = sqlite3.connect(db_loc)
        cursor = conn.cursor()
    except Exception as e:
        pass
