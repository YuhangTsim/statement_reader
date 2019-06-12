from src.model.bank_statement import BankStatment


class DebitStatement(BankStatment):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_type = 'debit'

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
