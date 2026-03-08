from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
from fastmcp import FastMCP

# ==========================================
# Enums
# ==========================================

class OrderStatus(Enum):
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"

# ==========================================
# Account & Bank
# ==========================================

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

    def add_account(self, account):
        self.__account_list.append(account)

    def _find_account(self, account_id):
        for acc in self.__account_list:
            if acc.get_id() == account_id:
                return acc
        return None

    def payment(self, account_id, amount):
        account = self._find_account(account_id)
        if account:
            return account.decrease_balance(amount)
        return False

    def refund(self, account_id, amount):
        account = self._find_account(account_id)
        if account:
            return account.increase_balance(amount)
        return False

# ==========================================
# Payment
# ==========================================

class PaymentGateway:
    def __init__(self, account_id, amount):
        self.__account_id = account_id
        self.__amount = amount

    def pay(self, bank):
        return bank.payment(self.__account_id, self.__amount)

# ==========================================
# Goods
# ==========================================

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

    def restore_stock(self, amount):
        self._values += amount
        return "success"

class Popcorn(Goods):
    def __init__(self, name, values: int, price, flavor):
        super().__init__(name, values, price)
        self._flavor = flavor

# ==========================================
# Cineplex
# ==========================================

class Cineplex:
    def __init__(self, name):
        self.__name = name
        self.__stock = []

    def get_cineplex_name(self):
        return self.__name

    def add_popcorn(self, name, values: int, price, flavor):
        popcorn = Popcorn(name, values, price, flavor)
        self.__stock.append(popcorn)

    def search_goods_stock(self, goods_name, amount_needed=0):
        for item in self.__stock:
            if item.get_name() == goods_name:
                if amount_needed == 0 or item.check_values(amount_needed):
                    return item
        return None

# ==========================================
# Order
# ==========================================

class Order:
    def __init__(self, order_id, goods_name, values, account_id, total_paid, coupon_id=None, status=OrderStatus.COMPLETED):
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

    def calculate_total(self, price_per_unit, discount_amount=0):
        total = (price_per_unit * self.__values) - discount_amount
        return max(total, 0)

    def pay(self, bank, gateway):
        return gateway.pay(bank)

# ==========================================
# Coupon
# ==========================================

class Coupon:
    def __init__(self, coupon_id, name, discount):
        self._coupon_id = coupon_id
        self._name = name
        self._discount = discount
        self._is_used = False

    def get_coupon_id(self):
        return self._coupon_id

    def get_discount(self):
        return self._discount

    def update_status(self, status):
        self._is_used = (status != "Available")
        return "success"

class DiscountCoupon(Coupon):
    pass

# ==========================================
# User / Member
# ==========================================

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

# ==========================================
# JamorPlinicex (Main System)
# ==========================================

