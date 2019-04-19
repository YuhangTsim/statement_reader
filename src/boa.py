''' BOA statement parser '''
import re
from datetime import datetime
from PdfToString import pdf_to_string
from utils import init_logger, func_recorder

# todo: add exception control
# todo: log func


class BOA_CREDIT():
    ''' Class for BOA statement'''

    def __init__(self, file_path):
        self.file_path = file_path
        self.log = init_logger('BOA')
        self.log.info('BOA credit job start')

        self.previous_balance = None
        self.payments_and_other_credits = None
        self.summary = None
        self.close_date = None
        self.close_yesr = None

        with open(self.file_path, 'rb') as file:
            file_string = pdf_to_string(file)
        self.statement_info = self.get_credit_statement_info(file_string)
        self.log.info('BOA credit job finished')

    def get_account_summary(self, file_string, page_delimiter='YUHANG ZHAN'):
        """ retrieve details in account summary """
        account_summary = {}

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
                neg = details[0]
                num = details[1].replace(',', '')
                res[line] = float(num) if not neg else -float(num)
        return res

    @func_recorder
    def get_credit_statement_info(self, file_string):
        ''' retrive all info from a statement '''
        self.summary, self.close_date = self.get_account_summary(file_string)
        parts = ['payment', 'purchase', 'fee', 'interest']
        transactions = {}
        for part in parts:
            if part == 'fee' and self.summary['fees_charged'] == 0:
                continue
            elif part == 'interest' and self.summary['interest_charged'] == 0:
                continue
            transactions[part] = self.get_transactions(file_string, part)
        return transactions

    def get_transactions(self, file_string, part='payment'):
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
            page_delimiter
            [1],
            2)
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
            return res


if __name__ == '__main__':
    fpath = './../data/pdf/boa/credit/eStmt_2019-02-28.pdf'
    boa = BOA_CREDIT(fpath)
    print(boa.statement_info)
    # print(boa.summary)
