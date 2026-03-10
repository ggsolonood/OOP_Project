# =============================================================================
# sumfile.py  –  JamorCineplex  (all-in-one)
# =============================================================================
#
# AI EDIT GUIDE
# ─────────────────────────────────────────────────────────────────────────────
#  แต่ละส่วนถูกคั่นด้วย tag  ## ── SECTION: <ชื่อ> ──
#
#  SECTION INDEX
#  ┌─────────────────────────────────┬──────────────────────────────────────────┐
#  │ SECTION                         │ เนื้อหา                                  │
#  ├─────────────────────────────────┼──────────────────────────────────────────┤
#  │ IMPORTS                         │ import ทั้งหมด                           │
#  │ ENUMS                           │ Enum ทุกตัว                              │
#  │ MODELS_PAYMENT                  │ Account, Bank, PaymentGateway, Order     │
#  │ MODELS_GOODS                    │ Goods (+ GoodsType enum, factory)        │
#  │ MODELS_COUPON                   │ Coupon, DiscountCoupon, ExchangeCoupon   │
#  │ MODELS_THEATER                  │ Seat, Theater (+ factory), Movie         │
#  │ MODELS_SHOWTIME                 │ Showtime, ShowtimeSeat                   │
#  │ MODELS_USER                     │ User, Member, Booking, Ticket            │
#  │ MODELS_CINEPLEX                 │ Cineplex, JamorCineplex                  │
#  │ MOCK_DATA                       │ ข้อมูลตัวอย่างสำหรับทดสอบ               │
#  │ SCHEMAS                         │ Pydantic request/response models         │
#  │ APP                             │ สร้าง FastAPI app + include routers      │
#  │ ROUTES_ADMIN                    │ /admin/* endpoints                       │
#  │ ROUTES_STORE                    │ /store/* endpoints                       │
#  │ ROUTES_BOOKING                  │ /booking/* endpoints                     │
#  │ ROUTES_USERS                    │ /users/* endpoints                       │
#  │ ENTRYPOINT                      │ uvicorn runner                           │
#  └─────────────────────────────────┴──────────────────────────────────────────┘
#
#  KEY DESIGN DECISIONS (v3)
#  ─────────────────────────────────────────────────────────────────────────────
#  [Theater]
#    BEFORE : StandardTheater(id) / IMAXTheater(id) / FourDXTheater(id)
#    AFTER  : Theater.create(id, "IMAX")  หรือ  Theater(id, TheaterType.IMAX)
#             TheaterType.from_str("imax") แปลง string → enum (case-insensitive)
#
#  [Seat]
#    BEFORE : NormalSeat(id, no) / SofaSeat(id, no) / HoneyMoonBed(id, no)
#    AFTER  : Seat(id, no, SeatType.NORMALSEAT)
#             SeatType.from_str("normalseat") แปลง string → enum (case-insensitive)
#
#  [Order]
#    ไม่มี subclass — ใช้ OrderStatus enum แยกสถานะ (ไม่เปลี่ยนแปลงมาก)
#
#  [Bank / JamorCineplex]
#    BEFORE : JamorCineplex(bank)  ← bank ผูกอยู่ใน system, ไม่แยกชัดเจน
#    AFTER  : Bank เป็น object อิสระ สร้างแยก แล้ว inject เข้า JamorCineplex(bank)
#             ไม่มี "ธนาคารของ cineplex" — Bank อยู่นอก JamorCineplex เสมอ
# =============================================================================


## ── SECTION: IMPORTS ──────────────────────────────────────────────────────
from datetime import datetime
from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, FastAPI, HTTPException, Query
from pydantic import BaseModel
import uvicorn


## ── SECTION: ENUMS ────────────────────────────────────────────────────────

class OrderStatus(Enum):
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    REFUNDED  = "Refunded"


class SeatType(Enum):
    """
    ประเภทที่นั่ง — แทน subclass NormalSeat / SofaSeat / HoneyMoonBed
    ใช้: Seat(id, no, SeatType.SOFA)
         Seat(id, no, SeatType.from_str("sofa"))
    """
    NORMALSEAT   = "Normalseat"
    SOFA         = "Sofa"
    HONEYMOONBED = "Honeymoonbed"

    @classmethod
    def from_str(cls, value: str) -> "SeatType":
        """case-insensitive: 'sofa' → SeatType.SOFA"""
        mapping = {t.value.lower(): t for t in cls}
        result  = mapping.get(value.strip().lower())
        if result is None:
            raise ValueError(
                f"Unknown SeatType '{value}'. "
                f"Valid values: {[t.value for t in cls]}"
            )
        return result

    def get_price(self) -> float:
        prices = {
            SeatType.NORMALSEAT:   100,
            SeatType.SOFA:         200,
            SeatType.HONEYMOONBED: 350,
        }
        return prices[self]


class MemberTier(Enum):
    SILVER   = "Silver"
    GOLD     = "Gold"
    PLATINUM = "Platinum"
    GUEST    = "Guest"

    def get_discount(self) -> float:
        discounts = {
            MemberTier.SILVER:   0.05,
            MemberTier.GOLD:     0.10,
            MemberTier.PLATINUM: 0.15,
            MemberTier.GUEST:    0.0,
        }
        return discounts[self]


class BookingStatus(Enum):
    PENDING   = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class GoodsType(Enum):
    """
    ประเภทสินค้า — แทน subclass Popcorn / Drinks / Snack
    ใช้: Goods("Cheese Popcorn", 100, 50, GoodsType.POPCORN, flavor="Cheese")
         Goods.create("Cheese Popcorn", 100, 50, "popcorn", flavor="Cheese")
    """
    POPCORN = "Popcorn"
    DRINKS  = "Drinks"
    SNACK   = "Snack"

    @classmethod
    def from_str(cls, value: str) -> "GoodsType":
        """case-insensitive: 'popcorn' -> GoodsType.POPCORN"""
        mapping = {t.value.lower(): t for t in cls}
        result  = mapping.get(value.strip().lower())
        if result is None:
            raise ValueError(
                f"Unknown GoodsType '{value}'. "
                f"Valid values: {[t.value for t in cls]}"
            )
        return result

    @property
    def has_flavor(self) -> bool:
        """True ถ้าประเภทนี้ต้องการ flavor (Popcorn, Drinks)"""
        return self in (GoodsType.POPCORN, GoodsType.DRINKS)


