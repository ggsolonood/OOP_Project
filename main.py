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
    #return class showtime
    def search_showtime_by_id(self,showtime_id):
        for i in self.search_showtime_by_id:
            if i.id == showtime_id:
                return i
        return False
    #return class goods
    def search_goods_by_id(self,goods_id):
        for i in self.__goods_list:
            if i.id == goods_id:
                return i
        return False
class Showtime:
    def __init__(self,showtime,movie,theater,status,subtitle,start_time,end_time,base_price):
        self.__id = showtime
        self.__movie = movie
        self.__theater = theater
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
    def __init__(self,seat_id,seat_number,type_seat,status):
        super().__init__(seat_id,seat_number,type_seat)
        self.__status = status
    @property
    def status(self):
        return self.__status
class Goods:
    def __init__(self,values,name,price,type_goods):
        self.__values = values
        self.__name = name
        self.__price = price
        self.__type_goods = type_goods
    
class Order:
    def __init__(self,goods,user_id):
        self.__goods = goods
        self.__user_id = user_id
        self.__totle_cost = None
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
class DiscountCoupon(coupon):
    def __init__(self, id, name, discount):
        super().__init__(id, name)
        self.__discount = discount
class ExchangeCoupon(coupon):
    def __init__(self, id, name,goods):
        super().__init__(id, name)
        self.__list_goods = goods
#test script
# --------------------------------------------

#----------------------------------------------

#api