from typing import List, Optional
from enums import OrderStatus


class Account:
    def __init__(self, name: str, balance: float, account_id: str):
        self.__name    = name
        self.__balance = balance
        self.__id      = account_id

    def get_id(self) -> str:
        return self.__id

    def decrease_balance(self, amount: float) -> bool:
        if self.__balance >= amount:
            self.__balance -= amount
            return True
        return False

    def increase_balance(self, amount: float) -> bool:
        self.__balance += amount
        return True


class Bank:
    def __init__(self, name: str):
        self.__name         = name
        self.__account_list: List[Account] = []

    @property
    def name(self) -> str:
        return self.__name

    def create_account(self, name: str, account_id: str, balance: float) -> Account:
        account = Account(name, balance,account_id)
        self.__account_list.append(account)
        return account

    def _find_account(self, account_id: str) :
        for acc in self.__account_list:
            if acc.get_id() == account_id:
                return acc
        return None

    def payment(self, account_id: str, amount: float) -> bool:
        account = self._find_account(account_id)
        if not account : return "Account not found"
        return account.decrease_balance(amount) 
    
    def refund(self, account_id: str, amount: float) -> bool:
        account = self._find_account(account_id)
        return account.increase_balance(amount) if account else False

class PaymentGateway:
    def __init__(self, account_id: str, amount: float, bank:str):
        self.__account_id = account_id
        self.__amount     = amount
        self.__bank = bank

    def pay(self) -> bool:
        return self.__bank.payment(self.__account_id, self.__amount)

class Order:
    def __init__(self, order_id: str, goods_name: str, values: int,
                 account_id: str, total_paid: float,
                 coupon_id: str = None,
                 status: OrderStatus = OrderStatus.COMPLETED):
        self.__order_id   = order_id
        self.__goods_name = goods_name
        self.__values     = values
        self.__account_id = account_id
        self.__total_paid = total_paid
        self.__coupon_id  = coupon_id
        self.__status     = status

    def get_order_id(self) -> str:
        return self.__order_id

    def get_status(self) -> str:
        return self.__status.value if isinstance(self.__status, OrderStatus) else self.__status

    def update_status(self, status: OrderStatus):
        self.__status = status
        return "success"

    def get_payment_details(self):
        return self.__account_id, self.__total_paid

    def get_items(self):
        return self.__goods_name, self.__values

    def get_used_coupon(self) -> Optional[str]:
        return self.__coupon_id

    def pay(self, bank: Bank, gateway: PaymentGateway) -> bool:
        return gateway.pay(bank)

    def pay_direct(self) -> bool:
        """จ่ายเงินโดยไม่ผ่าน Bank — คืน True เสมอ (สำหรับระบบที่ไม่มี Bank)"""
        return True