class TheaterType(Enum):
    """
    ประเภทโรงหนัง — แทน subclass StandardTheater / IMAXTheater / FourDXTheater
    ใช้: Theater.create(id, "IMAX")
         Theater(id, TheaterType.IMAX)
    """
    STANDARD = "Standard"
    IMAX     = "IMAX"
    _4DX     = "4DX"

    @classmethod
    def from_str(cls, value: str) -> "TheaterType":
        """case-insensitive: 'imax' → TheaterType.IMAX"""
        mapping = {t.value.lower(): t for t in cls}
        result  = mapping.get(value.strip().lower())
        if result is None:
            raise ValueError(
                f"Unknown TheaterType '{value}'. "
                f"Valid values: {[t.value for t in cls]}"
            )
        return result


## ── SECTION: MODELS_PAYMENT ───────────────────────────────────────────────

class Account:
    def __init__(self, name: str, balance: float, account_id: str):
        self.__name    = name
        self.__balance = balance
        self.__id      = account_id

    def get_id(self) -> str: return self.__id

    def decrease_balance(self, amount: float) -> bool:
        if self.__balance >= amount:
            self.__balance -= amount
            return True
        return False

    def increase_balance(self, amount: float) -> bool:
        self.__balance += amount
        return True


class Bank:
    """
    ระบบธนาคาร — object อิสระ ไม่ผูกติดกับ JamorCineplex
    ใช้งาน:
        bank   = Bank("KBank")
        bank.create_account("Alice", "ACC001", balance=5000)
        system = JamorCineplex(bank)   # inject เข้า system
    """
    def __init__(self, name: str):
        self.__name         = name
        self.__account_list: List[Account] = []

    @property
    def name(self) -> str: return self.__name

    def create_account(self, name: str, account_id: str, balance: float) -> Account:
        account = Account(name, balance, account_id)
        self.__account_list.append(account)
        return account

    def _find_account(self, account_id: str) -> Optional[Account]:
        for acc in self.__account_list:
            if acc.get_id() == account_id:
                return acc
        return None

    def payment(self, account_id: str, amount: float) -> bool:
        account = self._find_account(account_id)
        return account.decrease_balance(amount) if account else False

    def refund(self, account_id: str, amount: float) -> bool:
        account = self._find_account(account_id)
        return account.increase_balance(amount) if account else False


class PaymentGateway:
    def __init__(self, account_id: str, amount: float):
        self.__account_id = account_id
        self.__amount     = amount

    def pay(self, bank: Bank) -> bool:
        return bank.payment(self.__account_id, self.__amount)


class Order:
    """
    คำสั่งซื้อสินค้า — ใช้ OrderStatus enum แยกสถานะ (ไม่มี subclass)
    """
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

    def get_order_id(self) -> str: return self.__order_id

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


## ── SECTION: MODELS_GOODS ─────────────────────────────────────────────────

class Goods:
    """
    สินค้า — ใช้ GoodsType enum แยกประเภท (ไม่มี subclass อีกต่อไป)
    ตัวอย่าง:
        Goods("Cheese Popcorn", 100, 50, GoodsType.POPCORN, flavor="Cheese")
        Goods.create("Cola", 50, 30, "drinks", flavor="Original")
        Goods.create("Nachos", 30, 40, "snack")
    """
    def __init__(self, name: str, values: int, price: float,
                 goods_type: GoodsType, flavor: str = None):
        self.__name       = name
        self.__values     = values
        self.__price      = price
        self.__goods_type = (goods_type if isinstance(goods_type, GoodsType)
                             else GoodsType.from_str(str(goods_type)))
        self.__flavor     = flavor  # None สำหรับ Snack

    # ── factory ──────────────────────────────────────────────────────────────
    @classmethod
    def create(cls, name: str, values: int, price: float,
               type_str: str, flavor: str = None) -> "Goods":
        """Goods.create("Cola", 50, 30, "drinks", flavor="Original")"""
        return cls(name, values, price, GoodsType.from_str(type_str), flavor)

    # ── properties ───────────────────────────────────────────────────────────
    @property
    def goods_type(self) -> GoodsType: return self.__goods_type
    @property
    def flavor(self) -> Optional[str]: return self.__flavor

    def get_name(self) -> str:    return self.__name
    def get_price(self) -> float: return self.__price

    def check_values(self, amount_needed: int) -> bool:
        return self.__values >= amount_needed

    def clearstock(self, amount: int):
        self.__values -= amount
        return "success"

    def restore_stock(self, amount: int):
        self.__values += amount
        return "success"


## ── SECTION: MODELS_COUPON ────────────────────────────────────────────────

class Coupon:
    # last_date: datetime | None  — None = ไม่มีวันหมดอายุ
    def __init__(self, id: str, name: str, last_date: datetime = None):
        self.__coupon_id = id
        self.__name      = name
        self.__last_date = last_date
        self._is_used    = False

    @property
    def id(self) -> str: return self.__coupon_id

    @property
    def last_date(self) -> Optional[datetime]: return self.__last_date

    def get_coupon_id(self) -> str:   return self.__coupon_id
    def get_discount(self) -> float:  return 0

    def is_expired(self) -> bool:
        """True ถ้าเลย last_date แล้ว  (None = ไม่หมดอายุ)"""
        if self.__last_date is None:
            return False
        return datetime.now() > self.__last_date

    def update_status(self, status: str):
        self._is_used = (status != "Available")
        return "success"


class DiscountCoupon(Coupon):
    def __init__(self, id: str, name: str, discount: float,
                 last_date: datetime = None):
        super().__init__(id, name, last_date)
        self.__discount = discount

    def get_discount(self) -> float: return self.__discount