class JamorPlinicex:
    def __init__(self, bank: Bank):
        self.__bank = bank
        self.__member_list = []
        self.__order_list = []
        self.__cineplex_list = []
        self.__coupon_list = []
        self.__order_counter = 1

    def add_cineplex(self, name):
        cineplex = Cineplex(name)
        self.__cineplex_list.append(cineplex)
        return cineplex

    def register_member(self, name, birthday, member_id, registered_date, email=None, phone_number=None):
        member = Member(name, birthday, member_id, registered_date, email, phone_number)
        self.__member_list.append(member)

    def add_discount_coupon(self, coupon_id, name, discount):
        coupon = DiscountCoupon(coupon_id, name, discount)
        self.__coupon_list.append(coupon)

    def find_member(self, user_id):
        for m in self.__member_list:
            if m.get_member_id() == user_id:
                return m
        return None

    def find_order(self, order_id):
        for o in self.__order_list:
            if o.get_order_id() == order_id:
                return o
        return None

    def find_cineplex(self, cineplex_name):
        for c in self.__cineplex_list:
            if c.get_cineplex_name() == cineplex_name:
                return c
        return None

    # --- Feature 1: Order Goods ---
    def order_goods(self, goods_name, values, user_id, account_id, cineplex_name, coupon_id=None):
        member = self.find_member(user_id)
        if not member:
            return "Member not found"

        cineplex = self.find_cineplex(cineplex_name)
        if not cineplex:
            return "Cineplex not found"

        target_good = cineplex.search_goods_stock(goods_name, values)
        if not target_good:
            return "Out of stock or Not enough items"

        discount_amount = 0
        used_coupon_id = None
        if coupon_id:
            for coupon in self.__coupon_list:
                if coupon.get_coupon_id() == coupon_id:
                    discount_amount = coupon.get_discount()
                    used_coupon_id = coupon_id
                    coupon.update_status("Used")
                    break

        price_per_unit = target_good.get_price()
        total_price = max((price_per_unit * values) - discount_amount, 0)

        order_id = f"ORD-{self.__order_counter:04d}"
        self.__order_counter += 1

        order = Order(order_id, goods_name, values, account_id, total_price, used_coupon_id)
        gateway = PaymentGateway(account_id, total_price)

        if order.pay(self.__bank, gateway):
            target_good.clearstock(values)
            self.__order_list.append(order)
            return f"Order success | Order ID: {order_id} | Total Paid: {total_price} THB"
        else:
            return "Payment failed: Insufficient balance or invalid account."

    # --- Feature 2: Cancel Order ---
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
                item_text, coupon_text = self._restore_order_resources(order, cineplex_name)
                order.update_status(OrderStatus.CANCELLED)
                return f"Cancel success, Refund {total_paid} THB to account {account_id}. Restored: {item_text}, Coupon: {coupon_text}."
            else:
                return "Refund failed"

    def _restore_order_resources(self, order, cineplex_name):
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
# Setup & Mock Data
# ==========================================

kbank = Bank("KBank")
my_account = kbank.create_account("J", "A123", balance=500)

system = JamorPlinicex(kbank)

cineplex = system.add_cineplex("C")
cineplex.add_popcorn("Popcorn", 100, 50, "Cheese")

system.register_member("J", "01-01-1990", "M001", "2023-01-01")
system.add_discount_coupon("C10", "Discount 10", 10)


# ==========================================
# MCP Tools Setup (Replaces FastAPI Endpoints)
# ==========================================
mcp = FastMCP("JamorPlinicex Store System")

@mcp.tool()
def order_goods(
    goods_name: str,
    quantity: int,
    user_id: str,
    account_id: str,
    cineplex_name: str,
    coupon_id: str = None
) -> str:
    """
    ทำการสั่งซื้อสินค้าที่สาขาโรงภาพยนตร์
    - goods_name: ชื่อสินค้า (เช่น "Popcorn")
    - quantity: จำนวนที่ต้องการซื้อ
    - user_id: รหัสสมาชิก (เช่น "M001")
    - account_id: รหัสบัญชีธนาคาร (เช่น "A123")
    - cineplex_name: ชื่อสาขา (เช่น "C")
    - coupon_id: รหัสคูปองส่วนลด (ถ้ามี ปล่อยว่างได้)
    """
    result = system.order_goods(
        goods_name=goods_name,
        values=quantity,
        user_id=user_id,
        account_id=account_id,
        cineplex_name=cineplex_name,
        coupon_id=coupon_id
    )
    return str(result)

@mcp.tool()
def cancel_order(
    order_id: str,
    user_id: str,
    cineplex_name: str
) -> str:
    """
    ยกเลิกรายการสั่งซื้อสินค้าที่ทำสำเร็จไปแล้ว พร้อมทำการคืนเงิน (Refund) คืนสต็อก และคืนคูปอง
    - order_id: รหัสการสั่งซื้อ (เช่น "ORD-0001")
    - user_id: รหัสสมาชิกที่เป็นเจ้าของออเดอร์ (เช่น "M001")
    - cineplex_name: ชื่อสาขาโรงภาพยนตร์ (เช่น "C")
    """
    result = system.cancel_order(
        order_id=order_id,
        user_id=user_id,
        cineplex_name=cineplex_name
    )
    return str(result)

if __name__ == "__main__":
    mcp.run()