from datetime import datetime
from enums import MemberTier, BookingStatus
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
    def is_used(self, val: bool):
        self.__is_used = val

class DiscountCoupon(Coupon):
    def __init__(self, coupon_id: str, name: str, discount_amount: float):
        super().__init__(coupon_id, name)
        self.__discount_amount = discount_amount

    @property
    def discount_amount(self): return self.__discount_amount

class ExchangeCoupon(Coupon):
    def __init__(self, coupon_id: str, name: str, goods_list: list):
        super().__init__(coupon_id, name)
        self.__goods_list = goods_list

    @property
    def goods_list(self): return self.__goods_list


class Booking:
    def __init__(self, booking_id: str, showtime_id: str, seat_ids: list, total: float, coupon_id: str = None):
        self.__id = booking_id
        self.__showtime_id = showtime_id
        self.__seat_ids = seat_ids
        self.__total = total
        self.__coupon_id = coupon_id
        self.__account_id = None
        self.__status = BookingStatus.PENDING

    @property
    def id(self): return self.__id
    @property
    def showtime_id(self): return self.__showtime_id
    @property
    def coupon_id(self): return self.__coupon_id
    
    @property
    def seat_ids(self): return self.__seat_ids
    @seat_ids.setter
    def seat_ids(self, ids: list): self.__seat_ids = ids

    @property
    def total(self): return self.__total
    @total.setter
    def total(self, val: float): self.__total = val

    @property
    def account_id(self): return self.__account_id
    @account_id.setter
    def account_id(self, val: str): self.__account_id = val

    @property
    def status(self): return self.__status
    @status.setter
    def status(self, val: BookingStatus): self.__status = val

class User:
    def __init__(self, user_id: str, name: str, tier: MemberTier = MemberTier.GUEST):
        self.__id = user_id
        self.__name = name
        self.__tier = tier
        self.__points = 0
        self.__penalty_end = None
        self.__coupons = []
        self.__bookings = []
        self.__orders = []

    @property
    def id(self): return self.__id
    @property
    def name(self): return self.__name
    @property
    def penalty_end(self): return self.__penalty_end
    @property
    def bookings(self): return self.__bookings
    @property
    def orders(self): return self.__orders
    @property
    def coupons(self): return self.__coupons
    @property
    def points(self): return self.__points

    @property
    def tier(self): return self.__tier
    @tier.setter
    def tier(self, val: MemberTier): self.__tier = val

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