class ExchangeCoupon(Coupon):
    def __init__(self, id: str, name: str, goods: list,
                 last_date: datetime = None):
        super().__init__(id, name, last_date)
        self.__list_goods = goods

    def get_goods_list(self) -> list: return self.__list_goods


## ── SECTION: MODELS_THEATER ───────────────────────────────────────────────

class Seat:
    """
    ที่นั่ง — ใช้ SeatType enum แยกประเภท (ไม่มี subclass อีกต่อไป)
    ตัวอย่าง:
        Seat("S01", "A1", SeatType.NORMALSEAT)
        Seat("S01", "A1", SeatType.from_str("sofa"))
    """
    def __init__(self, seat_id: str, seat_number: str, type_seat: SeatType):
        self.__seat_id     = seat_id
        self.__seat_number = seat_number
        self.__type_seat   = (type_seat if isinstance(type_seat, SeatType)
                              else SeatType.from_str(str(type_seat)))

    @property
    def id(self) -> str:             return self.__seat_id
    @property
    def seat_number(self) -> str:    return self.__seat_number
    @property
    def type_seat(self) -> SeatType: return self.__type_seat


class Theater:
    """
    โรงหนัง — ใช้ TheaterType enum แยกประเภท (ไม่มี subclass อีกต่อไป)
    ตัวอย่าง:
        Theater("T01", TheaterType.IMAX)     ← enum โดยตรง
        Theater.create("T01", "IMAX")        ← string (case-insensitive)
    """
    def __init__(self, theater_id: str, type_theater: TheaterType):
        self.__theater_id    = theater_id
        self.__seats_list:   List[Seat] = []
        self.__type_theater  = (type_theater if isinstance(type_theater, TheaterType)
                                else TheaterType.from_str(str(type_theater)))
        self.__showtime_list: list      = []

    # ── factory ──────────────────────────────────────────────────────────────
    @classmethod
    def create(cls, theater_id: str, type_str: str) -> "Theater":
        """Theater.create('T01', 'IMAX')  ←  สะดวกกว่าเวลารับมาจาก API"""
        return cls(theater_id, TheaterType.from_str(type_str))

    # ── properties ───────────────────────────────────────────────────────────
    @property
    def id(self) -> str:                   return self.__theater_id
    @property
    def type_theater(self) -> TheaterType: return self.__type_theater
    @property
    def showtime_list(self) -> list:       return self.__showtime_list

    # ── seat management ───────────────────────────────────────────────────────
    def add_seat(self, seat: Seat):
        self.__seats_list.append(seat)

    def search_seat_by_no(self, seat_no: str) -> Optional[Seat]:
        for s in self.__seats_list:
            if s.seat_number == seat_no:
                return s
        return None

    # ── showtime management ───────────────────────────────────────────────────
    def add_showtime(self, showtime):
        """ลงทะเบียน showtime เข้า theater (เรียกหลัง conflict check ผ่านแล้ว)"""
        self.__showtime_list.append(showtime)

    def has_conflict(self, dt_start: datetime, dt_end: datetime) -> bool:
        """
        True ถ้าช่วง [dt_start, dt_end) ทับซ้อนกับ showtime ที่มีอยู่
        เงื่อนไข: new_start < existing_end  AND  new_end > existing_start
        """
        for st in self.__showtime_list:
            if dt_start < st.end_time and dt_end > st.start_time:
                return True
        return False


class Movie:
    def __init__(self, id: str, name: str, duration: int, genre: str, age_rating: str):
        self.__movie_id   = id
        self.__movie_name = name
        self.__duration   = duration
        self.__genre      = genre
        self.__age_rating = age_rating

    @property
    def id(self) -> str:   return self.__movie_id
    @property
    def name(self) -> str: return self.__movie_name


## ── SECTION: MODELS_SHOWTIME ──────────────────────────────────────────────

class ShowtimeSeat(Seat):
    def __init__(self, seat: Seat, status: BookingStatus):
        super().__init__(seat.id, seat.seat_number, seat.type_seat)
        self.__status = status

    @property
    def status(self) -> BookingStatus: return self.__status


class Showtime:
    # start_time / end_time เป็น datetime object
    # รูปแบบ string ที่รับจาก API: "YYYY-MM-DD HH:MM"
    DT_FORMAT = "%Y-%m-%d %H:%M"

    def __init__(self, showtime_id: str, movie: Movie, theater: Theater,
                 status: str, subtitle: str,
                 start_time: datetime, end_time: datetime, base_price: float):
        self.__id            = showtime_id
        self.__movie         = movie
        self.__theater       = theater
        self.__status        = status
        self.__subtitle      = subtitle
        self.__start_time    = start_time
        self.__end_time      = end_time
        self.__base_price    = base_price
        self.__showtime_seat: List[ShowtimeSeat] = []

    @property
    def id(self) -> str:              return self.__id
    @property
    def movie(self) -> Movie:         return self.__movie
    @property
    def theater(self) -> Theater:     return self.__theater
    @property
    def status(self) -> str:          return self.__status
    @property
    def subtitle(self) -> str:        return self.__subtitle
    @property
    def base_price(self) -> float:    return self.__base_price
    @property
    def start_time(self) -> datetime: return self.__start_time
    @property
    def end_time(self) -> datetime:   return self.__end_time

    def is_upcoming(self) -> bool:
        """True ถ้ารอบฉายยังไม่เริ่ม (start_time >= ปัจจุบัน)"""
        return self.__start_time >= datetime.now()

    def is_seat_available(self, seat_no: str) -> bool:
        for s in self.__showtime_seat:
            if s.seat_number == seat_no:
                return False
        return True

    def remove_seats(self, seat_nos: list):
        self.__showtime_seat = [
            s for s in self.__showtime_seat if s.seat_number not in seat_nos
        ]

    def add_seats(self, seats: list, status: BookingStatus) -> List[ShowtimeSeat]:
        new_seats = []
        for s in seats:
            st_seat = ShowtimeSeat(s, status)
            self.__showtime_seat.append(st_seat)
            new_seats.append(st_seat)
        return new_seats


## ── SECTION: MODELS_USER ──────────────────────────────────────────────────

