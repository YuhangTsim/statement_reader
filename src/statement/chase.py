''' Chase statement parser '''
import re
from datetime import datetime
from src.utility.PdfToString import pdf_to_string
from src.utility.utils import init_logger, func_recorder

from src.model.bank_statement import CreditStatement


class Chase_Credit(CreditStatement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bank_name = 'chase'

        self.__page_delimiter = self.__get_page_delimiter()
        self.open_date = None
        self.close_date = None

        self.summary = self.get_summary()
        self.transactions = self.get_transaction()

    def get_summary(self):
        account_summary = {}

        account_summary['account_type'] = ['credit']
        account_summary['account'] = re.findall('Account Number:[\s\d{4}]+(\d{4})\s', self.raw_pdf_string)

        first_page = self.raw_pdf_string.split(self.__page_delimiter)[0]
        account_summary['previous_balance'] = re.findall(
            r"Previous Balance\s+([-|+])?\$([\d|,]+\.\d+)\s", first_page)
        account_summary["payment_credits"] = re.findall(
            r"Payment, Credits\s+([-|+])?\$([\d|,]+\.\d+)\s", first_page)
        account_summary["purchases"] = re.findall(
            r"Purchases\s+([-|+])?\$([\d|,]+\.\d+)\s", first_page)
        account_summary['fees_charged'] = re.findall(
            r"Fees Charged\s+([-|+])?\$([\d|,]+\.\d+)\s", first_page
        )
        account_summary['interest_charged'] = re.findall(
            r"Interest Charged\s+([-|+])?\$([\d|,]+\.\d+)\s", first_page
        )
        account_summary['new_balance_total'] = re.findall(
            r"New Balance\s+([-|+])?\$([\d|,]+\.\d+)\s", first_page
        )
        account_summary['credit_line'] = re.findall(
            r"Credit Access Line\s+([-|+])?\$([\d|,]+[\.\d+]?)\s", first_page
        )

        open_date = re.findall(r"Opening/Closing Date\s+(\d{2}/\d{2}/\d{2})", first_page)[0]
        close_date = re.findall(r"Opening/Closing Date[\s|\d|\-|/]+(\d{2}/\d{2}/\d{2})", first_page)[0]
        self.open_date = datetime.strptime(open_date, "%m/%d/%y")
        self.close_date = datetime.strptime(close_date, "%m/%d/%y")

        return self.__get_summery_detail(account_summary)

    def get_transaction(self):
        parts = ['fee', 'purchase', 'payment']
        part_delimiters = {
            'payment': ['PAYMENTS AND OTHER CREDITS', 'PURCHASE'],
            'purchase': ['PURCHASE', 'FEES CHARGED'],
            'fee': ['FEES CHARGED', 'TOTAL FEES FOR THIS PERIOD']
        }
        transactions = {}
        text = self.raw_pdf_string.split('Totals Year-to-Date')[0]
        for part in parts:
            if part == 'fee' and self.summary['fees_charged'] == 0:
                part_delimiters[part][1] = ''
                continue
            elif part == 'payment' and self.summary['payment_credits'] == 0:
                part_delimiters[part][1] = ''
                continue
            elif part == 'purchase' and self.summary['purchases'] == 0:
                part_delimiters[part][1] = ''
                continue
            tran, text = self.__parse_transaction_part(text, part, part_delimiters[part])
            transactions[part] = tran
        return transactions

    def __parse_transaction_part(self, file_string, part, part_delimiters):
        delimiter = part_delimiters
        part_text = file_string.split(delimiter[0])[1]
        part_text = part_text.split(delimiter[1])[0] if delimiter[1] else part_text
        ret_text = file_string.split(delimiter[0])[0] if delimiter[1] else file_string

        trans = [line.strip() for line in part_text.split('\n') if line.strip()]
        trans = [self.__parse_tran_line(part, line) for line in trans if self.__parse_tran_line(part, line)]
        return trans, ret_text

    def __parse_tran_line(self, part, line):
        tran_date = self.__safe_regex('\d{2}/\d{2}', line, 0)
        amount = self.__safe_regex('-?[\d|,]+\.\d{2}', line,  -1)
        if not amount:
            return
        description = line.replace(tran_date, '').replace(amount, '').strip()
        transaction_date = self.__add_year_to_tran_date(tran_date)

        amount = amount.replace(',', '')

        res = {'type': part,
               'transaction_date': transaction_date,
               'posting_date': 'Null',
               'ref_number': 'Null',
               'account_number': int(self.summary['account']),
               'amount': float(amount) if amount[0] != '-' else -float(amount[1:]),
               'description': description}
        return res

    def __add_year_to_tran_date(self, raw_date):
        res = raw_date
        tran_month = int(raw_date[:2])
        year = self.close_date.year if self.close_date.month == tran_month else self.open_date.year
        return res + '/' + str(year)

    def __safe_regex(self, regex, text, idx):
        try:
            res = re.findall(regex, text)[idx]
        except:
            res = ''
        return res

    def __get_page_delimiter(self):
        res = re.findall('Mail to Chase Card Services at the address below:\s+(\w+\s\w+)\s', self.raw_pdf_string)
        assert res
        return res[0]

    def __get_summery_detail(self, details_list):
        """ regex result to numeric """
        res = {}
        for line in details_list:
            details = details_list[line][0]
            if details:
                if line in ('account', 'account_type'):
                    res[line] = details
                    continue
                neg = details[0] if details[0] == '-' else ''
                num = details[1].replace(',', '')
                res[line] = float(num) if not neg else -float(num)
        return res
