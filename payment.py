class Account:
    def __init__(self, account_id: str, balance: float):
        self.__id = account_id
        self.__balance = balance

    @property
    def id(self): return self.__id
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

    def create_account(self, account_id: str, balance: float) -> Account:
        acc = Account(account_id, balance)
        self.__accounts[account_id] = acc
        return acc

    def pay(self, account_id: str, amount: float) -> bool:
        if account_id in self.__accounts:
            return self.__accounts[account_id].decrease(amount)
        return False

    def refund(self, account_id: str, amount: float):
        if account_id in self.__accounts:
            self.__accounts[account_id].increase(amount)