class Booking:
    def __init__(self, booking_id: str, user, showtime: Showtime,
                 timestamp: datetime, status: BookingStatus, total_price: float = 0.0):
        self.__booking_id    = booking_id
        self.__user          = user
        self.__showtime      = showtime
        self.__ticket        = None
        self.__timestamp     = timestamp
        self.__showtime_seat: List[ShowtimeSeat] = []
        self.__status        = status
        self.__total_price   = total_price

    @property
    def id(self) -> str:                          return self.__booking_id
    @property
    def showtime(self) -> Showtime:               return self.__showtime
    @property
    def status(self) -> BookingStatus:            return self.__status
    @property
    def showtime_seat(self) -> List[ShowtimeSeat]: return self.__showtime_seat
    @property
    def total_price(self) -> float:               return self.__total_price
    @property
    def ticket(self):                             return self.__ticket

    @showtime_seat.setter
    def showtime_seat(self, seats): self.__showtime_seat = seats
    @total_price.setter
    def total_price(self, price):   self.__total_price = price
    @status.setter
    def status(self, stat):         self.__status = stat
    @ticket.setter
    def ticket(self, tk):           self.__ticket = tk


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


class User:
    """
    ผู้ใช้ระบบ — ใช้ MemberTier enum แยกระดับ (ไม่มี subclass Member อีกต่อไป)
    __type_user เริ่มต้นที่ MemberTier.GUEST เสมอ
    ใช้ set_tier() เพื่ออัปเกรด tier เช่น set_tier(MemberTier.SILVER)
    """
    def __init__(self, id: str, name: str, email: str = "", phone_number: str = "",
                 birthday: str = "", password: str = ""):
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
        self.__total_spending = 0
        self.__type_user      = MemberTier.GUEST   # เริ่มต้น GUEST เสมอ

    @property
    def id(self) -> str:                     return self.__id
    @property
    def name(self) -> str:                   return self.__name
    @property
    def booking_list(self) -> List[Booking]: return self.__booking_list
    @property
    def tier(self) -> MemberTier:            return self.__type_user

    def get_member_id(self) -> str:    return self.__id
    def get_discount(self) -> float:   return self.__type_user.get_discount()
    def get_point(self) -> int:        return self.__point
    def add_point(self, p: int):       self.__point += p
    def add_booking(self, b: Booking): self.__booking_list.append(b)
    def add_ticket(self, t: Ticket):   self.__ticket_list.append(t)

    def set_tier(self, tier: MemberTier):
        """อัปเกรด / เปลี่ยน tier เช่น user.set_tier(MemberTier.SILVER)"""
        self.__type_user = tier

    def search_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        for b in self.__booking_list:
            if b.id == booking_id:
                return b
        return None


## ── SECTION: MODELS_CINEPLEX ──────────────────────────────────────────────

class Cineplex:
    def __init__(self, cineplex_id: str, name: str):
        self.__cineplex_id    = cineplex_id
        self.__name           = name
        self.__movies_list:   List[Movie]    = []
        self.__theaters_list: List[Theater]  = []
        self.__showtime_list: List[Showtime] = []
        self.__goods_list:    List[Goods]    = []

    @property
    def id(self) -> str:                       return self.__cineplex_id
    @property
    def showtime_list(self) -> List[Showtime]: return self.__showtime_list

    def get_cineplex_name(self) -> str: return self.__name

    def search_movie_by_id(self, movie_id: str) -> Optional[Movie]:
        for i in self.__movies_list:
            if i.id == movie_id: return i
        return None

    def search_theater_by_id(self, theater_id: str) -> Optional[Theater]:
        for i in self.__theaters_list:
            if i.id == theater_id: return i
        return None

    def search_showtime_by_id(self, showtime_id: str) -> Optional[Showtime]:
        for i in self.__showtime_list:
            if i.id == showtime_id: return i
        return None

    def add_movie(self, movie: Movie):          self.__movies_list.append(movie)
    def add_theater(self, theater: Theater):    self.__theaters_list.append(theater)
    def add_showtime(self, showtime: Showtime): self.__showtime_list.append(showtime)

    def add_goods(self, name: str, values: int, price: float,
                 goods_type: str, flavor: str = None):
        """
        เพิ่มสินค้าเข้า cineplex
        goods_type: "Popcorn" | "Drinks" | "Snack"  (case-insensitive)
        flavor: ต้องระบุสำหรับ Popcorn/Drinks  (optional สำหรับ Snack)
        """
        self.__goods_list.append(Goods.create(name, values, price, goods_type, flavor))

    def search_goods_stock(self, goods_name: str, amount_needed: int = 0) -> Optional[Goods]:
        for item in self.__goods_list:
            if item.get_name() == goods_name:
                if amount_needed == 0 or item.check_values(amount_needed):
                    return item
        return None


