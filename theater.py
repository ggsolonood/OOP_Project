from typing import List, Optional
from datetime import datetime , timedelta
from enums import SeatType, TheaterType, BookingStatus


class Seat:
    def __init__(self, seat_id: str, seat_number: str, type_seat: SeatType):
        self.__seat_id     = seat_id
        self.__seat_number = seat_number
        self.__type_seat   = (type_seat if isinstance(type_seat, SeatType)
                              else SeatType.from_str(str(type_seat)))

    @property
    def id(self) -> str:
        return self.__seat_id

    @property
    def seat_number(self) -> str:
        return self.__seat_number

    @property
    def type_seat(self) -> SeatType:
        return self.__type_seat


class Theater:
    def __init__(self, theater_id: str, type_theater: TheaterType):
        self.__theater_id    = theater_id
        self.__seats_list:   List[Seat] = []
        self.__type_theater  = (type_theater if isinstance(type_theater, TheaterType)
                                else TheaterType.from_str(str(type_theater)))
        self.__showtime_list: list      = []

    @classmethod
    def create(cls, theater_id: str, type_str: str) -> "Theater":
        return cls(theater_id, TheaterType.from_str(type_str))

    @property
    def id(self) -> str:
        return self.__theater_id

    @property
    def type_theater(self) -> TheaterType:
        return self.__type_theater

    @property
    def showtime_list(self) -> list:
        return self.__showtime_list

    @property
    def seats_list(self) -> List[Seat]:
        return self.__seats_list

    def add_seat(self, seat: Seat):
        self.__seats_list.append(seat)

    def search_seat_by_no(self, seat_no: str) -> Optional[Seat]:
        for s in self.__seats_list:
            if s.seat_number == seat_no:
                return s
        return None

    def add_showtime(self, showtime):
        self.__showtime_list.append(showtime)

    def has_conflict(self, dt_start: datetime, dt_end: datetime) -> bool:
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
        self.__review = []

    @property
    def id(self) -> str:
        return self.__movie_id

    @property
    def name(self) -> str:
        return self.__movie_name
    
    def add_review(self,review) :
        self.__review.append(review)

    @property
    def duration(self) :
        return self.__duration

class ShowtimeSeat(Seat):
    def __init__(self, seat: Seat, status: BookingStatus):
        super().__init__(seat.id, seat.seat_number, seat.type_seat)
        self.__status = status

    @property
    def status(self) -> BookingStatus:
        return self.__status


class Showtime:
    DT_FORMAT = "%Y-%m-%d %H:%M"

    def __init__(self, showtime_id: str, movie: Movie, theater: Theater,
                 status: str, subtitle: str,
                 start_time: datetime, base_price: float):
        self.__id            = showtime_id
        self.__movie         = movie
        self.__theater       = theater
        self.__status        = status
        self.__subtitle      = subtitle
        self.__start_time    = start_time
        self.__base_price    = base_price
        self.__showtime_seat: List[ShowtimeSeat] = []

    @property
    def id(self) -> str:
        return self.__id

    @property
    def movie(self) -> Movie:
        return self.__movie

    @property
    def theater(self) -> Theater:
        return self.__theater

    @property
    def status(self) -> str:
        return self.__status

    @property
    def subtitle(self) -> str:
        return self.__subtitle

    @property
    def base_price(self) -> float:
        return self.__base_price

    @property
    def start_time(self) -> datetime:
        return self.__start_time

    @property
    def end_time(self) -> datetime:
        return self.__start_time + timedelta(minutes=self.__movie.duration)

    def is_upcoming(self) -> bool:
        return self.__start_time >= datetime.now()

    def get_booked_seat_numbers(self) -> List[str]:
        return [s.seat_number for s in self.__showtime_seat]

    def get_available_seats(self) -> List[dict]:
        booked = self.get_booked_seat_numbers()
        return [
            {
                "seat_number": s.seat_number,
                "type":        s.type_seat.value,
                "price":       s.type_seat.get_price(),
            }
            for s in self.__theater.seats_list
            if s.seat_number not in booked
        ]

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

class Review :
    def __init__(self,star,comment,author):
        self.__star = star
        self.__comment = comment
        self.__author = author

    @property
    def read(self) :
        return f"{self.__author} {self.__star} ⭐\n\t{self.__comment}"