from enums import OrderStatus


class Account:
    def __init__(self, name, balance, account_id):
        self.__name = name
        self.__balance = balance
        self.__id = account_id

    def get_id(self):
        return self.__id

    def decrease_balance(self, amount):
        if self.__balance >= amount:
            self.__balance -= amount
            return True
        return False

    def increase_balance(self, amount):
        self.__balance += amount
        return True


class Bank:
    def __init__(self, name):
        self.__name = name
        self.__account_list = []

    def create_account(self, name, account_id, balance):
        account = Account(name, balance, account_id)
        self.__account_list.append(account)
        return account

    def _find_account(self, account_id):
        for acc in self.__account_list:
            if acc.get_id() == account_id:
                return acc
        return None

    def payment(self, account_id, amount):
        account = self._find_account(account_id)
        return account.decrease_balance(amount) if account else False

    def refund(self, account_id, amount):
        account = self._find_account(account_id)
        return account.increase_balance(amount) if account else False


class PaymentGateway:
    def __init__(self, account_id, amount):
        self.__account_id = account_id
        self.__amount = amount

    def pay(self, bank):
        return bank.payment(self.__account_id, self.__amount)


class Order:
    def __init__(self, order_id, goods_name, values, account_id, total_paid,
                 coupon_id=None, status=OrderStatus.COMPLETED):
        self.__order_id = order_id
        self.__goods_name = goods_name
        self.__values = values
        self.__account_id = account_id
        self.__total_paid = total_paid
        self.__coupon_id = coupon_id
        self.__status = status

    def get_order_id(self):
        return self.__order_id

    def get_status(self):
        return self.__status.value if isinstance(self.__status, OrderStatus) else self.__status

    def update_status(self, status: OrderStatus):
        self.__status = status
        return "success"

    def get_payment_details(self):
        return self.__account_id, self.__total_paid

    def get_items(self):
        return self.__goods_name, self.__values

    def get_used_coupon(self):
        return self.__coupon_id

    def pay(self, bank, gateway):
        return gateway.pay(bank)
