"""
database class
"""
import os
import sqlite3
import subprocess
from src.utility.utils import init_logger
from src.utility.utils import get_project_path, import_conf, import_conf_query

# TODO: add bank name to files table
# TODO: change to sqlalchemy


class BILLING_DB():
    """ """

    def __init__(self, project_path, db_path='/data/db/billing.db'):
        self.log = init_logger('DB')
        self.project_path = get_project_path(project_path)
        self.db_loc = self.project_path + db_path
        self.conn = None
        self.cursor = None

        if self.__db_exist():
            self.connect()
        else:
            self.init_db()

    def init_db(self):
        """init db if not exist"""
        DEFAULT_CONFIG_PATH = '/conf/db_default_config.json'
        PERSONAL_CATE_CONFIG_PATH = '/conf/personal_category_config.json'
        CREATE_DB_SCRIPT_PATH = '/src/database/create_tables.sql'
        INSERT_CONF_SCRIPT_PATH = '/src/database/insert_init_setting.sql'

        default_conf = import_conf(self.project_path + DEFAULT_CONFIG_PATH)
        personal_cate_conf = import_conf(self.project_path + PERSONAL_CATE_CONFIG_PATH)
        conf = {**default_conf, **personal_cate_conf}
        insert_queries = import_conf_query(self.project_path + INSERT_CONF_SCRIPT_PATH)

        try:
            with open(self.project_path + CREATE_DB_SCRIPT_PATH, 'r') as f:
                init_script = f.read()
            conn = sqlite3.connect(self.db_loc)
            cursor = conn.cursor()
            cursor.executescript(init_script)
            for table, query in insert_queries.items():
                cursor.executemany(query, conf[table])
            conn.commit()
            self.conn = conn
            self.cursor = cursor
        except KeyError as e:
            self.__drop()

    def connect(self):
        """ get db connection"""
        assert self.__db_exist(), "database does not exist"
        if not self.conn:
            self.conn = sqlite3.connect(self.db_loc)
            self.cursor = self.conn.cursor()
        return self.conn, self.cursor

    def import_statement(self, bank_statement, normailze=True):
        """ insert statement info into db """
        bank_name = bank_statement.bank_name
        file_name = bank_statement.file_name
        statement_type = bank_statement.account_type
        is_new_file = self.__insert_filename(bank_name, statement_type, file_name)
        if is_new_file:
            self.__insert_new_card(bank_name, bank_statement.summary)
            self.__insert_transaction(bank_statement.transactions)
            if normailze:
                self.__normalize_db()
            self.conn.commit()
            self.log.info(f"---- {bank_name} @ {statement_type} @ {file_name} imported")
            return
        self.conn.rollback()

    def __insert_transaction(self, transactions):
        """ insert transaction into db """
        INSERT_TRANS = "INSERT INTO staging_transactions (trans_type, transaction_date, post_date, ref_number, account_number, amount, DESCRIPTION) VALUES (?, ?, ?, ?, ?, ?, ?)"

        for _, trans in transactions.items():
            trans = [self.__flatten_transaction(tran) for tran in trans]
            self.cursor.executemany(INSERT_TRANS, trans)

    def __flatten_transaction(self, transaction):
        assert isinstance(transaction, dict), f"{transaction} if not a dict"
        return tuple([value for _, value in transaction.items()])

    def __insert_new_card(self, bank_name, bank_statement_summary):
        """ insert new card into db """
        card = int(bank_statement_summary['account'])

        self.cursor.execute('select card_number from card')
        exist_cards = [i[0] for i in list(self.cursor.fetchall())]
        if card in exist_cards:
            return
        card_id = len(exist_cards)+1
        bank_id = self.__get_bank_id(bank_name)
        card_type_id = self.__get_card_type_id(bank_statement_summary['account_type'])
        if bank_statement_summary['account_type'] == 'credit':
            total_credit_line = bank_statement_summary['credit_line']
            query = f"INSERT INTO card (card_id, bank_id, card_type_id, card_number, creadit_amount) VALUES (?, '{bank_id}', ?, ?, ?)"
            data = (card_id, card_type_id, card, total_credit_line)
        else:
            query = f"INSERT INTO card (card_id, bank_id, card_type_id, card_number) VALUES (?, 'bank_id', ?, ?)"
            data = (card_id, card_type_id, card)
        self.cursor.execute(query, data)

    def __insert_filename(self, bankname, statement_type, filename):
        QUERY = f"""
        select file_name 
        from files 
        where statement_type='{statement_type}' and bank='{bankname}';"""

        self.cursor.execute(QUERY)
        exist_files = [i[0] for i in list(self.cursor.fetchall())]
        if filename in exist_files:
            self.log.error(f"---- {bankname} @ {statement_type} @ {filename} exist.")
            return False
        else:
            self.cursor.execute(
                f"INSERT INTO files (bank, statement_type, file_name) values ('{bankname}', '{statement_type}', '{filename}')")
            return True

    def __get_card_type_id(self, card_type):
        type_id = {
            'debit': 1,
            'credit': 2
        }
        return type_id[card_type]

    def __get_bank_id(self, bankname):
        self.cursor.execute(f"select bank_id from bank where bank_name='{bankname}';")
        bank_id = self.cursor.fetchone()[0]
        return bank_id

    def __db_exist(self):
        """check db existence"""
        return os.path.isfile(self.db_loc)

    def __drop(self):
        subprocess.run(['rm', self.db_loc])

    def __normalize_db(self):
        ETL_SCRIPT_PATH = '/src/database/etl.sql'
        with open(self.project_path + ETL_SCRIPT_PATH, 'r') as f:
            etl_script = f.read()
        self.cursor.executescript(etl_script)

    def resetdb(self):
        """ reset db """
        subprocess.run(['rm', self.db_loc])
        self.init_db()

    def test(self):
        """ testing everything """
        pass
