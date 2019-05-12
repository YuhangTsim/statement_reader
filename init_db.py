""" Initialize database """
import sqlite3
from src.utility.utils import get_project_path
from src.utility.utils import import_conf, import_conf_query, del_db

DEFAULT_CONFIG_PATH = '/conf/db_default_config.json'
PERSONAL_CATE_CONFIG_PATH = '/conf/personal_category_config.json'
CREATE_DB_SCRIPT_PATH = '/src/database/create_tables.sql'
INSERT_CONF_SCRIPT_PATH = '/src/database/insert_init_setting.sql'
DB_LOC = '/data/db/billing.db'

if __name__ == '__main__':
    project_path = get_project_path(__file__)
    default_conf = import_conf(project_path + DEFAULT_CONFIG_PATH)
    personal_cate_conf = import_conf(project_path + PERSONAL_CATE_CONFIG_PATH)
    conf = {**default_conf, **personal_cate_conf}
    insert_queries = import_conf_query(project_path + INSERT_CONF_SCRIPT_PATH)

    try:
        with open(project_path + CREATE_DB_SCRIPT_PATH, 'r') as f:
            init_script = f.read()
        db_loc = project_path + DB_LOC
        conn = sqlite3.connect(db_loc)
        cursor = conn.cursor()
        cursor.executescript(init_script)

        for table, query in insert_queries.items():
            cursor.executemany(query, conf[table])
        conn.commit()
    except KeyError as e:
        del_db(db_loc)
    finally:
        conn.close()
