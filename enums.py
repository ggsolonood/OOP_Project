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
    BOOKED = "Booked"       
    OCCUPIED = "Occupied"   

class SeatType(Enum):
    NORMALSEAT = "Normalseat"
    SOFA = "Sofa"
    HONEYMOONBED = "Honeymoonbed"

class BookingStatus(Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class TicketStatus(Enum):
    UNUSED = "Unused"
    USED = "Used"
    CANCELLED = "Cancelled"

class GoodsType(Enum):
    POPCORN = "Popcorn"
    DRINKS = "Drinks"
    SNACK = "Snack"

class TheaterType(Enum):
    STANDARD = "Standard"
    IMAX = "IMAX"
    _4DX = "4DX"

class Genre(Enum):
    ACTION = "Action"
    COMEDY = "Comedy"
    SCI_FI = "Sci-Fi"
    DRAMA = "Drama"