class JamorCineplex:
    """
    ระบบจัดการโรงหนัง

    Bank เป็น dependency แยกต่างหาก — inject เข้ามาตอน __init__
    JamorCineplex ไม่สร้าง Bank เอง และไม่รู้จักรายละเอียดบัญชี
    การชำระเงินผ่าน PaymentGateway → Bank ที่ inject มา

    ตัวอย่าง:
        bank   = Bank("KBank")
        system = JamorCineplex(bank)
    """
    def __init__(self, bank: Bank):
        self.__bank          = bank              # Bank inject จากภายนอก
        self.__cineplex_list: List[Cineplex] = []
        self.__user_list:     List[User]     = []
        self.__booking_list:  List[Booking]  = []
        self.__order_list:    List[Order]    = []
        self.__coupon_list:   List[Coupon]   = []
        self.__ticket_list:   List[Ticket]   = []
        self.__order_counter = 1

    # ── properties ──

    @property
    def cineplex_list(self) -> List[Cineplex]: return self.__cineplex_list

    # ── search helpers ──

    def search_cineplex_by_id(self, cineplex_id: str) -> Optional[Cineplex]:
        for i in self.__cineplex_list:
            if i.id == cineplex_id: return i
        return None

    def search_user_by_id(self, user_id: str) -> Optional[User]:
        for i in self.__user_list:
            if i.id == user_id: return i
        return None

    def search_order_by_id(self, order_id: str) -> Optional[Order]:
        for o in self.__order_list:
            if o.get_order_id() == order_id: return o
        return None

    def search_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        for b in self.__booking_list:
            if b.id == booking_id: return b
        return None

    # ── add helpers ──

    def add_cineplex(self, cineplex: Cineplex): self.__cineplex_list.append(cineplex)
    def add_user(self, user: User):             self.__user_list.append(user)
    def get_all_users(self) -> List[User]:      return self.__user_list

    def register_member(self, name: str, birthday: str, member_id: str,
                        registered_date: str, email: str = None,
                        phone_number: str = None,
                        tier: MemberTier = MemberTier.SILVER):
        """
        ลงทะเบียน User ใหม่พร้อมกำหนด tier ทันที
        ค่าเริ่มต้น tier=SILVER (สมาชิกทั่วไปที่เพิ่งสมัคร)
        ใช้ tier=MemberTier.GOLD เป็นต้น สำหรับสมาชิกพิเศษ
        """
        user = User(member_id, name, email or "", phone_number or "", birthday, "")
        user.set_tier(tier)
        self.__user_list.append(user)

    # ── admin process ──

    def process_create_cineplex(self, cineplex_id: str, name: str):
        if self.search_cineplex_by_id(cineplex_id):
            return False, "Cineplex ID already exists."
        self.__cineplex_list.append(Cineplex(cineplex_id, name))
        return True, "Cineplex created successfully."

    def process_create_movie(self, cineplex_id, movie_id, name, duration, genre, age_rating):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex: return False, "Cineplex not found."
        if cineplex.search_movie_by_id(movie_id): return False, "Movie ID already exists."
        cineplex.add_movie(Movie(movie_id, name, duration, genre, age_rating))
        return True, "Movie created successfully."

    def process_create_theater(self, cineplex_id: str, theater_id: str, type_theater: str):
        """
        type_theater รับ string: "Standard" | "IMAX" | "4DX"  (case-insensitive)
        ใช้ TheaterType.from_str() + Theater.create() — ไม่ต้องใช้ subclass
        """
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex: return False, "Cineplex not found."
        if cineplex.search_theater_by_id(theater_id): return False, "Theater ID already exists."
        try:
            cineplex.add_theater(Theater.create(theater_id, type_theater))
        except ValueError as e:
            return False, str(e)
        return True, "Theater created successfully."

    def process_create_seat(self, cineplex_id: str, theater_id: str,
                            seat_id: str, seat_number: str, type_seat: str):
        """
        type_seat รับ string: "Normalseat" | "Sofa" | "Honeymoonbed"  (case-insensitive)
        ใช้ SeatType.from_str() — ไม่ต้องใช้ subclass
        """
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex: return False, "Cineplex not found."
        theater = cineplex.search_theater_by_id(theater_id)
        if not theater: return False, "Theater not found."
        try:
            theater.add_seat(Seat(seat_id, seat_number, SeatType.from_str(type_seat)))
        except ValueError as e:
            return False, str(e)
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

        # แปลง string → datetime  (รูปแบบ: "YYYY-MM-DD HH:MM")
        try:
            dt_start = datetime.strptime(start_time, Showtime.DT_FORMAT)
            dt_end   = datetime.strptime(end_time,   Showtime.DT_FORMAT)
        except ValueError:
            return False, f"Invalid datetime format. Use '{Showtime.DT_FORMAT}' (e.g. '2025-12-31 14:30')"

        if dt_end <= dt_start:
            return False, "end_time must be after start_time"

        # เช็คว่าเวลาทับกับ showtime อื่นใน theater เดียวกันไหม
        if theater.has_conflict(dt_start, dt_end):
            conflict = next(
                st for st in theater.showtime_list
                if dt_start < st.end_time and dt_end > st.start_time
            )
            return False, (
                f"Time conflict in Theater '{theater_id}': "
                f"showtime '{conflict.id}' "
                f"({conflict.start_time.strftime(Showtime.DT_FORMAT)}"
                f" – {conflict.end_time.strftime(Showtime.DT_FORMAT)}) "
                f"overlaps with the requested slot."
            )

        new_showtime = Showtime(showtime_id, movie, theater, status, subtitle,
                                dt_start, dt_end, base_price)
        cineplex.add_showtime(new_showtime)
        theater.add_showtime(new_showtime)
        return True, "Showtime created successfully."

    def process_create_coupon(self, coupon_type, coupon_id, name, discount=0.0,
                              goods_list=None, last_date: str = None):
        dt_last = None
        if last_date:
            try:
                dt_last = datetime.strptime(last_date, "%Y-%m-%d %H:%M")
            except ValueError:
                return False, "Invalid last_date format. Use 'YYYY-MM-DD HH:MM'"

        if coupon_type.lower() == "discount":
            new_coupon = DiscountCoupon(coupon_id, name, discount, dt_last)
        elif coupon_type.lower() == "exchange":
            new_coupon = ExchangeCoupon(coupon_id, name, goods_list or [], dt_last)
        else:
            return False, "Invalid coupon_type. Use 'discount' or 'exchange'."
        self.__coupon_list.append(new_coupon)
        return True, "Coupon created successfully."

    # ── booking process ──

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

    def process_create_booking(self, booking_id: str, user_id: str, cineplex_id: str,
                               showtime_id: str, seat_nos: list):
        user = self.search_user_by_id(user_id)
        if not user: return False, "Member not found"
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex: return False, "Cineplex not found"
        showtime = cineplex.search_showtime_by_id(showtime_id)
        if not showtime: return False, "Showtime not found"
        if self.search_booking_by_id(booking_id): return False, "Booking ID already exists"

        theater = showtime.theater
        seats   = []
        for seat_no in seat_nos:
            if not showtime.is_seat_available(seat_no):
                return False, f"Seat {seat_no} is already booked"
            seat = theater.search_seat_by_no(seat_no)
            if not seat: return False, f"Seat {seat_no} not found in theater"
            seats.append(seat)

        seat_total  = sum(s.type_seat.get_price() for s in seats)
        raw_total   = showtime.base_price + seat_total
        discount    = user.get_discount()
        total_price = round(raw_total * (1 - discount), 2)

        booking = Booking(booking_id, user, showtime, datetime.now(),
                          BookingStatus.PENDING, total_price)
        booking.showtime_seat = showtime.add_seats(seats, BookingStatus.PENDING)
        self.__booking_list.append(booking)
        user.add_booking(booking)
        return True, {
            "booking_id":  booking_id,
            "seats":       seat_nos,
            "total_price": total_price,
            "discount":    int(discount * 100),
        }

    def process_cancel_booking(self, booking_id: str, user_id: str):
        user    = self.search_user_by_id(user_id)
        if not user: return False, "Member not found"
        booking = self.search_booking_by_id(booking_id)
        if not booking: return False, "Booking not found"
        if booking.status == BookingStatus.CANCELLED: return False, "Booking is already cancelled"
        if booking.status == BookingStatus.COMPLETED: return False, "Cannot cancel a completed booking"
        booking.showtime.remove_seats([s.seat_number for s in booking.showtime_seat])
        booking.status = BookingStatus.CANCELLED
        return True, f"Booking {booking_id} cancelled (no refund)"

    def process_confirm_booking(self, booking_id: str, user_id: str, account_id: str):
        user    = self.search_user_by_id(user_id)
        if not user: return False, "Member not found"
        booking = self.search_booking_by_id(booking_id)
        if not booking: return False, "Booking not found"
        if booking.status != BookingStatus.PENDING:
            return False, f"Booking status is '{booking.status.value}', cannot confirm"

        total  = booking.total_price
        result = PaymentGateway(account_id, total).pay(self.__bank)
        if not result: return False, "Failed: Insufficient balance"

        booking.status = BookingStatus.CONFIRMED
        showtime = booking.showtime
        ticket = Ticket(
            booking=booking, cineplex=None, user=user,
            movie=showtime.movie, theater=showtime.theater,
            showtime=showtime, seat_list=booking.showtime_seat,
        )
        booking.ticket = ticket
        user.add_ticket(ticket)
        self.__ticket_list.append(ticket)
        points = len(booking.showtime_seat) * 10
        user.add_point(points)
        return True, f"Confirm booking success | Total Paid: {total} THB | Points earned: {points}"

    def process_change_booking(self, user_id: str, booking_id: str, new_seat_nos: list):
        user    = self.search_user_by_id(user_id)
        if not user: return None, "User not found"
        booking = user.search_booking_by_id(booking_id)
        if not booking: return None, "Booking not found"

        current_seats = [s.seat_number for s in booking.showtime_seat]
        if len(new_seat_nos) != len(current_seats):
            return None, f"Validation Error: Must select exactly {len(current_seats)} seats"
        if len(new_seat_nos) != len(set(new_seat_nos)):
            return None, "Validation Error: Duplicate seats requested"

        showtime       = booking.showtime
        theater        = showtime.theater
        booking_status = booking.status
        old_total      = booking.total_price
        new_real_seats = []
        new_total      = 0.0

        for seat_no in new_seat_nos:
            if seat_no not in current_seats:
                if not showtime.is_seat_available(seat_no):
                    return None, f"Seat {seat_no} is already booked"
            seat = theater.search_seat_by_no(seat_no)
            if not seat: return None, f"Seat {seat_no} not found in theater"
            new_total += seat.type_seat.get_price()
            new_real_seats.append(seat)

        new_total = round(new_total * (1 - user.get_discount()), 2)

        if booking_status == BookingStatus.CONFIRMED:
            if new_total > old_total: return None, "Cannot change to more expensive seats"
            showtime.remove_seats(current_seats)
            new_st = showtime.add_seats(new_real_seats, BookingStatus.CONFIRMED)
            booking.showtime_seat = new_st
            booking.total_price   = new_total
            if booking.ticket: booking.ticket.seat_list = new_st
            return booking, "Change booking (Confirmed) successful"

        elif booking_status == BookingStatus.PENDING:
            showtime.remove_seats(current_seats)
            new_st = showtime.add_seats(new_real_seats, BookingStatus.PENDING)
            booking.showtime_seat = new_st
            booking.total_price   = new_total
            return booking, "Change booking (Pending) successful"

        return None, "Invalid booking status"

    # ── order process ──

    def process_order_goods(self, cineplex_id, goods_name, values, user_id,
                            account_id, coupon_id=None):
        member = self.search_user_by_id(user_id)
        if not member: return False, "Member not found"
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex: return False, "Cineplex not found"
        target_good = cineplex.search_goods_stock(goods_name, values)
        if not target_good: return False, "Out of stock or Not enough items"

        discount_amount = 0
        used_coupon_id  = None
        if coupon_id:
            for c in self.__coupon_list:
                if c.get_coupon_id() == coupon_id:
                    if c.is_expired():
                        last = c.last_date.strftime("%Y-%m-%d %H:%M") if c.last_date else "-"
                        return False, f"Coupon '{coupon_id}' has expired (last_date: {last})"
                    discount_amount = c.get_discount()
                    used_coupon_id  = coupon_id
                    c.update_status("Used")
                    break
            else:
                return False, f"Coupon '{coupon_id}' not found"

        total_price = max((target_good.get_price() * values) - discount_amount, 0)
        order_id    = f"ORD-{self.__order_counter:04d}"
        self.__order_counter += 1

        order   = Order(order_id, goods_name, values, account_id, total_price, used_coupon_id)
        gateway = PaymentGateway(account_id, total_price)
        if order.pay(self.__bank, gateway):
            target_good.clearstock(values)
            self.__order_list.append(order)
            return True, {"order_id": order_id, "total_paid": total_price}
        return False, "Payment failed: Insufficient balance or invalid account."

    def process_cancel_order(self, cineplex_id, order_id, user_id):
        member = self.search_user_by_id(user_id)
        if not member: return False, "Member not found"
        order  = self.search_order_by_id(order_id)
        if not order: return False, "Order not found"

        current_status = order.get_status()
        if current_status == OrderStatus.CANCELLED.value: return False, "Order is already cancelled"
        if current_status == OrderStatus.REFUNDED.value:  return False, "Order has already been refunded"

        if current_status == OrderStatus.COMPLETED.value:
            account_id, total_paid = order.get_payment_details()
            if self.__bank.refund(account_id, total_paid):
                goods_name, values = order.get_items()
                cineplex = self.search_cineplex_by_id(cineplex_id)
                if cineplex:
                    g = cineplex.search_goods_stock(goods_name)
                    if g: g.restore_stock(values)
                cid = order.get_used_coupon()
                if cid:
                    for c in self.__coupon_list:
                        if c.get_coupon_id() == cid:
                            c.update_status("Available")
                            break
                order.update_status(OrderStatus.CANCELLED)
                return True, f"Cancel success, Refund {total_paid} THB"
            return False, "Refund failed"
        return False, "Cannot cancel order with current status"


