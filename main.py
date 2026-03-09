from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional
from datetime import datetime
from fastmcp import FastMCP


# ==========================================
# Enums
# ==========================================

class OrderStatus(Enum):
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"

class MemberTier(Enum):
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"
    GUEST = "Guest"

class BookingStatus(Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class GoodsType(Enum):
    POPCORN = "Popcorn"
    DRINKS = "Drinks"
    SNACK = "Snack"

class SeatType(Enum):
    NORMALSEAT = "Normalseat"
    SOFA = "Sofa"
    HONEYMOONBED = "Honeymoonbed"

class TheaterType(Enum):
    STANDARD = "Standard"
    IMAX = "IMAX"
    _4DX = "4DX"


# ==========================================
# Bank & Account (จากไฟล์ 1)
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
# Payment Gateway (จากไฟล์ 1)
# ==========================================

class PaymentGateway:
    def __init__(self, account_id, amount):
        self.__account_id = account_id
        self.__amount = amount

    def pay(self, bank):
        return bank.payment(self.__account_id, self.__amount)


# ==========================================
# Goods & Popcorn (จากไฟล์ 1)
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
# Coupon (จากไฟล์ 1)
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
# Order (จากไฟล์ 1)
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
# Movie, Theater, Seat, Showtime (จากไฟล์ 2)
# ==========================================

class Movie:
    def __init__(self, id, name, duration, genre, age_rating):
        self.__movie_id = id
        self.__movie_name = name
        self.__duration = duration
        self.__genre = genre
        self.__age_rating = age_rating

    @property
    def id(self): return self.__movie_id

    @property
    def name(self): return self.__movie_name


class Theater:
    def __init__(self, theater_id, type_theater: TheaterType):
        self.__theater_id = theater_id
        self.__seats_list = []
        self.__type_theater = type_theater

    @property
    def id(self): return self.__theater_id

    def add_seat(self, seat):
        self.__seats_list.append(seat)

    def search_seat_by_no(self, seat_no):
        for s in self.__seats_list:
            if s.seat_number == seat_no:
                return s
        return None


class Seat:
    def __init__(self, seat_id, seat_number, type_seat: SeatType):
        self.__seat_id = seat_id
        self.__seat_number = seat_number
        self.__type_seat = type_seat

    @property
    def id(self): return self.__seat_id

    @property
    def seat_number(self): return self.__seat_number

    @property
    def type_seat(self): return self.__type_seat


class ShowtimeSeat(Seat):
    def __init__(self, seat: Seat, status: BookingStatus):
        super().__init__(seat.id, seat.seat_number, seat.type_seat)
        self.__status = status

    @property
    def status(self): return self.__status


class Showtime:
    def __init__(self, showtime_id, movie, theater, start_time, end_time, base_price):
        self.__id = showtime_id
        self.__movie = movie
        self.__theater = theater
        self.__start_time = start_time
        self.__end_time = end_time
        self.__base_price = base_price
        self.__showtime_seat = []

    @property
    def movie(self): return self.__movie

    @property
    def id(self): return self.__id

    @property
    def theater(self): return self.__theater

    def is_seat_available(self, seat_no):
        for s in self.__showtime_seat:
            if s.seat_number == seat_no:
                return False
        return True

    def remove_seats(self, seat_nos: list):
        self.__showtime_seat = [s for s in self.__showtime_seat if s.seat_number not in seat_nos]

    def add_seats(self, seats: list, status: BookingStatus):
        new_seats = []
        for s in seats:
            st_seat = ShowtimeSeat(s, status)
            self.__showtime_seat.append(st_seat)
            new_seats.append(st_seat)
        return new_seats


# ==========================================
# Booking & Ticket (จากไฟล์ 2)
# ==========================================

class Booking:
    def __init__(self, booking_id, user, showtime, timestamp, status: BookingStatus, total_price=0.0):
        self.__booking_id = booking_id
        self.__user = user
        self.__showtime = showtime
        self.__ticket = None
        self.__timestamp = timestamp
        self.__showtime_seat = []
        self.__status = status
        self.__total_price = total_price

    @property
    def id(self): return self.__booking_id

    @property
    def showtime(self): return self.__showtime

    @property
    def status(self): return self.__status

    @property
    def showtime_seat(self): return self.__showtime_seat

    @property
    def total_price(self): return self.__total_price

    @property
    def ticket(self): return self.__ticket

    @showtime_seat.setter
    def showtime_seat(self, seats): self.__showtime_seat = seats

    @total_price.setter
    def total_price(self, price): self.__total_price = price

    @status.setter
    def status(self, stat): self.__status = stat

    @ticket.setter
    def ticket(self, tk): self.__ticket = tk


class Ticket:
    def __init__(self, booking, cineplex, user, movie, theater, showtime, seat_list):
        self.__booking = booking
        self.__cineplex = cineplex
        self.__user = user
        self.__movie = movie
        self.__theater = theater
        self.__showtime = showtime
        self.seat_list = seat_list


# ==========================================
# User / Member (รวม File 1 + File 2)
# ==========================================

class User:
    def __init__(self, id, name, email, phone_number, birthday, password,
                 member_id=None, registered_date=None):
        self.__id = id
        self.__name = name
        self.__email = email
        self.__phone_number = phone_number
        self.__birthday = birthday
        self.__password = password
        self.__member_id = member_id or id
        self.__registered_date = registered_date
        self.__point = 0
        self.__coupon_list = []
        self.__ticket_list = []
        self.__booking_list = []
        self.__total_spending = 0
        self.__type_user = MemberTier.SILVER

    @property
    def id(self): return self.__id

    @property
    def name(self): return self.__name

    @property
    def booking_list(self): return self.__booking_list

    def get_member_id(self):
        return self.__member_id

    def get_discount(self):
        if self.__type_user == MemberTier.GOLD:
            return 0.10
        elif self.__type_user == MemberTier.PLATINUM:
            return 0.15
        return 0.0

    def add_booking(self, booking):
        self.__booking_list.append(booking)

    def search_booking_by_id(self, booking_id):
        for b in self.__booking_list:
            if b.id == booking_id:
                return b
        return None


# ==========================================
# Cineplex (รวม File 1 stock + File 2 cinema)
# ==========================================

class Cineplex:
    def __init__(self, cineplex_id, name):
        self.__cineplex_id = cineplex_id
        self.__name = name
        self.__movies_list = []
        self.__theaters_list = []
        self.__showtime_list = []
        self.__goods_stock = []  # สินค้า (จากไฟล์ 1)

    @property
    def id(self): return self.__cineplex_id

    def get_cineplex_name(self): return self.__name

    def add_movie(self, movie): self.__movies_list.append(movie)

    def add_theater(self, theater): self.__theaters_list.append(theater)

    def add_showtime(self, showtime): self.__showtime_list.append(showtime)

    def add_popcorn(self, name, values: int, price, flavor):
        popcorn = Popcorn(name, values, price, flavor)
        self.__goods_stock.append(popcorn)

    def search_goods_stock(self, goods_name, amount_needed=0):
        for item in self.__goods_stock:
            if item.get_name() == goods_name:
                if amount_needed == 0 or item.check_values(amount_needed):
                    return item
        return None


# ==========================================
# JamorCineplex — Main System (ไฟล์ 2 เป็นหลัก + รวม logic ไฟล์ 1)
# ==========================================

class JamorCineplex:
    def __init__(self, bank: Bank):
        self.__bank = bank
        self.__cineplex_list = []
        self.__user_list = []
        self.__booking_list = []
        self.__coupon_list = []
        self.__order_list = []
        self.__order_counter = 1

    # --- Cineplex ---
    def add_cineplex(self, cineplex: Cineplex):
        self.__cineplex_list.append(cineplex)

    def search_cineplex_by_id(self, cineplex_id):
        for c in self.__cineplex_list:
            if c.id == cineplex_id:
                return c
        return None

    def find_cineplex_by_name(self, name):
        for c in self.__cineplex_list:
            if c.get_cineplex_name() == name:
                return c
        return None

    # --- User ---
    def add_user(self, user: User):
        self.__user_list.append(user)

    def register_member(self, name, birthday, member_id, registered_date,
                        email=None, phone_number=None, password=""):
        user = User(
            id=member_id,
            name=name,
            email=email or "",
            phone_number=phone_number or "",
            birthday=birthday,
            password=password,
            member_id=member_id,
            registered_date=registered_date
        )
        self.__user_list.append(user)
        return user

    def search_user_by_id(self, user_id):
        for u in self.__user_list:
            if u.id == user_id:
                return u
        return None

    # --- Coupon ---
    def add_discount_coupon(self, coupon_id, name, discount):
        coupon = DiscountCoupon(coupon_id, name, discount)
        self.__coupon_list.append(coupon)

    # --- Order (Goods) ---
    def find_order(self, order_id):
        for o in self.__order_list:
            if o.get_order_id() == order_id:
                return o
        return None

    def order_goods(self, goods_name, values, user_id, account_id, cineplex_name, coupon_id=None):
        user = self.search_user_by_id(user_id)
        if not user:
            return "Member not found"

        cineplex = self.find_cineplex_by_name(cineplex_name)
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

    def cancel_order(self, order_id, user_id, cineplex_name):
        user = self.search_user_by_id(user_id)
        if not user:
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
                return (f"Cancel success, Refund {total_paid} THB to account {account_id}. "
                        f"Restored: {item_text}, Coupon: {coupon_text}.")
            else:
                return "Refund failed"

    def _restore_order_resources(self, order, cineplex_name):
        goods_name, values = order.get_items()
        cineplex = self.find_cineplex_by_name(cineplex_name)

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

    # --- Booking (Cinema) ---
    def process_change_booking(self, user_id: str, booking_id: str, new_seat_nos: list):
        user = self.search_user_by_id(user_id)
        if not user:
            return None, "User not found"

        booking = user.search_booking_by_id(booking_id)
        if not booking:
            return None, "Booking not found"

        current_seats = [s.seat_number for s in booking.showtime_seat]
        if len(new_seat_nos) != len(current_seats):
            return None, f"Validation Error: Must select exactly {len(current_seats)} seats"

        if len(new_seat_nos) != len(set(new_seat_nos)):
            return None, "Validation Error: Duplicate seats requested"

        showtime = booking.showtime
        theater = showtime.theater
        booking_status = booking.status
        old_total_price = booking.total_price

        new_real_seats = []
        new_total_price = 0.0

        for seat_no in new_seat_nos:
            if seat_no not in current_seats:
                if not showtime.is_seat_available(seat_no):
                    return None, f"Seat {seat_no} is already booked"

            seat = theater.search_seat_by_no(seat_no)
            if not seat:
                return None, f"Seat {seat_no} not found in theater"

            seat_price = 200 if seat.type_seat == SeatType.NORMALSEAT else 300
            new_total_price += seat_price
            new_real_seats.append(seat)

        discount = user.get_discount()
        new_total_price = new_total_price * (1 - discount)

        if booking_status == BookingStatus.CONFIRMED:
            if new_total_price > old_total_price:
                return None, "Cannot change to more expensive seats"

            showtime.remove_seats(current_seats)
            new_st_seats = showtime.add_seats(new_real_seats, BookingStatus.CONFIRMED)
            booking.showtime_seat = new_st_seats
            booking.total_price = new_total_price

            if booking.ticket:
                booking.ticket.seat_list = new_st_seats

            return booking, "Change booking (Confirmed) successful"

        elif booking_status == BookingStatus.PENDING:
            showtime.remove_seats(current_seats)
            new_st_seats = showtime.add_seats(new_real_seats, BookingStatus.PENDING)
            booking.showtime_seat = new_st_seats
            booking.total_price = new_total_price

            return booking, "Change booking (Pending) successful"

        return None, "Invalid booking status"


# ==========================================
# Setup & Mock Data
# ==========================================

kbank = Bank("KBank")
my_account = kbank.create_account("J", "A123", balance=500)

system = JamorCineplex(kbank)

# --- Cineplex + สินค้า (จากไฟล์ 1) ---
cineplex_c = Cineplex("CPX_C", "C")
cineplex_c.add_popcorn("Popcorn", 100, 50, "Cheese")
system.add_cineplex(cineplex_c)

# --- Cineplex โรงหนัง (จากไฟล์ 2) ---
cineplex_siam = Cineplex("CPX01", "Siam Paragon")
theater1 = Theater("T01", TheaterType.STANDARD)
theater1.add_seat(Seat("S01", "A1", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S02", "A2", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S03", "B1", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S04", "B2", SeatType.NORMALSEAT))
cineplex_siam.add_theater(theater1)
movie1 = Movie("M01", "The Matrix", 120, "Sci-Fi", "13+")
showtime1 = Showtime("ST01", movie1, theater1, "10:00", "12:00", 200)
cineplex_siam.add_showtime(showtime1)
system.add_cineplex(cineplex_siam)

# --- Members ---
system.register_member("J", "01-01-1990", "M001", "2023-01-01")

user1 = User("U01", "Ken", "ken@mail.com", "081", "2000-01-01", "1234")
system.add_user(user1)

# --- Coupon ---
system.add_discount_coupon("C10", "Discount 10", 10)

# --- Booking เริ่มต้น (จากไฟล์ 2) ---
initial_seats = [theater1.search_seat_by_no("A1"), theater1.search_seat_by_no("A2")]
booking1 = Booking("BK01", user1, showtime1, datetime.now(), BookingStatus.PENDING, 400.0)
booking1.showtime_seat = showtime1.add_seats(initial_seats, BookingStatus.PENDING)
user1.add_booking(booking1)


# ==========================================
# MCP Tools (รวมทุก tool)
# ==========================================

mcp = FastMCP("JamorCineplex System")


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


@mcp.tool()
def change_booking_seats(user_id: str, booking_id: str, new_seat_nos: List[str]) -> str:
    """
    ใช้สำหรับเปลี่ยนที่นั่ง (Change Seats) ให้กับ Booking เดิมที่มีอยู่แล้ว
    เช่น ถ้าย้ายจากที่นั่งเดิม ไปเป็น B1 และ B2 ให้ส่ง new_seat_nos=["B1", "B2"]
    """
    booking, msg = system.process_change_booking(user_id, booking_id, new_seat_nos)

    if not booking:
        return f"Failed to change booking: {msg}"

    return (f"Success: {msg}\n"
            f"Booking ID: {booking.id}\n"
            f"Status: {booking.status.value}\n"
            f"New Seats: {[s.seat_number for s in booking.showtime_seat]}\n"
            f"Total Price: {booking.total_price} THB")


@mcp.tool()
def get_user_bookings(user_id: str) -> str:
    """
    ดึงข้อมูลประวัติการจองภาพยนตร์ (Bookings) ทั้งหมดของ User ตาม user_id
    """
    user = system.search_user_by_id(user_id)
    if not user:
        return "Error: User not found in the system."

    if not user.booking_list:
        return f"User {user_id} currently has no bookings."

    bookings_info = []
    for b in user.booking_list:
        info = {
            "booking_id": b.id,
            "movie": b.showtime.movie.name,
            "status": b.status.value,
            "seats": [s.seat_number for s in b.showtime_seat],
            "price": b.total_price
        }
        bookings_info.append(str(info))

    return "\n".join(bookings_info)


if __name__ == "__main__":
    mcp.run()