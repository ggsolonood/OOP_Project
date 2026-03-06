from fastapi import FastAPI
from abc import ABC
from enum import Enum

app = FastAPI()

class OrderStatus(Enum):
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"

class Account:
    def __init__(self, name, account_id, balance):
        self.__name = name
        self.__id = account_id
        self.__balance = balance

    def get_id(self):
        return self.__id

    def increase_balance(self, amount):
        self.__balance += amount  
        return True

class Bank:
    def __init__(self, name):
        self.__name = name
        self.__account_list = []
    
    def create_account(self, name, account_id, balance):
        account = Account(name, account_id, balance)
        self.__account_list.append(account)
        return account

    def check_account(self, account_id):
        for acc in self.__account_list:
            if acc.get_id() == account_id:
                return acc
        return None

    def refund(self, account_id, amount):
        account = self.check_account(account_id)
        if account is not None:
            return account.increase_balance(amount) 
        return False



class Order:
    def __init__(self, order_id, goods_name, values, account_id, total_paid, coupon_id=None, status=OrderStatus.COMPLETED):
        self.__order_id = order_id
        self.__status = status 
        self.__goods_name = goods_name
        self.__values = values
        self.__account_id = account_id 
        self.__total_paid = total_paid
        self.__coupon_id = coupon_id
  
    def update_status(self, status: OrderStatus):
        self.__status = status 
        return "success"
    
    def get_status(self):
        return self.__status.value if isinstance(self.__status, OrderStatus) else self.__status

    def get_order_id(self):
        return self.__order_id

    def get_payment_details(self):
        return self.__account_id, self.__total_paid

    def get_items(self):
        return self.__goods_name, self.__values

    def get_used_coupon(self):
        return self.__coupon_id


class Goods(ABC):
    def __init__(self, name, values: int):
        self._name = name
        self._values = values

    def get_name(self):
        return self._name

    def restore_stock(self, amount):
        self._values += amount 
        return "success"

class Popcorn(Goods):
    def __init__(self, name, values: int, flavor):
        super().__init__(name, values)
        self._flavor = flavor


class Cineplex:
    def __init__(self, name):
        self.__name = name
        self.__stock = []

    def get_cineplex_name(self):
        return self.__name

    def search_goods_stock(self, goods_name):
        for item in self.__stock:
            if item.get_name() == goods_name:
                return item
        return None

class Coupon:
    def __init__(self, coupon_id):
        self._coupon_id = coupon_id
        self._is_used = True 

    def get_coupon_id(self):
        return self._coupon_id

    def update_status(self, status):
        if status == "Available":
            self._is_used = False
        return "success"

class DiscountCoupon(Coupon):
    pass

class User:
    def __init__(self, member_id):
        self._member_id = member_id

    def get_member_id(self):
        return self._member_id
    
class Member(User):
    pass

class JamorPlinicex:
    def __init__(self, bank: Bank):
        self.__bank = bank 
        self.__member_list = []
        self.__order_list = []   
        self.__cineplex_list = []
        self.__coupon_list = []

    def find_member(self, user_id):
        for member in self.__member_list:
            if member.get_member_id() == user_id:
                return member
        return None
    
    def find_order(self, order_id):
        for order in self.__order_list:
            if order.get_order_id() == order_id:
                return order
        return None

    def find_cineplex(self, cineplex_name):
        for c in self.__cineplex_list:
            if c.get_cineplex_name() == cineplex_name:
                return c
        return None

    def cancel_order(self, order_id, user_id, cineplex_name):
        member = self.find_member(user_id)
        if not member:
            return "Member not found"

        order = self.find_order(order_id)
        if not order:
            return "Order not found"

        current_status = order.get_status()

        if current_status == OrderStatus.CANCELLED.value:
            return "Order is already cancelled"
            
        if current_status == OrderStatus.REFUNDED.value:
            return "Order has already been refunded"

     
        if current_status == OrderStatus.COMPLETED.value:
            account_id, total_paid = order.get_payment_details()
            
           
            refund_success = self.__bank.refund(account_id, total_paid)
            
            if refund_success:
                item_text, coupon_text = self.restore_order_resources(order, cineplex_name)
                order.update_status(OrderStatus.CANCELLED)
                
               
                return f"Cancel success, Refund {total_paid} THB to account {account_id}. Restored: {item_text}, Coupon: {coupon_text}."
            else:
                return "Refund failed"

  
    def restore_order_resources(self, order, cineplex_name):
        goods_name, values = order.get_items()
        cineplex = self.find_cineplex(cineplex_name)
        
        restored_item_text = f"{values} x {goods_name}"
        restored_coupon_text = "None"

        if cineplex:
            target_good = cineplex.search_goods_stock(goods_name)
            if target_good:
                target_good.restore_stock(values)
        
        coupon_id = order.get_used_coupon()
        if coupon_id:
            for coupon in self.__coupon_list:
                if coupon.get_coupon_id() == coupon_id:
                    coupon.update_status("Available")
                    restored_coupon_text = str(coupon_id)
                    break
        
        return restored_item_text, restored_coupon_text

# ==========================================
# Setup Mock Data & System
# ==========================================
main_bank = Bank("KBank")
main_account = main_bank.create_account("John Doe", "ACC-001", balance=1000) 

system = JamorPlinicex(main_bank)

system._JamorPlinicex__member_list.append(Member("USER-001"))

cineplex = Cineplex("Cineplex-A")
popcorn = Popcorn("Popcorn Cheese", values=98, flavor="Cheese") 
cineplex._Cineplex__stock.append(popcorn)
system._JamorPlinicex__cineplex_list.append(cineplex)

coupon = DiscountCoupon("DISC-50")
system._JamorPlinicex__coupon_list.append(coupon)

mock_order = Order("ORD-999", "Popcorn Cheese", 2, "ACC-001", 150, "DISC-50")
system._JamorPlinicex__order_list.append(mock_order)

# ==========================================
# FastAPI Endpoint 
# ==========================================

@app.post("/cancel-order")
def cancel_order_api(
    order_id: str,
    user_id: str,
    cineplex_name: str
):
    result = system.cancel_order(
        order_id=order_id, 
        user_id=user_id,
        cineplex_name=cineplex_name
    )
    return result