## ── SECTION: MOCK_DATA ────────────────────────────────────────────────────
# Bank เป็น object แยก — สร้างก่อน แล้ว inject เข้า JamorCineplex
# Theater ใช้ Theater.create(id, "Standard")  แทน StandardTheater(id)
# Seat    ใช้ Seat(id, no, SeatType.NORMALSEAT)  แทน NormalSeat(id, no)

kbank = Bank("KBank")
kbank.create_account("J", "A123", balance=5000)

system = JamorCineplex(kbank)   # inject bank เข้า system

# Cineplex C – goods only
cineplex_c = Cineplex("CPX_C", "C")
cineplex_c.add_goods("Popcorn", 100, 50, "Popcorn", flavor="Cheese")
system.add_cineplex(cineplex_c)

# Cineplex Siam Paragon
cineplex_siam = Cineplex("CPX01", "Siam Paragon")
theater1 = Theater.create("T01", "Standard")               # ← ไม่ต้องใช้ StandardTheater
theater1.add_seat(Seat("S01", "A1", SeatType.NORMALSEAT))  # ← ไม่ต้องใช้ NormalSeat
theater1.add_seat(Seat("S02", "A2", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S03", "B1", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S04", "B2", SeatType.NORMALSEAT))
cineplex_siam.add_theater(theater1)

