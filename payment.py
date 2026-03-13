class Account:
    def __init__(self, account_number: str, account_name: str, balance: float):
        self.__number = account_number
        self.__name = account_name
        self.__balance = balance

    @property
    def number(self): return self.__number
    @property
    def name(self): return self.__name
    @property
    def balance(self): return self.__balance

    def decrease(self, amount: float) -> bool:
        if self.__balance >= amount:
            self.__balance -= amount
            return True
        return False

    def increase(self, amount: float):
        self.__balance += amount

class Bank:
    def __init__(self):
        self.__accounts = {}

    def create_account(self, account_number: str, account_name: str, balance: float) -> Account:
        acc = Account(account_number, account_name, balance)
        self.__accounts[account_number] = acc
        return acc

    def pay(self, account_number: str, amount: float) -> bool:
        if account_number in self.__accounts:
            return self.__accounts[account_number].decrease(amount)
        return False

    def refund(self, account_number: str, amount: float):
        if account_number in self.__accounts:
            self.__accounts[account_number].increase(amount)