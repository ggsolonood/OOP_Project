from datetime import datetime
from typing import List, Optional
from enums import BookingStatus, MemberTier
from theater import Showtime, ShowtimeSeat, Movie, Theater


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
        self.__type_user      = MemberTier.GUEST

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
        self.__type_user = tier

    def search_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        for b in self.__booking_list:
            if b.id == booking_id:
                return b
        return None