movie1    = Movie("M01", "The Matrix", 120, "Sci-Fi", "13+")
showtime1 = Showtime(
    "ST01", movie1, theater1, "Active", "TH",
    start_time = datetime(2026, 3, 10, 10, 0),
    end_time   = datetime(2026, 3, 10, 12, 0),
    base_price = 200,
)
cineplex_siam.add_showtime(showtime1)
theater1.add_showtime(showtime1)    # ลงทะเบียนใน theater เพื่อ conflict check
system.add_cineplex(cineplex_siam)

# Users
system.register_member("J", "01-01-1990", "M001", "2023-01-01")
user1 = User("U01", "Ken", "ken@mail.com", "081", "2000-01-01", "1234")
system.add_user(user1)

# Coupons
system.process_create_coupon("discount", "C10", "Discount 10", discount=10)
system.process_create_coupon("discount", "C20", "Discount 20 (limited)", discount=20,
                             last_date="2026-12-31 23:59")

# Pre-existing booking
_init_seats = [theater1.search_seat_by_no("A1"), theater1.search_seat_by_no("A2")]
booking1    = Booking("BK01", user1, showtime1, datetime.now(), BookingStatus.PENDING, 400.0)
booking1.showtime_seat = showtime1.add_seats(_init_seats, BookingStatus.PENDING)
user1.add_booking(booking1)


## ── SECTION: SCHEMAS ──────────────────────────────────────────────────────

class CineplexCreate(BaseModel):
    cineplex_id: str
    name: str

class MovieCreate(BaseModel):
    cineplex_id: str
    movie_id: str
    name: str
    duration: int
    genre: str
    age_rating: str

class TheaterCreate(BaseModel):
    cineplex_id: str
    theater_id: str
    type_theater: str   # "Standard" | "IMAX" | "4DX"  (case-insensitive)

class SeatCreate(BaseModel):
    cineplex_id: str
    theater_id: str
    seat_id: str
    seat_number: str
    type_seat: str      # "Normalseat" | "Sofa" | "Honeymoonbed"  (case-insensitive)

class ShowtimeCreate(BaseModel):
    cineplex_id: str
    showtime_id: str
    movie_id: str
    theater_id: str
    status: str
    subtitle: str
    start_time: str   # "YYYY-MM-DD HH:MM"
    end_time: str     # "YYYY-MM-DD HH:MM"
    base_price: float

class CouponCreate(BaseModel):
    coupon_type: str
    coupon_id: str
    name: str
    discount: float = 0.0
    goods_list: List[str] = []
    last_date: Optional[str] = None   # "YYYY-MM-DD HH:MM"  หรือ null

class OrderGoodsRequest(BaseModel):
    cineplex_id: str
    goods_name: str
    quantity: int
    user_id: str
    account_id: str
    coupon_id: Optional[str] = None

class BookingCreate(BaseModel):
    booking_id: str
    user_id: str
    cineplex_id: str
    showtime_id: str
    seat_nos: List[str]

class BookingConfirm(BaseModel):
    user_id: str
    account_id: str

class BookingChangeSeats(BaseModel):
    user_id: str
    new_seat_nos: List[str]


## ── SECTION: APP ──────────────────────────────────────────────────────────

app = FastAPI(
    title="JamorCineplex API",
    description="API สำหรับระบบจัดการโรงภาพยนตร์และระบบการจองที่นั่ง",
    version="1.0.0",
)

admin_router   = APIRouter(prefix="/admin",   tags=["Cinema Management"])
store_router   = APIRouter(prefix="/store",   tags=["Store"])
booking_router = APIRouter(prefix="/booking", tags=["Booking"])
user_router    = APIRouter(prefix="/users",   tags=["Users"])


## ── SECTION: ROUTES_ADMIN ─────────────────────────────────────────────────

