from enum import Enum


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
