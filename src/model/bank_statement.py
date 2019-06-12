class BankStatment():
    """ bank base """

    def __init__(self, file_path):
        self.file_path = file_path
        self.bank_name = None
        self.account_type = None
        self.file_name = file_path.rsplit('/')[-1]
        self.summary = None
        self.transactions = None

    def get_summary(self):
        """ overwrite this func 
            return dict :
            {
                'account_type': <text>, (credit or debit)
                'account': <int/str>, (last 4 digit is fine)
                ...
            }
        """
        raise NotImplementedError()

    def get_transaction(self):
        """ overwrite this func 
            return dict:
            {
                'transaction_type':[
                    {
                        'type': <TEXT>,
                        'transaction_date': <YYYY-MM-DD>,
                        'posting_date': <YYYY-MM-DD>,
                        'reference_number': <INT>,
                        'account_number': <INT>,
                        'amount': <FLOAT>,
                        'description': <TEXT>
                    }
                ]
            }
        """
        raise NotImplementedError()
