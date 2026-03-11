from typing import List, Optional
from datetime import datetime
from enums import MemberTier, BookingStatus
from theater import Showtime, Movie, Theater, ShowtimeSeat


# ── Reward ────────────────────────────────────────────────────────────────

class Reward:
    def __init__(self, reward_id: str, name: str, point_cost: int, stock: int):
        self.__reward_id  = reward_id
        self.__name       = name
        self.__point_cost = point_cost
        self.__stock      = stock

    @property
    def id(self) -> str:
        return self.__reward_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def point_cost(self) -> int:
        return self.__point_cost

    @property
    def stock(self) -> int:
        return self.__stock

    def decrease_stock(self) -> bool:
        if self.__stock > 0:
            self.__stock -= 1
            return True
        return False


# ── Booking ───────────────────────────────────────────────────────────────

class Booking:
    def __init__(self, booking_id: str, user, showtime: Showtime,
                 timestamp: datetime, status: BookingStatus, total_price: float = 0.0, account_id = None):
        self.__booking_id    = booking_id
        self.__user          = user
        self.__showtime      = showtime
        self.__ticket        = None
        self.__timestamp     = timestamp
        self.__showtime_seat: List[ShowtimeSeat] = []
        self.__status        = status
        self.__total_price   = total_price
        self.__account = account_id
    @property
    def account(self):
        return self.__account
    
    @account.setter
    def account(self, account):
        account = account
        
    @property
    def id(self) -> str:
        return self.__booking_id

    @property
    def showtime(self) -> Showtime:
        return self.__showtime

    @property
    def status(self) -> BookingStatus:
        return self.__status

    @property
    def showtime_seat(self) -> List[ShowtimeSeat]:
        return self.__showtime_seat

    @property
    def total_price(self) -> float:
        return self.__total_price

    @property
    def ticket(self):
        return self.__ticket

    @showtime_seat.setter
    def showtime_seat(self, seats):
        self.__showtime_seat = seats

    @total_price.setter
    def total_price(self, price):
        self.__total_price = price

    @status.setter
    def status(self, stat):
        self.__status = stat

    @ticket.setter
    def ticket(self, tk):
        self.__ticket = tk


# ── Ticket ────────────────────────────────────────────────────────────────

class Ticket:
    def __init__(self, booking: Booking, cineplex, user, movie: Movie,
                 theater: Theater, showtime: Showtime, seat_list: list):
        self.__booking  = booking
        self.__cineplex = cineplex
        self.__user     = user
        self.__movie    = movie
        self.__theater  = theater
        self.__showtime = showtime
        self.seat_list  = seat_list


# ── User ──────────────────────────────────────────────────────────────────

class User:
    def __init__(self, id: str, name: str, email: str = "",
                 phone_number: str = "", birthday: str = "", password: str = ""):
        """
        สร้าง User ใหม่
        - Guest  : ต้องการแค่ id + name (email ถ้ามี)
        - Member : เพิ่ม phone_number, birthday, password ตอน register
        """
        self.__id             = id
        self.__name           = name
        self.__email          = email
        self.__phone_number   = phone_number
        self.__birthday       = birthday
        self.__password       = password
        self.__point          = 0
        self.__coupon_list    = []
        self.__ticket_list    = []
        self.__booking_list:  List[Booking] = []
        self.__reward_history: list = []   # [{"reward_id", "name", "point_cost", "redeemed_at"}]
        self.__total_spending = 0
        self.__type_user      = MemberTier.GUEST
        self.__last_monthly_coupon: Optional[str] = None  # "YYYY-MM" ของเดือนล่าสุดที่รับ

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def email(self) -> str:
        return self.__email

    @property
    def phone_number(self) -> str:
        return self.__phone_number

    @property
    def birthday(self) -> str:
        return self.__birthday

    @property
    def booking_list(self) -> List[Booking]:
        return self.__booking_list

    @property
    def tier(self) -> MemberTier:
        return self.__type_user

    def get_member_id(self) -> str:
        return self.__id

    def get_discount(self) -> float:
        return self.__type_user.get_discount()

    def get_point(self) -> int:
        return self.__point

    def add_point(self, p: int):
        self.__point += p

    def deduct_point(self, p: int) -> bool:
        if self.__point >= p:
            self.__point -= p
            return True
        return False

    def add_booking(self, b: Booking):
        self.__booking_list.append(b)

    def add_ticket(self, t: Ticket):
        self.__ticket_list.append(t)

    def add_reward_history(self, reward_id: str, name: str, point_cost: int):
        from datetime import datetime
        self.__reward_history.append({
            "reward_id":  reward_id,
            "name":       name,
            "point_cost": point_cost,
            "redeemed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })

    def get_reward_history(self) -> list:
        return list(self.__reward_history)

    def get_last_monthly_coupon(self) -> Optional[str]:
        return self.__last_monthly_coupon

    def set_last_monthly_coupon(self, ym: str):
        """ym = 'YYYY-MM'"""
        self.__last_monthly_coupon = ym

    def add_password(self, password: str):
        self.__password = password

    def set_profile(self, phone_number: str = "", birthday: str = ""):
        """อัปเดตข้อมูลโปรไฟล์ตอนสมัครสมาชิก"""
        if phone_number:
            self.__phone_number = phone_number
        if birthday:
            self.__birthday = birthday

    def check_password(self, password: str) -> bool:
        return self.__password == password

    def has_password(self) -> bool:
        return bool(self.__password)

    def change_type(self, tier: MemberTier):
        self.__type_user = tier

    def set_tier(self, tier: MemberTier):
        self.__type_user = tier

    def search_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        for b in self.__booking_list:
            if b.id == booking_id:
                return b
        return None
