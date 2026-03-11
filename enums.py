from enum import Enum


class OrderStatus(Enum):
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    REFUNDED  = "Refunded"


class SeatType(Enum):
    NORMALSEAT   = "Normalseat"
    SOFA         = "Sofa"
    HONEYMOONBED = "Honeymoonbed"

    @classmethod
    def from_str(cls, value: str) -> "SeatType":
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
    POPCORN = "Popcorn"
    DRINKS  = "Drinks"
    SNACK   = "Snack"

    @classmethod
    def from_str(cls, value: str) -> "GoodsType":
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
        return self in (GoodsType.POPCORN, GoodsType.DRINKS)


class TheaterType(Enum):
    STANDARD = "Standard"
    IMAX     = "IMAX"
    _4DX     = "4DX"

    @classmethod
    def from_str(cls, value: str) -> "TheaterType":
        mapping = {t.value.lower(): t for t in cls}
        result  = mapping.get(value.strip().lower())
        if result is None:
            raise ValueError(
                f"Unknown TheaterType '{value}'. "
                f"Valid values: {[t.value for t in cls]}"
            )
        return result
