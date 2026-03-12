from enum import Enum

class MemberTier(Enum):
    GUEST = "Guest"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"

class OrderStatus(Enum):
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class SeatStatus(Enum):
    BOOKED = "Booked"       # ถูกจอง (รอจ่ายเงิน)
    OCCUPIED = "Occupied"   # จ่ายเงินแล้ว

class SeatType(Enum):
    NORMALSEAT = "Normalseat"
    SOFA = "Sofa"
    HONEYMOONBED = "Honeymoonbed"

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