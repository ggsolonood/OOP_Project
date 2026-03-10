from enums import SeatType, TheaterType, BookingStatus


class Seat:
    def __init__(self, seat_id, seat_number, type_seat):
        self.__seat_id = seat_id
        self.__seat_number = seat_number
        self.__type_seat = type_seat

    @property
    def id(self):
        return self.__seat_id

    @property
    def seat_number(self):
        return self.__seat_number

    @property
    def type_seat(self):
        return self.__type_seat


class NormalSeat(Seat):
    def __init__(self, seat_id, seat_number):
        super().__init__(seat_id, seat_number, SeatType.NORMALSEAT)


class SofaSeat(Seat):
    def __init__(self, seat_id, seat_number):
        super().__init__(seat_id, seat_number, SeatType.SOFA)


class HoneyMoonBed(Seat):
    def __init__(self, seat_id, seat_number):
        super().__init__(seat_id, seat_number, SeatType.HONEYMOONBED)


class ShowtimeSeat(Seat):
    def __init__(self, seat: Seat, status: BookingStatus):
        super().__init__(seat.id, seat.seat_number, seat.type_seat)
        self.__status = status

    @property
    def status(self):
        return self.__status


class Theater:
    def __init__(self, theater_id, type_theater):
        self.__theater_id = theater_id
        self.__seats_list = []
        self.__type_theater = type_theater

    @property
    def id(self):
        return self.__theater_id

    def add_seat(self, seat):
        self.__seats_list.append(seat)

    def search_seat_by_no(self, seat_no):
        for s in self.__seats_list:
            if s.seat_number == seat_no:
                return s
        return None


class StandardTheater(Theater):
    def __init__(self, theater_id, seat_list=None):
        super().__init__(theater_id, TheaterType.STANDARD)
        if seat_list:
            for s in seat_list:
                self.add_seat(s)


class IMAXTheater(Theater):
    def __init__(self, theater_id, seat_list=None):
        super().__init__(theater_id, TheaterType.IMAX)
        if seat_list:
            for s in seat_list:
                self.add_seat(s)


class FourDXTheater(Theater):
    def __init__(self, theater_id, seat_list=None):
        super().__init__(theater_id, TheaterType._4DX)
        if seat_list:
            for s in seat_list:
                self.add_seat(s)


class Movie:
    def __init__(self, id, name, duration, genre, age_rating):
        self.__movie_id = id
        self.__movie_name = name
        self.__duration = duration
        self.__genre = genre
        self.__age_rating = age_rating

    @property
    def id(self):
        return self.__movie_id

    @property
    def name(self):
        return self.__movie_name


class Showtime:
    def __init__(self, showtime_id, movie, theater, status, subtitle,
                 start_time, end_time, base_price):
        self.__id = showtime_id
        self.__movie = movie
        self.__theater = theater
        self.__status = status
        self.__subtitle = subtitle
        self.__start_time = start_time
        self.__end_time = end_time
        self.__base_price = base_price
        self.__showtime_seat = []

    @property
    def id(self):
        return self.__id

    @property
    def movie(self):
        return self.__movie

    @property
    def theater(self):
        return self.__theater

    @property
    def status(self):
        return self.__status

    @property
    def subtitle(self):
        return self.__subtitle

    @property
    def base_price(self):
        return self.__base_price

    def is_seat_available(self, seat_no):
        for s in self.__showtime_seat:
            if s.seat_number == seat_no:
                return False
        return True

    def remove_seats(self, seat_nos: list):
        self.__showtime_seat = [
            s for s in self.__showtime_seat if s.seat_number not in seat_nos
        ]

    def add_seats(self, seats: list, status: BookingStatus):
        new_seats = []
        for s in seats:
            st_seat = ShowtimeSeat(s, status)
            self.__showtime_seat.append(st_seat)
            new_seats.append(st_seat)
        return new_seats