@admin_router.post("/cineplex/")
def create_cineplex(cineplex_id: str, name: str):
    success, msg = system.process_create_cineplex(cineplex_id, name)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.post("/movie/")
def create_movie(cineplex_id: str, movie_id: str, name: str,
                 duration: int, genre: str, age_rating: str):
    success, msg = system.process_create_movie(cineplex_id, movie_id, name, duration, genre, age_rating)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.post("/theater/")
def create_theater(cineplex_id: str, theater_id: str, type_theater: str):
    """**type_theater**: `Standard` | `IMAX` | `4DX`  (case-insensitive)"""
    success, msg = system.process_create_theater(cineplex_id, theater_id, type_theater)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.post("/seat/")
def create_seat(cineplex_id: str, theater_id: str, seat_id: str,
                seat_number: str, type_seat: str):
    """**type_seat**: `Normalseat` | `Sofa` | `Honeymoonbed`  (case-insensitive)"""
    success, msg = system.process_create_seat(cineplex_id, theater_id, seat_id, seat_number, type_seat)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.post("/showtime/")
def create_showtime(cineplex_id: str, showtime_id: str, movie_id: str, theater_id: str,
                    status: str, subtitle: str, start_time: str, end_time: str, base_price: float):
    """
    **start_time / end_time** format: `YYYY-MM-DD HH:MM`  เช่น `2026-03-10 14:30`
    ระบบเช็ค time conflict อัตโนมัติ
    """
    success, msg = system.process_create_showtime(
        cineplex_id, showtime_id, movie_id, theater_id,
        status, subtitle, start_time, end_time, base_price,
    )
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.post("/coupon/")
def create_coupon(coupon_type: str, coupon_id: str, name: str,
                  discount: float = 0.0,
                  goods_list: List[str] = Query(default=[]),
                  last_date: Optional[str] = None):
    """**last_date** format: `YYYY-MM-DD HH:MM`  ละไว้ = ไม่มีวันหมดอายุ"""
    success, msg = system.process_create_coupon(coupon_type, coupon_id, name, discount,
                                                goods_list, last_date)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.get("/showtimes/")
def get_all_showtimes():
    """แสดงรอบฉายที่ยังไม่เริ่ม (start_time >= ปัจจุบัน)"""
    now    = datetime.now()
    result = []
    for cineplex in system.cineplex_list:
        for showtime in cineplex.showtime_list:
            if showtime.is_upcoming():
                result.append({
                    "cineplex_name": cineplex.get_cineplex_name(),
                    "showtime_id":   showtime.id,
                    "movie_name":    showtime.movie.name,
                    "theater_id":    showtime.theater.id,
                    "theater_type":  showtime.theater.type_theater.value,
                    "start_time":    showtime.start_time.strftime(Showtime.DT_FORMAT),
                    "end_time":      showtime.end_time.strftime(Showtime.DT_FORMAT),
                    "price":         showtime.base_price,
                })
    return {
        "current_datetime": now.strftime(Showtime.DT_FORMAT),
        "total_available":  len(result),
        "showtimes":        result,
    }


## ── SECTION: ROUTES_STORE ─────────────────────────────────────────────────

@store_router.post("/order/")
def order_goods(cineplex_id: str, goods_name: str, quantity: int,
                user_id: str, account_id: str, coupon_id: Optional[str] = None):
    success, msg = system.process_order_goods(cineplex_id, goods_name, quantity,
                                              user_id, account_id, coupon_id)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": "Order successful", "data": msg}


@store_router.delete("/order/{cineplex_id}/{order_id}")
def cancel_order(cineplex_id: str, order_id: str, user_id: str):
    success, msg = system.process_cancel_order(cineplex_id, order_id, user_id)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


## ── SECTION: ROUTES_BOOKING ───────────────────────────────────────────────

@booking_router.post("/")
def create_booking(booking_id: str, user_id: str, cineplex_id: str, showtime_id: str,
                   seat_nos: List[str] = Query(..., description="รายการที่นั่ง เช่น A1, A2")):
    success, msg = system.process_create_booking(booking_id, user_id, cineplex_id,
                                                 showtime_id, seat_nos)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": "Booking created", "data": msg}


@booking_router.post("/{booking_id}/confirm")
def confirm_booking(booking_id: str, user_id: str, account_id: str):
    success, msg = system.process_confirm_booking(booking_id, user_id, account_id)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@booking_router.delete("/{booking_id}")
def cancel_booking(booking_id: str, user_id: str):
    success, msg = system.process_cancel_booking(booking_id, user_id)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@booking_router.put("/{booking_id}/seats")
def change_booking_seats(booking_id: str, user_id: str,
                         new_seat_nos: List[str] = Query(...)):
    booking, msg = system.process_change_booking(user_id, booking_id, new_seat_nos)
    if not booking: raise HTTPException(status_code=400, detail=msg)
    return {
        "message":     msg,
        "booking_id":  booking.id,
        "status":      booking.status.value,
        "new_seats":   [s.seat_number for s in booking.showtime_seat],
        "total_price": booking.total_price,
    }


## ── SECTION: ROUTES_USERS ─────────────────────────────────────────────────

@user_router.get("/")
def get_all_users():
    result = [
        {"id": u.id, "name": u.name, "tier": u.tier.value, "points": u.get_point()}
        for u in system.get_all_users()
    ]
    return {"users": result}


@user_router.get("/{user_id}/bookings")
def get_user_bookings(user_id: str, status_filter: Optional[str] = None):
    success, msg, data = system.process_get_booking_history(user_id, status_filter)
    if not success: raise HTTPException(status_code=400, detail=msg)
    user, bookings = data
    result = [{
        "booking_id": b.id,
        "movie":      b.showtime.movie.name,
        "status":     b.status.value,
        "seats":      [s.seat_number for s in b.showtime_seat],
        "price":      b.total_price,
    } for b in bookings]
    return {"member": user.name, "tier": user.tier.value, "bookings": result}


## ── SECTION: ENTRYPOINT ───────────────────────────────────────────────────

app.include_router(admin_router)
app.include_router(store_router)
app.include_router(booking_router)
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)