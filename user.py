from datetime import datetime
from enums import MemberTier, BookingStatus, TicketStatus
from goods import Order

class Coupon:
    def __init__(self, coupon_id: str, name: str):
        self.__id = coupon_id
        self.__name = name
        self.__is_used = False

    @property
    def id(self): return self.__id
    @property
    def name(self): return self.__name
    @property
    def is_used(self): return self.__is_used
    @is_used.setter
    def is_used(self, val: bool): self.__is_used = val

    def calculate_discount(self, total_price: float) -> float:
        return total_price

class FixedDiscountCoupon(Coupon):
    def __init__(self, coupon_id: str, name: str, discount_amount: float):
        super().__init__(coupon_id, name)
        self.__discount_amount = discount_amount

    def calculate_discount(self, total_price: float) -> float:
        return max(total_price - self.__discount_amount, 0)

class PercentDiscountCoupon(Coupon):
    def __init__(self, coupon_id: str, name: str, percent: float):
        super().__init__(coupon_id, name)
        self.__percent = percent

    def calculate_discount(self, total_price: float) -> float:
        return max(total_price * (1 - self.__percent), 0)

class Ticket:
    def __init__(self, ticket_id: str, booking_id: str, showtime_id: str, seat_number: str):
        self.__id = ticket_id
        self.__booking_id = booking_id
        self.__showtime_id = showtime_id
        self.__seat_number = seat_number
        self.__status = TicketStatus.UNUSED

    @property
    def id(self): return self.__id
    @property
    def booking_id(self): return self.__booking_id
    @property
    def showtime_id(self): return self.__showtime_id
    @property
    def seat_number(self): return self.__seat_number
    @seat_number.setter
    def seat_number(self, val: str): self.__seat_number = val
    @property
    def status(self): return self.__status
    @status.setter
    def status(self, val: TicketStatus): self.__status = val

class Booking:
    def __init__(self, booking_id: str, user_id: str, showtime_id: str, seat_ids: list, total: float, coupon_id: str = None):
        self.__id = booking_id
        self.__user_id = user_id
        self.__showtime_id = showtime_id
        self.__seat_ids = seat_ids
        self.__total = total
        self.__coupon_id = coupon_id
        self.__account_number = None
        self.__status = BookingStatus.PENDING
        self.__created_at = datetime.now()

    @property
    def id(self): return self.__id
    @property
    def user_id(self): return self.__user_id
    @property
    def showtime_id(self): return self.__showtime_id
    @property
    def seat_ids(self): return self.__seat_ids
    @seat_ids.setter
    def seat_ids(self, ids: list): self.__seat_ids = ids
    @property
    def total(self): return self.__total
    @total.setter
    def total(self, val: float): self.__total = val
    @property
    def account_number(self): return self.__account_number
    @account_number.setter
    def account_number(self, val: str): self.__account_number = val
    @property
    def coupon_id(self): return self.__coupon_id
    @property
    def status(self): return self.__status
    @status.setter
    def status(self, val: BookingStatus): self.__status = val
    @property
    def created_at(self): return self.__created_at

class User:
    def __init__(self, user_id: str, name: str, birth_date: str, email: str = "", phone: str = ""):
        self.__id = user_id
        self.__name = name
        self.__birth_date = birth_date
        self.__email = email
        self.__phone = phone
        self.__tier = MemberTier.GUEST
        self.__points = 0
        self.__renewal_count = 0
        self.__penalty_end = None
        self.__coupons = []
        self.__bookings = []
        self.__orders = []
        self.__tickets = []

    @property
    def id(self): return self.__id
    @property
    def name(self): return self.__name
    @property
    def birth_date(self): return self.__birth_date
    @property
    def email(self): return self.__email
    @property
    def phone(self): return self.__phone
    @property
    def penalty_end(self): return self.__penalty_end
    @property
    def bookings(self): return self.__bookings
    @property
    def orders(self): return self.__orders
    @property
    def coupons(self): return self.__coupons
    @property
    def tickets(self): return self.__tickets
    @property
    def points(self): return self.__points
    @property
    def tier(self): return self.__tier
    @property
    def renewal_count(self): return self.__renewal_count

    def upgrade_tier(self):
        self.__renewal_count += 1
        if self.__renewal_count == 1: self.__tier = MemberTier.SILVER
        elif self.__renewal_count == 2: self.__tier = MemberTier.GOLD
        elif self.__renewal_count >= 3: self.__tier = MemberTier.PLATINUM

    @property
    def discount(self) -> float:
        if self.__tier == MemberTier.SILVER: return 0.05
        if self.__tier == MemberTier.GOLD: return 0.10
        if self.__tier == MemberTier.PLATINUM: return 0.15
        return 0.0

    def decrease_points(self, amount: int): self.__points -= amount
    def add_points(self, amount: int): self.__points += amount

    def add_coupon(self, coupon: Coupon): self.__coupons.append(coupon)
    def add_booking(self, bkg: Booking): self.__bookings.append(bkg)
    def add_order(self, order: Order): self.__orders.append(order)
    def add_ticket(self, ticket: Ticket): self.__tickets.append(ticket)