from enums import MemberTier, BookingStatus


class Booking:
    def __init__(self, booking_id, user, showtime, timestamp,
                 status: BookingStatus, total_price=0.0):
        self.__booking_id = booking_id
        self.__user = user
        self.__showtime = showtime
        self.__ticket = None
        self.__timestamp = timestamp
        self.__showtime_seat = []
        self.__status = status
        self.__total_price = total_price

    @property
    def id(self):
        return self.__booking_id

    @property
    def showtime(self):
        return self.__showtime

    @property
    def status(self):
        return self.__status

    @property
    def showtime_seat(self):
        return self.__showtime_seat

    @property
    def total_price(self):
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


class Ticket:
    def __init__(self, booking, cineplex, user, movie, theater, showtime, seat_list):
        self.__booking = booking
        self.__cineplex = cineplex
        self.__user = user
        self.__movie = movie
        self.__theater = theater
        self.__showtime = showtime
        self.seat_list = seat_list


class User:
    def __init__(self, id, name, email, phone_number, birthday, password):
        self.__id = id
        self.__name = name
        self.__email = email
        self.__phone_number = phone_number
        self.__birthday = birthday
        self.__password = password
        self.__point = 0
        self.__coupon_list = []
        self.__ticket_list = []
        self.__booking_list = []
        self.__total_spending = 0
        self.__type_user = MemberTier.GUEST

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def booking_list(self):
        return self.__booking_list

    @property
    def tier(self):
        return self.__type_user

    def get_member_id(self):
        return self.__id

    def get_discount(self):
        return self.__type_user.get_discount()

    def add_point(self, point: int):
        self.__point += point

    def get_point(self):
        return self.__point

    def add_booking(self, booking):
        self.__booking_list.append(booking)

    def add_ticket(self, ticket):
        self.__ticket_list.append(ticket)

    def search_booking_by_id(self, booking_id):
        for b in self.__booking_list:
            if b.id == booking_id:
                return b
        return None


class Member(User):
    def __init__(self, name, birthday, member_id, registered_date,
                 email=None, phone_number=None):
        super().__init__(member_id, name, email or "", phone_number or "", birthday, "")
        self._birthday = birthday
