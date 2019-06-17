from src.utility.PdfToString import pdf_to_string


class BankStatement():
    """ bank base """

    def __init__(self, file_path, path_delimiter='/'):
        self.file_path = file_path
        self.bank_name = None
        self.account_type = None
        self.file_name = file_path.split(path_delimiter)[-1]
        self.summary = None
        self.transactions = None

        self.raw_pdf_string = self.__get_raw_string()

    def __get_raw_string(self):
        with open(self.file_path, 'rb') as file:
            raw_pdf_string = pdf_to_string(file)
        return raw_pdf_string

    def get_summary(self):
        """ overwrite this func 
            return dict to self.summary:
            {
                'account_type': <text>, (credit or debit)
                'account': <int/str>, (last 4 digit is fine)
                ...
            }
        """
        raise NotImplementedError()

    def get_transaction(self):
        """ overwrite this func 
            return dict to self.transactions: <field order is important !!!>
            {
                'transaction_type':[
                    {
                        'type': <TEXT>,
                        'transaction_date': <YYYY-MM-DD>,
                        'posting_date': <YYYY-MM-DD> or 'Null',
                        'reference_number': <INT> or 'Null',
                        'account_number': <INT>,
                        'amount': <FLOAT>,
                        'description': <TEXT>
                    }
                ]
            }
        """
        raise NotImplementedError()


class CreditStatement(BankStatement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_type = 'credit'

        def get_summary(self):
            """ overwrite this func 
            return dict to self.summary:
            {
                'account_type': <text>, (credit or debit)
                'account': <int/str>, (last 4 digit is fine)
                'total_credit_line': <float>
                ...
            }
        """
            raise NotImplementedError()


class DebitStatement(BankStatement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_type = 'debit'

        def get_summary(self):
            """ overwrite this func 
            return dict to self.summary:
            {
                'account_type': <text>, (credit or debit)
                'account': <int/str>, (last 4 digit is fine)
                ...
            }
        """
            raise NotImplementedError()
