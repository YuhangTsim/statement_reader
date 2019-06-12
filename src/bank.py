''' BOA statement parser '''
import re
from datetime import datetime
from src.utility.PdfToString import pdf_to_string
from src.utility.utils import init_logger, func_recorder

from src.model.credit_statement import CreditStatement

# todo: add exception control
# todo: log func


class BankOfAmerica_Credit(CreditStatement):
    ''' Class for BOA statement'''

    def __init__(self, file_path):
        super().__init__(file_path)
        self.log = init_logger('BOA')
        # self.log.info('BOA credit job start')

        self.previous_balance = None
        self.payments_and_other_credits = None
        self.close_date = None
        self.close_yesr = None

        with open(self.file_path, 'rb') as file:
            self.raw_pdf_string = pdf_to_string(file)
        self.delimiter = self.__get_delimiter()
        self.summary, self.close_date = self.get_summary(self.raw_pdf_string, self.delimiter)
        self.transactions = self.get_transactions(self.raw_pdf_string)
        # self.log.info('BOA credit job finished')

    def get_summary(self, file_string, page_delimiter):
        """ retrieve details in account summary """
        account_summary = {}
        account_summary['account_type'] = ['credit']
        account_summary['account'] = re.findall('Account#[\s\d{4}]+\s(\d{4})', file_string)

        first_page = file_string.split(page_delimiter)[1].strip()
        account_summary["previous_balance"] = re.findall(
            r"Previous Balance\s+(-)?\$([\d|,]+\.\d+)\s", first_page)
        account_summary["payments_and_other_credits"] = re.findall(
            r"Payments and Other Credits\s+(-)?\$([\d|,]+\.\d+)\s", first_page)
        account_summary['fees_charged'] = re.findall(
            r"Fees Charged\s+(-)?\$([\d|,]+\.\d+)\s", first_page
        )
        account_summary['interest_charged'] = re.findall(
            r"Interest Charged\s+(-)?\$([\d|,]+\.\d+)\s", first_page
        )
        account_summary['new_balance_total'] = re.findall(
            r"New Balance Total\s+(-)?\$([\d|,]+\.\d+)\s", first_page
        )
        account_summary['total_credit_line'] = re.findall(
            r"Total Credit Line\s+(-)?\$([\d|,]+\.\d+)\s", first_page
        )
        state_close_date = re.findall(
            r"Statement Closing Date\s+(\d{2}/\d{2}/\d{4})", first_page
        )[0]
        state_close_date = datetime.strptime(state_close_date, '%m/%d/%Y')
        # print(account_summary)
        return self.get_summery_detail(account_summary), state_close_date

    def get_summery_detail(self, details_list):
        """ regex result to numeric """
        res = {}
        for line in details_list:
            details = details_list[line][0]
            if details:
                if line in ('account', 'account_type'):
                    res[line] = details
                    continue
                neg = details[0]
                num = details[1].replace(',', '')
                res[line] = float(num) if not neg else -float(num)
        return res

    def get_transactions(self, file_string):
        ''' retrive all info from a statement '''
        parts = ['payment', 'purchase', 'fee', 'interest']
        transactions = {}
        for part in parts:
            if part == 'fee' and self.summary['fees_charged'] == 0:
                continue
            elif part == 'interest' and self.summary['interest_charged'] == 0:
                continue
            transactions[part] = self.get_transactions_detail(file_string, part)
        return transactions

    def get_transactions_detail(self, file_string, part='payment'):
        ''' retrive detail for each transaction  '''
        trans_parts = {
            'payment': ('TOTAL PAYMENTS AND OTHER CREDITS FOR THIS PERIOD', 'Payments and Other Credits'),
            'purchase': ('TOTAL PURCHASES AND ADJUSTMENTS FOR THIS PERIOD', 'Purchases and Adjustments'),
            'fee': ('TOTAL FEES FOR THIS PERIOD', 'Fees'),
            'interest': ('TOTAL INTEREST CHARGED FOR THIS PERIOD', 'Interest Charged')
        }
        page_delimiter = trans_parts[part]

        transactions = self.get_transaction_page(file_string, part)

        transactions = transactions.split('\n')
        trans_details = self.get_trans_details(transactions, part)

        total = self.get_total(file_string.split(page_delimiter[0])[1], part)

        if self.valid_amount(trans_details, total):
            return trans_details
        else:
            # TODO: add reminder for inconsistence record parsing
            self.log.error(
                f'Fail to validate ammount in {part}, Total : {total}')
            self.log.error(f'Error transactions:\n {trans_details} ')

    def get_transaction_page(self, file_string, part='payment'):
        """ parsing string for transactions part """

        trans_parts = {
            'payment': ('TOTAL PAYMENTS AND OTHER CREDITS FOR THIS PERIOD', 'Payments and Other Credits'),
            'purchase': ('TOTAL PURCHASES AND ADJUSTMENTS FOR THIS PERIOD', 'Purchases and Adjustments'),
            'fee': ('TOTAL FEES FOR THIS PERIOD', '  Fees'),
            'interest': ('TOTAL INTEREST CHARGED FOR THIS PERIOD', 'Interest Charged')
        }
        page_delimiter = trans_parts[part]

        transaction_pages_temp = file_string.split(page_delimiter[0])[0]
        transaction_pages_temp = transaction_pages_temp.split(
            page_delimiter[1], 2)
        transactions_pages = transaction_pages_temp[-1]
        return transactions_pages

    def get_trans_details(self, transactions, part='payment'):
        """ raw line to value """
        trans_result = []
        for line in transactions:  # TODO: can not parse full info on multi-line transaction
            if not line:
                continue
            fields = {}
            fields['types'] = part
            fields['transaction_date'] = self.retrive_regex(
                re.findall(r'(\d+/\d+)', line), 0)
            # fields['transaction_date'], line = self.regex_handler(
            #     line, r'(\d+/\d+)', 0)
            fields['posting_date'] = self.retrive_regex(
                re.findall(r'(\d+/\d+)', line), 1)
            fields['reference_number'] = self.retrive_regex(
                re.findall(r'\d{4}', line), -2)
            fields['account_number'] = self.account_regex_handler(line)
            fields['amount'] = self.retrive_regex(
                re.findall(r'-?[\d|,]+\.\d{2}', line), 0)

            line_text = line
            for field in fields:
                if fields[field]:
                    line_text = line_text.replace(fields[field], '').strip()
            fields['description'] = line_text

            fields['reference_number'] = int(
                fields['reference_number']) if fields['reference_number'] else None
            fields['account_number'] = int(
                fields['account_number']) if fields['account_number'] else None
            fields['amount'] = float(fields['amount'].replace(
                ',', '')) if fields['amount'] else None
            if fields['amount'] and fields['transaction_date']:
                trans_result.append(fields)
            if self.close_date:
                fields['transaction_date'] = self.add_year_to_datefield(
                    fields['transaction_date'])
                fields['posting_date'] = self.add_year_to_datefield(
                    fields['posting_date'])
        return trans_result

    def get_total(self, file_string, part='payment'):
        """ raw line to value """
        total = re.findall(r'[-|$]{,2}[\d|,]+\.\d{2}',
                           file_string)[0].replace('$', '').replace(',', '')
        return float(total)

    def valid_amount(self, transactions, total):
        """ valiate transaction amount """
        trans_total = sum([tran['amount'] for tran in transactions])
        trans_total = round(trans_total, 2)
        if trans_total == total:
            res = True
        else:
            res = False
            self.log.error(f'Error total: {trans_total}')
        return res

    def retrive_regex(self, findall_res, idx):
        ''' return regex value if exist'''
        if findall_res:
            try:
                return findall_res[idx]
            except Exception as e:
                print('----')  # TODO: add excpetion control

    # def regex_handler(self, transaction, regex, idx): # ! Deprecated method, fix needed
    #     ''' general field handler
    #     '''
    #     res = self.retrive_regex(re.findall(regex, transaction), idx)
    #     new_transaction = transaction.replace(res, '', 1)
    #     return res, new_transaction

    def account_regex_handler(self, transaction):
        ''' func to parse account number in transactions, 
            1. deal with "Virtual Card" value in account number field #todo : to fix -- current method will leave "Virtual Card" in description
        '''
        res = ''
        if "Virtural Card" in transaction:
            res = "-1111"
            # new_transaction = transaction.replace("Virtural Card", '', 1)
        else:
            res = self.retrive_regex(re.findall(r'\d{4}', transaction), -1)
            # res, new_transaction = self.regex_handler(transaction, r'\d{4}', -1)
        # return res, new_transaction
        return res

    def add_year_to_datefield(self, datefield):
        """ Add year to transaction data & posting date in transaction"""
        if not self.close_yesr and self.close_date:
            self.close_yesr = str(self.close_date.year)
        if datefield:
            res = datefield + '/' + self.close_yesr
            res = datetime.strptime(res, '%m/%d/%Y').strftime('%Y-%m-%d')
            return res

    def __get_delimiter(self):
        res = re.findall('P.O. Box 15019\n\s+(\w+\s\w+)\n', self.raw_pdf_string)
        assert res
        return res[0]


if __name__ == '__main__':
    fpath = './../data/pdf/boa/credit/eStmt_2019-02-28.pdf'
    boa = BankOfAmerica_Credit(fpath)
    # print(boa.statement_transaction)
    print(boa.summary)
