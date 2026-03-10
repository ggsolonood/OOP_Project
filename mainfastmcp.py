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


class SeatType(Enum):
    NORMALSEAT = "Normalseat"
    SOFA = "Sofa"
    HONEYMOONBED = "Honeymoonbed"

    def get_price(self):
        prices = {
            SeatType.NORMALSEAT: 100,
            SeatType.SOFA: 200,
            SeatType.HONEYMOONBED: 350,
        }
        return prices[self]


class MemberTier(Enum):
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"
    GUEST = "Guest"

    def get_discount(self):
        discounts = {
            MemberTier.SILVER: 0.05,
            MemberTier.GOLD: 0.10,
            MemberTier.PLATINUM: 0.15,
            MemberTier.GUEST: 0.0,
        }
        return discounts[self]


class BookingStatus(Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class GoodsType(Enum):
    POPCORN = "Popcorn"
    DRINKS = "Drinks"
    SNACK = "Snack"


class TheaterType(Enum):
    STANDARD = "Standard"
    IMAX = "IMAX"
    _4DX = "4DX"


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

    def get_name(self): return self._name
    def get_price(self): return self._price

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


class Drinks(Goods):
    def __init__(self, name, values: int, price, flavor):
        super().__init__(name, values, price)
        self._flavor = flavor


class Snack(Goods):
    def __init__(self, name, values: int, price):
        super().__init__(name, values, price)


# ==========================================
# Coupon
# ==========================================

class Coupon:
    def __init__(self, id, name):
        self.__coupon_id = id
        self.__name = name
        self._is_used = False

    @property
    def id(self): return self.__coupon_id

    def get_coupon_id(self): return self.__coupon_id
    def get_discount(self): return 0

    def update_status(self, status):
        self._is_used = (status != "Available")
        return "success"


class DiscountCoupon(Coupon):
    def __init__(self, id, name, discount):
        super().__init__(id, name)
        self.__discount = discount

    def get_discount(self): return self.__discount


class ExchangeCoupon(Coupon):
    def __init__(self, id, name, goods):
        super().__init__(id, name)
        self.__list_goods = goods

    def get_goods_list(self): return self.__list_goods


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

    def get_order_id(self): return self.__order_id

    def get_status(self):
        return self.__status.value if isinstance(self.__status, OrderStatus) else self.__status

    def update_status(self, status: OrderStatus):
        self.__status = status
        return "success"

    def get_payment_details(self): return self.__account_id, self.__total_paid
    def get_items(self): return self.__goods_name, self.__values
    def get_used_coupon(self): return self.__coupon_id

    def pay(self, bank, gateway):
        return gateway.pay(bank)


# ==========================================
# Movie, Theater, Seat, Showtime
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
    def __init__(self, theater_id, type_theater):
        self.__theater_id = theater_id
        self.__seats_list = []
        self.__type_theater = type_theater

    @property
    def id(self): return self.__theater_id

    def add_seat(self, seat): self.__seats_list.append(seat)

    def search_seat_by_no(self, seat_no):
        for s in self.__seats_list:
            if s.seat_number == seat_no: return s
        return None


# Theater subclasses
class StandardTheater(Theater):
    def __init__(self, theater_id, seat_list=None):
        super().__init__(theater_id, TheaterType.STANDARD)
        if seat_list:
            for s in seat_list: self.add_seat(s)

class IMAXTheater(Theater):
    def __init__(self, theater_id, seat_list=None):
        super().__init__(theater_id, TheaterType.IMAX)
        if seat_list:
            for s in seat_list: self.add_seat(s)

class FourDXTheater(Theater):
    def __init__(self, theater_id, seat_list=None):
        super().__init__(theater_id, TheaterType._4DX)
        if seat_list:
            for s in seat_list: self.add_seat(s)


class Seat:
    def __init__(self, seat_id, seat_number, type_seat):
        self.__seat_id = seat_id
        self.__seat_number = seat_number
        self.__type_seat = type_seat

    @property
    def id(self): return self.__seat_id
    @property
    def seat_number(self): return self.__seat_number
    @property
    def type_seat(self): return self.__type_seat


# Seat subclasses
class NormalSeat(Seat):
    def __init__(self, seat_id, seat_number):
        super().__init__(seat_id, seat_number, SeatType.NORMALSEAT)

class SofaSeat(Seat):
    def __init__(self, seat_id, seat_number):
        super().__init__(seat_id, seat_number, SeatType.SOFA)

class HoneyMoonBed(Seat):
    def __init__(self, seat_id, seat_number):
        super().__init__(seat_id, seat_number, SeatType.HONEYMOONBED)


class ShowtimeSeat(Seat):
    def __init__(self, seat: Seat, status: BookingStatus):
        super().__init__(seat.id, seat.seat_number, seat.type_seat)
        self.__status = status

    @property
    def status(self): return self.__status


class Showtime:
    def __init__(self, showtime_id, movie, theater, status, subtitle, start_time, end_time, base_price):
        self.__id = showtime_id
        self.__movie = movie
        self.__theater = theater
        self.__status = status
        self.__subtitle = subtitle
        self.__start_time = start_time
        self.__end_time = end_time
        self.__base_price = base_price
        self.__showtime_seat = []

    @property
    def id(self): return self.__id
    @property
    def movie(self): return self.__movie
    @property
    def theater(self): return self.__theater
    @property
    def status(self): return self.__status
    @property
    def subtitle(self): return self.__subtitle
    @property
    def base_price(self): return self.__base_price

    def is_seat_available(self, seat_no):
        for s in self.__showtime_seat:
            if s.seat_number == seat_no: return False
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
# Booking & Ticket
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
# Cineplex
# ==========================================

class Cineplex:
    def __init__(self, cineplex_id, name):
        self.__cineplex_id = cineplex_id
        self.__name = name
        self.__movies_list = []
        self.__theaters_list = []
        self.__showtime_list = []
        self.__goods_list = []

    @property
    def id(self): return self.__cineplex_id

    def get_cineplex_name(self): return self.__name

    def search_movie_by_id(self, movie_id):
        for i in self.__movies_list:
            if i.id == movie_id: return i
        return None

    def search_theater_by_id(self, theater_id):
        for i in self.__theaters_list:
            if i.id == theater_id: return i
        return None

    def search_showtime_by_id(self, showtime_id):
        for i in self.__showtime_list:
            if i.id == showtime_id: return i
        return None

    def add_movie(self, movie): self.__movies_list.append(movie)
    def add_theater(self, theater): self.__theaters_list.append(theater)
    def add_showtime(self, showtime): self.__showtime_list.append(showtime)

    def add_popcorn(self, name, values: int, price, flavor):
        self.__goods_list.append(Popcorn(name, values, price, flavor))

    def add_drinks(self, name, values: int, price, flavor):
        self.__goods_list.append(Drinks(name, values, price, flavor))

    def add_snack(self, name, values: int, price):
        self.__goods_list.append(Snack(name, values, price))

    def search_goods_stock(self, goods_name, amount_needed=0):
        for item in self.__goods_list:
            if item.get_name() == goods_name:
                if amount_needed == 0 or item.check_values(amount_needed):
                    return item
        return None


# ==========================================
# User / Member
# ==========================================

class User:
    def __init__(self, id, name, email, phone_number, birthday, password):
        self.__id = id
        self.__name = name
        self.__email = email
        self.__phone_number = phone_number
        self.__birthday = birthday
        self.__password = password
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
    @property
    def tier(self): return self.__type_user

    def get_member_id(self): return self.__id

    def get_discount(self):
        return self.__type_user.get_discount()

    def add_point(self, point: int):
        self.__point += point

    def get_point(self):
        return self.__point

    def add_booking(self, booking):
        self.__booking_list.append(booking)

    def add_ticket(self, ticket):
        self.__ticket_list.append(ticket)

    def search_booking_by_id(self, booking_id):
        for b in self.__booking_list:
            if b.id == booking_id: return b
        return None


class Member(User):
    def __init__(self, name, birthday, member_id, registered_date, email=None, phone_number=None):
        super().__init__(member_id, name, email or "", phone_number or "", birthday, "")
        self._birthday = birthday


# ==========================================
# JamorCineplex — Main System
# ==========================================

class JamorCineplex:
    def __init__(self, bank: Bank):
        self.__bank = bank
        self.__cineplex_list = []
        self.__user_list = []
        self.__booking_list = []
        self.__order_list = []
        self.__coupon_list = []
        self.__ticket_list = []
        self.__order_counter = 1

    # --- Search ---
    def search_cineplex_by_id(self, cineplex_id):
        for i in self.__cineplex_list:
            if i.id == cineplex_id: return i
        return None

    def search_user_by_id(self, user_id):
        for i in self.__user_list:
            if i.id == user_id: return i
        return None

    def search_order_by_id(self, order_id):
        for o in self.__order_list:
            if o.get_order_id() == order_id: return o
        return None

    def search_booking_by_id(self, booking_id):
        for b in self.__booking_list:
            if b.id == booking_id: return b
        return None

    # --- Add / Register ---
    def add_cineplex(self, cineplex: Cineplex):
        self.__cineplex_list.append(cineplex)

    def add_user(self, user):
        self.__user_list.append(user)

    def get_all_users(self):
        return self.__user_list

    def register_member(self, name, birthday, member_id, registered_date, email=None, phone_number=None):
        self.__user_list.append(Member(name, birthday, member_id, registered_date, email, phone_number))

    # --- Admin: Create ---
    def process_create_cineplex(self, cineplex_id, name):
        if self.search_cineplex_by_id(cineplex_id):
            return False, "Cineplex ID already exists."
        self.__cineplex_list.append(Cineplex(cineplex_id, name))
        return True, "Cineplex created successfully."

    def process_create_movie(self, cineplex_id, movie_id, name, duration, genre, age_rating):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex: return False, "Cineplex not found."
        if cineplex.search_movie_by_id(movie_id): return False, "Movie ID already exists in this Cineplex."
        cineplex.add_movie(Movie(movie_id, name, duration, genre, age_rating))
        return True, "Movie created successfully."

    def process_create_theater(self, cineplex_id, theater_id, type_theater):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex: return False, "Cineplex not found."
        if cineplex.search_theater_by_id(theater_id): return False, "Theater ID already exists."
        cineplex.add_theater(Theater(theater_id, type_theater))
        return True, "Theater created successfully."

    def process_create_seat(self, cineplex_id, theater_id, seat_id, seat_number, type_seat):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex: return False, "Cineplex not found."
        theater = cineplex.search_theater_by_id(theater_id)
        if not theater: return False, "Theater not found."
        theater.add_seat(Seat(seat_id, seat_number, type_seat))
        return True, "Seat created successfully."

    def process_create_showtime(self, cineplex_id, showtime_id, movie_id, theater_id,
                                 status, subtitle, start_time, end_time, base_price):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex: return False, "Cineplex not found."
        movie = cineplex.search_movie_by_id(movie_id)
        if not movie: return False, "Movie not found."
        theater = cineplex.search_theater_by_id(theater_id)
        if not theater: return False, "Theater not found."
        if cineplex.search_showtime_by_id(showtime_id): return False, "Showtime ID already exists."
        cineplex.add_showtime(Showtime(showtime_id, movie, theater, status, subtitle, start_time, end_time, base_price))
        return True, "Showtime created successfully."

    def process_create_coupon(self, coupon_type, coupon_id, name, discount=0.0, goods_list=None):
        if coupon_type.lower() == "discount":
            new_coupon = DiscountCoupon(coupon_id, name, discount)
        elif coupon_type.lower() == "exchange":
            new_coupon = ExchangeCoupon(coupon_id, name, goods_list or [])
        else:
            return False, "Invalid coupon_type. Use 'discount' or 'exchange'."
        self.__coupon_list.append(new_coupon)
        return True, "Coupon created successfully."

    # --- Booking ---
    def process_get_booking_history(self, user_id: str, status_filter: str = None):
        user = self.search_user_by_id(user_id)
        if not user: return False, "Member not found", None

        if user.tier == MemberTier.GUEST:
            return False, "Guest members cannot view booking history", None

        bookings = user.booking_list
        if status_filter:
            try:
                filter_enum = BookingStatus(status_filter)
                bookings = [b for b in bookings if b.status == filter_enum]
            except ValueError:
                return False, f"Invalid status. Use: {[s.value for s in BookingStatus]}", None

        return True, "OK", (user, bookings)

    def process_create_booking(self, booking_id: str, user_id: str, cineplex_id, showtime_id: str, seat_nos: list):
        user = self.search_user_by_id(user_id)
        if not user: return False, "Member not found"

        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex: return False, "Cineplex not found"

        showtime = cineplex.search_showtime_by_id(showtime_id)
        if not showtime: return False, "Showtime not found"

        if self.search_booking_by_id(booking_id): return False, "Booking ID already exists"

        theater = showtime.theater
        seats = []
        for seat_no in seat_nos:
            if not showtime.is_seat_available(seat_no):
                return False, f"Seat {seat_no} is already booked"
            seat = theater.search_seat_by_no(seat_no)
            if not seat: return False, f"Seat {seat_no} not found in theater"
            seats.append(seat)

        base_price = showtime.base_price
        seat_total = sum(s.type_seat.get_price() for s in seats)
        raw_total = base_price + seat_total
        discount = user.get_discount()
        total_price = round(raw_total * (1 - discount), 2)

        booking = Booking(booking_id, user, showtime, datetime.now(), BookingStatus.PENDING, total_price)
        booked_seats = showtime.add_seats(seats, BookingStatus.PENDING)
        booking.showtime_seat = booked_seats

        self.__booking_list.append(booking)
        user.add_booking(booking)

        return True, (f"Booking created | Booking ID: {booking_id} | "
                      f"Seats: {seat_nos} | Total: {total_price} THB "
                      f"(Discount {int(discount * 100)}%)")

    def process_cancel_booking(self, booking_id: str, user_id: str):
        user = self.search_user_by_id(user_id)
        if not user: return False, "Member not found"

        booking = self.search_booking_by_id(booking_id)
        if not booking: return False, "Booking not found"

        if booking.status == BookingStatus.CANCELLED:
            return False, "Booking is already cancelled"
        if booking.status == BookingStatus.COMPLETED:
            return False, "Cannot cancel a completed booking"

        seat_nos = [s.seat_number for s in booking.showtime_seat]
        booking.showtime.remove_seats(seat_nos)
        booking.status = BookingStatus.CANCELLED

        return True, f"Booking {booking_id} cancelled (no refund)"

    def process_confirm_booking(self, booking_id: str, user_id: str, account_id: str):
        user = self.search_user_by_id(user_id)
        if not user: return False, "Member not found"

        booking = self.search_booking_by_id(booking_id)
        if not booking: return False, "Booking not found"

        if booking.status != BookingStatus.PENDING:
            return False, f"Booking status is '{booking.status.value}', cannot confirm"

        total = booking.total_price
        gateway = PaymentGateway(account_id, total)
        result = gateway.pay(self.__bank)

        if result is True:
            booking.status = BookingStatus.CONFIRMED
            showtime = booking.showtime
            ticket = Ticket(
                booking=booking, cineplex=None, user=user,
                movie=showtime.movie, theater=showtime.theater,
                showtime=showtime, seat_list=booking.showtime_seat
            )
            booking.ticket = ticket
            user.add_ticket(ticket)
            self.__ticket_list.append(ticket)

            seat_count = len(booking.showtime_seat)
            points_earned = seat_count * 10
            user.add_point(points_earned)

            return True, (f"Confirm booking success | Total Paid: {total} THB | "
                          f"Points earned: {points_earned} (Total: {user.get_point()})")
        else:
            return False, "Failed: Insufficient balance"

    def process_change_booking(self, user_id: str, booking_id: str, new_seat_nos: list):
        user = self.search_user_by_id(user_id)
        if not user: return None, "User not found"

        booking = user.search_booking_by_id(booking_id)
        if not booking: return None, "Booking not found"

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
            new_total_price += seat.type_seat.get_price()
            new_real_seats.append(seat)

        discount = user.get_discount()
        new_total_price = round(new_total_price * (1 - discount), 2)

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

    # --- Goods ---
    def process_order_goods(self, cineplex_id, goods_name, values, user_id, account_id, coupon_id=None):
        member = self.search_user_by_id(user_id)
        if not member: return False, "Member not found"

        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex: return False, "Cineplex not found"

        target_good = cineplex.search_goods_stock(goods_name, values)
        if not target_good: return False, "Out of stock or Not enough items"

        discount_amount = 0
        used_coupon_id = None
        if coupon_id:
            for c in self.__coupon_list:
                if c.get_coupon_id() == coupon_id:
                    discount_amount = c.get_discount()
                    used_coupon_id = coupon_id
                    c.update_status("Used")
                    break

        total_price = max((target_good.get_price() * values) - discount_amount, 0)
        order_id = f"ORD-{self.__order_counter:04d}"
        self.__order_counter += 1

        order = Order(order_id, goods_name, values, account_id, total_price, used_coupon_id)
        gateway = PaymentGateway(account_id, total_price)

        if order.pay(self.__bank, gateway):
            target_good.clearstock(values)
            self.__order_list.append(order)
            return True, f"Order success | Order ID: {order_id} | Total Paid: {total_price} THB"
        else:
            return False, "Payment failed: Insufficient balance or invalid account."

    def process_cancel_order(self, cineplex_id, order_id, user_id):
        member = self.search_user_by_id(user_id)
        if not member: return False, "Member not found"

        order = self.search_order_by_id(order_id)
        if not order: return False, "Order not found"

        current_status = order.get_status()
        if current_status == OrderStatus.CANCELLED.value: return False, "Order is already cancelled"
        if current_status == OrderStatus.REFUNDED.value: return False, "Order has already been refunded"

        if current_status == OrderStatus.COMPLETED.value:
            account_id, total_paid = order.get_payment_details()
            if self.__bank.refund(account_id, total_paid):
                goods_name, values = order.get_items()
                cineplex = self.search_cineplex_by_id(cineplex_id)
                restored_item_text = f"{values} x {goods_name}"
                restored_coupon_text = "None"
                if cineplex:
                    target_good = cineplex.search_goods_stock(goods_name)
                    if target_good:
                        target_good.restore_stock(values)
                coupon_id = order.get_used_coupon()
                if coupon_id:
                    for c in self.__coupon_list:
                        if c.get_coupon_id() == coupon_id:
                            c.update_status("Available")
                            restored_coupon_text = str(coupon_id)
                            break
                order.update_status(OrderStatus.CANCELLED)
                return True, (f"Cancel success, Refund {total_paid} THB to account {account_id}. "
                              f"Restored: {restored_item_text}, Coupon: {restored_coupon_text}.")
            else:
                return False, "Refund failed"

        return False, "Cannot cancel order with current status"


# ==========================================
# Setup
# ==========================================

kbank = Bank("KBank")
kbank.create_account("J", "A123", balance=500)
system = JamorCineplex(kbank)

# Cineplex + สินค้า
cineplex_c = Cineplex("CPX_C", "C")
cineplex_c.add_popcorn("Popcorn", 100, 50, "Cheese")
system.add_cineplex(cineplex_c)

# Cineplex โรงหนัง
cineplex_siam = Cineplex("CPX01", "Siam Paragon")
theater1 = Theater("T01", TheaterType.STANDARD)
theater1.add_seat(Seat("S01", "A1", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S02", "A2", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S03", "B1", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S04", "B2", SeatType.NORMALSEAT))
cineplex_siam.add_theater(theater1)
movie1 = Movie("M01", "The Matrix", 120, "Sci-Fi", "13+")
showtime1 = Showtime("ST01", movie1, theater1, "Active", "TH", "10:00", "12:00", 200)
cineplex_siam.add_showtime(showtime1)
system.add_cineplex(cineplex_siam)

# Members
system.register_member("J", "01-01-1990", "M001", "2023-01-01")
user1 = User("U01", "Ken", "ken@mail.com", "081", "2000-01-01", "1234")
system.add_user(user1)

# Coupon
system.process_create_coupon("discount", "C10", "Discount 10", 10)

# Booking เริ่มต้น
initial_seats = [theater1.search_seat_by_no("A1"), theater1.search_seat_by_no("A2")]
booking1 = Booking("BK01", user1, showtime1, datetime.now(), BookingStatus.PENDING, 400.0)
booking1.showtime_seat = showtime1.add_seats(initial_seats, BookingStatus.PENDING)
user1.add_booking(booking1)


# ==========================================
# MCP Tools
# ==========================================

mcp = FastMCP("JamorCineplex")


# --- Cinema Management ---

@mcp.tool()
def create_cineplex(cineplex_id: int, name: str) -> str:
    """สร้างสาขาโรงภาพยนตร์ใหม่ (Cineplex)"""
    success, msg = system.process_create_cineplex(cineplex_id, name)
    return f"Success: {msg}" if success else f"Error: {msg}"


@mcp.tool()
def create_movie(cineplex_id: int, movie_id: int, name: str, duration: int, genre: str, age_rating: str) -> str:
    """เพิ่มภาพยนตร์เรื่องใหม่เข้าไปในระบบของสาขา"""
    success, msg = system.process_create_movie(cineplex_id, movie_id, name, duration, genre, age_rating)
    return f"Success: {msg}" if success else f"Error: {msg}"


@mcp.tool()
def create_theater(cineplex_id: int, theater_id: str, type_theater: str) -> str:
    """สร้างโรงฉายภาพยนตร์ย่อยภายในสาขา"""
    success, msg = system.process_create_theater(cineplex_id, theater_id, type_theater)
    return f"Success: {msg}" if success else f"Error: {msg}"


@mcp.tool()
def create_seat(cineplex_id: int, theater_id: str, seat_id: str, seat_number: str, type_seat: str) -> str:
    """เพิ่มที่นั่งในโรงฉายภาพยนตร์"""
    success, msg = system.process_create_seat(cineplex_id, theater_id, seat_id, seat_number, type_seat)
    return f"Success: {msg}" if success else f"Error: {msg}"


@mcp.tool()
def create_showtime(cineplex_id: int, showtime_id: str, movie_id: int, theater_id: str,
                    status: str, subtitle: str, start_time: str, end_time: str, base_price: float) -> str:
    """สร้างรอบฉายภาพยนตร์"""
    success, msg = system.process_create_showtime(
        cineplex_id, showtime_id, movie_id, theater_id, status, subtitle, start_time, end_time, base_price)
    return f"Success: {msg}" if success else f"Error: {msg}"


@mcp.tool()
def create_coupon(coupon_type: str, coupon_id: str, name: str,
                  discount: float = 0.0, goods_list: List[str] = []) -> str:
    """สร้างคูปองส่วนลด (discount) หรือ คูปองแลกของ (exchange)"""
    success, msg = system.process_create_coupon(coupon_type, coupon_id, name, discount, goods_list)
    return f"Success: {msg}" if success else f"Error: {msg}"


# --- Store ---

@mcp.tool()
def order_goods(cineplex_id: int, goods_name: str, quantity: int,
                user_id: str, account_id: str, coupon_id: str = None) -> str:
    """
    ทำการสั่งซื้อสินค้าที่สาขาโรงภาพยนตร์
    - cineplex_id: รหัสสาขา, goods_name: ชื่อสินค้า, quantity: จำนวน
    - user_id: รหัสสมาชิก, account_id: รหัสบัญชี, coupon_id: รหัสคูปอง (ถ้ามี)
    """
    success, msg = system.process_order_goods(
        cineplex_id=cineplex_id, goods_name=goods_name, values=quantity,
        user_id=user_id, account_id=account_id, coupon_id=coupon_id
    )
    return f"Success: {msg}" if success else f"Error: {msg}"


@mcp.tool()
def cancel_order(cineplex_id: int, order_id: str, user_id: str) -> str:
    """
    ยกเลิกรายการสั่งซื้อ พร้อมคืนเงิน คืนสต็อก และคืนคูปอง
    - cineplex_id: รหัสสาขา, order_id: รหัสออเดอร์ (เช่น "ORD-0001"), user_id: รหัสสมาชิก
    """
    success, msg = system.process_cancel_order(cineplex_id=cineplex_id, order_id=order_id, user_id=user_id)
    return f"Success: {msg}" if success else f"Error: {msg}"


# --- Booking ---

@mcp.tool()
def create_booking(booking_id: str, user_id: str, cineplex_id: int,
                   showtime_id: str, seat_nos: List[str]) -> str:
    """
    สร้างการจองภาพยนตร์ใหม่ (สถานะ Pending รอยืนยัน)
    ราคา = base_price + ราคาประเภทที่นั่ง หักส่วนลดตาม MemberTier
    (NORMALSEAT=100, SOFA=200, HONEYMOONBED=350 | SILVER=5%, GOLD=10%, PLATINUM=15%, GUEST=0%)
    """
    success, msg = system.process_create_booking(booking_id, user_id, cineplex_id, showtime_id, seat_nos)
    return f"Success: {msg}" if success else f"Error: {msg}"


@mcp.tool()
def cancel_booking(booking_id: str, user_id: str) -> str:
    """ยกเลิกการจองภาพยนตร์ (ไม่คืนเงิน)"""
    success, msg = system.process_cancel_booking(booking_id, user_id)
    return f"Success: {msg}" if success else f"Error: {msg}"


@mcp.tool()
def confirm_booking(booking_id: str, user_id: str, account_id: str) -> str:
    """ยืนยันการจองและหักเงินผ่านบัญชีธนาคาร"""
    success, msg = system.process_confirm_booking(booking_id, user_id, account_id)
    return f"Success: {msg}" if success else f"Error: {msg}"


@mcp.tool()
def change_booking_seats(user_id: str, booking_id: str, new_seat_nos: List[str]) -> str:
    """
    เปลี่ยนที่นั่งให้กับ Booking เดิม
    - new_seat_nos: รายการที่นั่งใหม่ (เช่น ["B1", "B2"])
    """
    booking, msg = system.process_change_booking(user_id, booking_id, new_seat_nos)
    if not booking:
        return f"Error: {msg}"
    return (f"Success: {msg}\n"
            f"Booking ID: {booking.id}\n"
            f"Status: {booking.status.value}\n"
            f"New Seats: {[s.seat_number for s in booking.showtime_seat]}\n"
            f"Total Price: {booking.total_price} THB")


@mcp.tool()
def get_booking_history(user_id: str, status_filter: str = None) -> str:
    """
    ดูประวัติการจองของสมาชิก (GUEST ไม่มีสิทธิ์)
    - status_filter: "Pending" | "Confirmed" | "Completed" | "Cancelled" (ไม่ระบุ = แสดงทั้งหมด)
    """
    success, msg, data = system.process_get_booking_history(user_id, status_filter)
    if not success:
        return f"Error: {msg}"

    user, bookings = data
    if not bookings:
        label = f"[{status_filter}]" if status_filter else ""
        return f"No bookings found {label} for user {user_id}"

    lines = [
        "=== Booking History ===",
        f"Member: {user.name} | Tier: {user.tier.value} | Points: {user.get_point()}",
        f"Total bookings shown: {len(bookings)}",
        "---"
    ]
    for b in bookings:
        lines.append(
            f"[{b.id}] {b.showtime.movie.name} | "
            f"Seats: {[s.seat_number for s in b.showtime_seat]} | "
            f"Status: {b.status.value} | "
            f"Total: {b.total_price} THB"
        )
    return "\n".join(lines)


@mcp.tool()
def get_all_users() -> str:
    """ดูรายชื่อสมาชิกทั้งหมดในระบบ พร้อม Tier และ Points"""
    users = system.get_all_users()
    if not users:
        return "No users in the system."

    lines = [f"=== All Users ({len(users)}) ==="]
    for u in users:
        lines.append(
            f"[{u.id}] {u.name} | "
            f"Tier: {u.tier.value} | "
            f"Points: {u.get_point()} | "
            f"Bookings: {len(u.booking_list)}"
        )
    return "\n".join(lines)


@mcp.tool()
def get_user_bookings(user_id: str) -> str:
    """ดึงข้อมูลการจองทั้งหมดของ User ตาม user_id"""
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