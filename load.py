from os import listdir
from os.path import isfile, join
from sys import argv
from src.billing import BILLING_DB
from src.model.bank_statement import BankStatement
from src.statement.boa import BankOfAmerica_Credit


def load(path):
    onlyfiles = [join(pdf_path, f) for f in listdir(path) if isfile(join(path, f))]
    db = BILLING_DB(__file__)
#     db.resetdb()
    for pdf in onlyfiles:
        boa = BankOfAmerica_Credit(pdf)
        db.import_statement(boa)


if __name__ == '__main__':
    pdf_path = "/Users/yuhangzhan/Git/statement_reader/data/pdf/boa/credit"
    load(pdf_path)
    # db = BILLING_DB(__file__)
