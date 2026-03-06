import datetime
from pydantic import BaseModel
from fastapi import FastAPI
from abc import ABC, abstractmethod
from typing import Optional

app = FastAPI()


class Account:
    def __init__(self, name, balance, account_id): 
        self.__name = name
        self.__balance = balance
        self.__id = account_id

    def decrease_balance(self, amount):
        if self.__balance >= amount:
            self.__balance -= amount
            return True
        return False
    
    def get_id(self):
        return self.__id

class Bank:
    def __init__(self, name):
        self.__name = name
        self.__account_list = []
    
    def add_account(self, account):
        self.__account_list.append(account)


    def payment(self, account_id, amount):
        
        target_account = None
        for acc in self.__account_list:
            if acc.get_id() == account_id:
                target_account = acc
                break
        if target_account:
            return target_account.decrease_balance(amount)
        else:
            return False 


class PaymentGateway:
    def __init__(self, account_id, amount):
        self.__account_id = account_id
        self.__amount = amount

    
    def pay(self, bank):
        return bank.payment(self.__account_id, self.__amount)


class Order:
    def __init__(self, goods_name, values, price_per_unit):
        self.__goods_name = goods_name
        self.__values = values
        self.__price_per_unit = price_per_unit
        self.__total = 0

    def calculate_total(self, discount_amount=0):
        self.__total = (self.__price_per_unit * self.__values) - discount_amount
        if self.__total < 0: self.__total = 0
        return self.__total


    def pay(self, bank, gateway):

        return gateway.pay(bank)
    
    def success(self):
        return True


class Goods(ABC):
    def __init__(self, name, values: int, price):
        self._name = name
        self._values = values
        self._price = price

    def get_name(self):
        return self._name
    
    def get_price(self):
        return self._price

    def check_values(self, amount_needed):
        return self._values >= amount_needed

    def clearstock(self, amount):
        self._values -= amount
        return "success"

class Popcorn(Goods):
    def __init__(self, name, values: int, price, flavor):
        super().__init__(name, values, price)
        self._flavor = flavor

class Cineplex:
    def __init__(self, name):
        self.__name = name
        self.__stock = []

    def add_popcorn(self, name, values: int, price, flavor):
        popcorn = Popcorn(name, values, price, flavor)
        self.__stock.append(popcorn)

    def search_goods_stock(self, goods_name, amount_needed):
        for item in self.__stock:
            if item.get_name() == goods_name and item.check_values(amount_needed):
                return item
        return None
    
    def get_cineplex_name(self):
        return self.__name


class User:
    def __init__(self, name, member_id):
        self._name = name
        self._member_id = member_id

    def get_member_id(self):
        return self._member_id
    
class Member(User):
    def __init__(self, name, birthday, member_id, registered_date, email=None, phone_number=None):
        super().__init__(name, member_id) 
        self._birthday = birthday

class Coupon:
    def __init__(self, coupon_id, name, discount):
        self._coupon_id = coupon_id
        self._discount = discount

    def get_discount(self):
        return self._discount
    
    def get_coupon_id(self):
        return self._coupon_id

class DiscountCoupon(Coupon):
    def __init__(self, coupon_id, name, discount):
        super().__init__(coupon_id, name, discount)


class JamorPlinicex:
    def __init__(self):
        self.__member_list = []
        self.__coupon_list = []
        self.__cineplex_list = []
    
    def add_cineplex(self, name):
        cineplex = Cineplex(name)
        self.__cineplex_list.append(cineplex)
        return cineplex

    def register_member(self, name, birthday, member_id, registered_date, email=None, phone_number=None):
        member = Member(name, birthday, member_id, registered_date, email, phone_number)
        self.__member_list.append(member)
    
    def add_discount_coupon(self, coupon_id, name, discount):
        discount_coupon = DiscountCoupon(coupon_id, name, discount)
        self.__coupon_list.append(discount_coupon)  

    def find_cineplex(self, cineplex_name):
        for i in self.__cineplex_list:
            if cineplex_name == i.get_cineplex_name():
                return i
        return None

    def find_member(self, user_id):
        for i in self.__member_list:
            if user_id == i.get_member_id():
                return i
        return None


    def order_goods(self, goods_name, values, user_id, bank, account_id, cineplex_name, coupon_id=None):


        member = self.find_member(user_id)
        if not member:
            return "Member not found"


        cineplex = self.find_cineplex(cineplex_name)
        if not cineplex:
            return "Cineplex not found"
        

        target_good = cineplex.search_goods_stock(goods_name,values)

        if not target_good:
            return "Out of stock or Not enough items"


        discount_amount = 0
        if coupon_id:
            for coupon in self.__coupon_list:
                if coupon.get_coupon_id() == coupon_id:
                    discount_amount = coupon.get_discount()
        

        order = Order(goods_name, values, target_good.get_price())
        total_price = order.calculate_total(discount_amount)

        gateway = PaymentGateway(account_id, total_price)
        

        if order.pay(bank, gateway):
 
            order.success()
            target_good.clearstock(values)
            return f"create_order success, Total Paid: {total_price}"
        else:
   
            return "payment failed"

#------------------------------------------------------------------------------------------------------

system = JamorPlinicex()
cineplex = system.add_cineplex("C") # Cineplex Name: "C"
cineplex.add_popcorn("Popcorn", 100, 50, "Cheese") # Goods: "Popcorn"
system.register_member("J", "01-01-1990", "M001", "2023-01-01") # User ID: "M001"
system.add_discount_coupon("C10", "Discount 10", 10) # Coupon: "C10"

# 2. Setup Bank & Account
kbank = Bank("KB")
my_account = Account("J", 500, "A123") # Account ID: "A123"
kbank.add_account(my_account)

# =======================================================
#  API Endpoint
# =======================================================

@app.post("/order-goods")
def api_order_goods(
    goods_name: str,
    quantity: int,
    user_id: str,
    account_id: str,       
    cineplex_name: str,
    coupon_id: Optional[str] = None
):
    # ตอนนี้ system และ kbank จะมีข้อมูลครบถ้วนแล้ว
    result = system.order_goods(
        goods_name=goods_name,
        values=quantity,
        user_id=user_id,
        bank=kbank,          
        account_id=account_id,
        cineplex_name=cineplex_name,
        coupon_id=coupon_id
    )
    
    return {"result": result}