"""
database class
"""
import os
import sqlite3
import subprocess
from src.utility.utils import get_project_path, import_conf, import_conf_query


class BILLING_DB():
    """ """

    def __init__(self, project_path, db_path='/data/db/billing.db'):
        self.DEFAULT_CONFIG_PATH = '/conf/db_default_config.json'
        self.PERSONAL_CATE_CONFIG_PATH = '/conf/personal_category_config.json'
        self.CREATE_DB_SCRIPT_PATH = '/src/database/create_tables.sql'
        self.INSERT_CONF_SCRIPT_PATH = '/src/database/insert_init_setting.sql'
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
        default_conf = import_conf(self.project_path + self.DEFAULT_CONFIG_PATH)
        personal_cate_conf = import_conf(self.project_path + self.PERSONAL_CATE_CONFIG_PATH)
        conf = {**default_conf, **personal_cate_conf}
        insert_queries = import_conf_query(self.project_path + self.INSERT_CONF_SCRIPT_PATH)

        try:
            with open(self.project_path + self.CREATE_DB_SCRIPT_PATH, 'r') as f:
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

    def import_statement(self, bank_statement):
        """ insert statement info into db """
        self.__insert_new_card(bank_statement.summary)
        self.__import_transaction(bank_statement.transactions)
        self.conn.commit()

    def __import_transaction(self, transactions):
        """ insert transaction into db """
        INSERT_TRANS = "INSERT INTO raw_transactions (trans_type, transaction_date, post_date, ref_number, account_number, amount, DESCRIPTION) VALUES (?, ?, ?, ?, ?, ?, ?)"

        for _, trans in transactions.items():
            trans = [self.__flatten_transaction(tran) for tran in trans]
            self.cursor.executemany(INSERT_TRANS, trans)

    def __flatten_transaction(self, transaction):
        assert isinstance(transaction, dict)
        return tuple([value for _, value in transaction.items()])

    def __insert_new_card(self, bank_statement_summary):
        """ insert new card into db """
        card = int(bank_statement_summary['account'])

        self.cursor.execute('select card_number from card')
        exist_cards = [i[0] for i in list(self.cursor.fetchall())]
        if card in exist_cards:
            return
        card_id = len(exist_cards)+1
        card_type_id = self.__get_card_type_id(bank_statement_summary['account_type'])
        total_credit_line = bank_statement_summary['total_credit_line']
        query = "INSERT INTO card (card_id, card_type_id, card_number, creadit_amount) VALUES (?, ?, ?, ?)"
        self.cursor.execute(query, (card_id, card_type_id, card, total_credit_line))

    def __get_card_type_id(self, card_type):
        type_id = {
            'debit': 1,
            'credit': 2
        }
        return type_id[card_type]

    def __db_exist(self):
        """check db existence"""
        return os.path.isfile(self.db_loc)

    def __drop(self):
        subprocess.run(['rm', self.db_loc])

    def resetdb(self):
        """ reset db """
        subprocess.run(['rm', self.db_loc])
        self.init_db()

    def test(self):
        """ testing everything """
        pass
