from src.model.bank_statement import BankStatment


class CreditStatement(BankStatment):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def get_summary(self):
            """ overwrite this func 
            return dict :
            {
                'account_type': <text>, (credit or debit)
                'account': <int/str>, (last 4 digit is fine)
                'total_credit_line': <float>
                ...
            }
        """
            raise NotImplementedError()
