from datetime import datetime

from enums import BookingStatus, MemberTier, OrderStatus, TheaterType
from goods import Coupon, DiscountCoupon, ExchangeCoupon, Popcorn, Drinks, Snack
from payment import Bank, Order, PaymentGateway
from theater import Movie, Seat, Showtime, Theater
from user import Booking, Member, Ticket, User


class Cineplex:
    def __init__(self, cineplex_id, name):
        self.__cineplex_id = cineplex_id
        self.__name = name
        self.__movies_list = []
        self.__theaters_list = []
        self.__showtime_list = []
        self.__goods_list = []

    @property
    def id(self):
        return self.__cineplex_id

    def get_cineplex_name(self):
        return self.__name

    @property
    def showtime_list(self):
        return self.__showtime_list

    def search_movie_by_id(self, movie_id):
        for i in self.__movies_list:
            if i.id == movie_id:
                return i
        return None

    def search_theater_by_id(self, theater_id):
        for i in self.__theaters_list:
            if i.id == theater_id:
                return i
        return None

    def search_showtime_by_id(self, showtime_id):
        for i in self.__showtime_list:
            if i.id == showtime_id:
                return i
        return None

    def add_movie(self, movie):
        self.__movies_list.append(movie)

    def add_theater(self, theater):
        self.__theaters_list.append(theater)

    def add_showtime(self, showtime):
        self.__showtime_list.append(showtime)

    def add_popcorn(self, name, values: int, price, flavor):
        self.__goods_list.append(Popcorn(name, values, price, flavor))

    def add_drinks(self, name, values: int, price, flavor):
        self.__goods_list.append(Drinks(name, values, price, flavor))

    def add_snack(self, name, values: int, price):
        self.__goods_list.append(Snack(name, values, price))

    def search_goods_stock(self, goods_name, amount_needed=0):
        for item in self.__goods_list:
            if item.get_name() == goods_name:
                if amount_needed == 0 or item.check_values(amount_needed):
                    return item
        return None


class JamorCineplex:
    def __init__(self, bank: Bank):
        self.__bank = bank
        self.__cineplex_list = []
        self.__user_list = []
        self.__booking_list = []
        self.__order_list = []
        self.__coupon_list = []
        self.__ticket_list = []
        self.__order_counter = 1

    def search_cineplex_by_id(self, cineplex_id):
        for i in self.__cineplex_list:
            if i.id == cineplex_id:
                return i
        return None

    @property
    def cineplex_list(self):
        return self.__cineplex_list

    def search_user_by_id(self, user_id):
        for i in self.__user_list:
            if i.id == user_id:
                return i
        return None

    def search_order_by_id(self, order_id):
        for o in self.__order_list:
            if o.get_order_id() == order_id:
                return o
        return None

    def search_booking_by_id(self, booking_id):
        for b in self.__booking_list:
            if b.id == booking_id:
                return b
        return None

    def add_cineplex(self, cineplex: Cineplex):
        self.__cineplex_list.append(cineplex)

    def add_user(self, user):
        self.__user_list.append(user)

    def get_all_users(self):
        return self.__user_list

    def register_member(self, name, birthday, member_id, registered_date,
                        email=None, phone_number=None):
        self.__user_list.append(
            Member(name, birthday, member_id, registered_date, email, phone_number)
        )

    # --- Admin processes ---

    def process_create_cineplex(self, cineplex_id, name):
        if self.search_cineplex_by_id(cineplex_id):
            return False, "Cineplex ID already exists."
        self.__cineplex_list.append(Cineplex(cineplex_id, name))
        return True, "Cineplex created successfully."

    def process_create_movie(self, cineplex_id, movie_id, name, duration, genre, age_rating):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex:
            return False, "Cineplex not found."
        if cineplex.search_movie_by_id(movie_id):
            return False, "Movie ID already exists in this Cineplex."
        cineplex.add_movie(Movie(movie_id, name, duration, genre, age_rating))
        return True, "Movie created successfully."

    def process_create_theater(self, cineplex_id, theater_id, type_theater):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex:
            return False, "Cineplex not found."
        if cineplex.search_theater_by_id(theater_id):
            return False, "Theater ID already exists."
        cineplex.add_theater(Theater(theater_id, type_theater))
        return True, "Theater created successfully."

    def process_create_seat(self, cineplex_id, theater_id, seat_id, seat_number, type_seat):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex:
            return False, "Cineplex not found."
        theater = cineplex.search_theater_by_id(theater_id)
        if not theater:
            return False, "Theater not found."
        theater.add_seat(Seat(seat_id, seat_number, type_seat))
        return True, "Seat created successfully."

    def process_create_showtime(self, cineplex_id, showtime_id, movie_id, theater_id,
                                 status, subtitle, start_time, end_time, base_price):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex:
            return False, "Cineplex not found."
        movie = cineplex.search_movie_by_id(movie_id)
        if not movie:
            return False, "Movie not found."
        theater = cineplex.search_theater_by_id(theater_id)
        if not theater:
            return False, "Theater not found."
        if cineplex.search_showtime_by_id(showtime_id):
            return False, "Showtime ID already exists."
        cineplex.add_showtime(
            Showtime(showtime_id, movie, theater, status, subtitle, start_time, end_time, base_price)
        )
        return True, "Showtime created successfully."

    def process_create_coupon(self, coupon_type, coupon_id, name, discount=0.0, goods_list=None):
        if coupon_type.lower() == "discount":
            new_coupon = DiscountCoupon(coupon_id, name, discount)
        elif coupon_type.lower() == "exchange":
            new_coupon = ExchangeCoupon(coupon_id, name, goods_list or [])
        else:
            return False, "Invalid coupon_type. Use 'discount' or 'exchange'."
        self.__coupon_list.append(new_coupon)
        return True, "Coupon created successfully."

    # --- Booking processes ---

    def process_get_booking_history(self, user_id: str, status_filter: str = None):
        user = self.search_user_by_id(user_id)
        if not user:
            return False, "Member not found", None
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

    def process_create_booking(self, booking_id: str, user_id: str, cineplex_id,
                                showtime_id: str, seat_nos: list):
        user = self.search_user_by_id(user_id)
        if not user:
            return False, "Member not found"
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex:
            return False, "Cineplex not found"
        showtime = cineplex.search_showtime_by_id(showtime_id)
        if not showtime:
            return False, "Showtime not found"
        if self.search_booking_by_id(booking_id):
            return False, "Booking ID already exists"

        theater = showtime.theater
        seats = []
        for seat_no in seat_nos:
            if not showtime.is_seat_available(seat_no):
                return False, f"Seat {seat_no} is already booked"
            seat = theater.search_seat_by_no(seat_no)
            if not seat:
                return False, f"Seat {seat_no} not found in theater"
            seats.append(seat)

        base_price = showtime.base_price
        seat_total = sum(s.type_seat.get_price() for s in seats)
        raw_total = base_price + seat_total
        discount = user.get_discount()
        total_price = round(raw_total * (1 - discount), 2)

        booking = Booking(booking_id, user, showtime, datetime.now(),
                          BookingStatus.PENDING, total_price)
        booked_seats = showtime.add_seats(seats, BookingStatus.PENDING)
        booking.showtime_seat = booked_seats
        self.__booking_list.append(booking)
        user.add_booking(booking)

        return True, {
            "booking_id": booking_id,
            "seats": seat_nos,
            "total_price": total_price,
            "discount": int(discount * 100),
        }

    def process_cancel_booking(self, booking_id: str, user_id: str):
        user = self.search_user_by_id(user_id)
        if not user:
            return False, "Member not found"
        booking = self.search_booking_by_id(booking_id)
        if not booking:
            return False, "Booking not found"
        if booking.status == BookingStatus.CANCELLED:
            return False, "Booking is already cancelled"
        if booking.status == BookingStatus.COMPLETED:
            return False, "Cannot cancel a completed booking"

        seat_nos = [s.seat_number for s in booking.showtime_seat]
        booking.showtime.remove_seats(seat_nos)
        booking.status = BookingStatus.CANCELLED
        return True, f"Booking {booking_id} cancelled (no refund)"

    def process_confirm_booking(self, booking_id: str, user_id: str, account_id: str):
        user = self.search_user_by_id(user_id)
        if not user:
            return False, "Member not found"
        booking = self.search_booking_by_id(booking_id)
        if not booking:
            return False, "Booking not found"
        if booking.status != BookingStatus.PENDING:
            return False, f"Booking status is '{booking.status.value}', cannot confirm"

        total = booking.total_price
        gateway = PaymentGateway(account_id, total)
        result = gateway.pay(self.__bank)

        if result is True:
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
            points_earned = len(booking.showtime_seat) * 10
            user.add_point(points_earned)
            return True, f"Confirm booking success | Total Paid: {total} THB | Points earned: {points_earned}"
        else:
            return False, "Failed: Insufficient balance"

    def process_change_booking(self, user_id: str, booking_id: str, new_seat_nos: list):
        user = self.search_user_by_id(user_id)
        if not user:
            return None, "User not found"
        booking = user.search_booking_by_id(booking_id)
        if not booking:
            return None, "Booking not found"

        current_seats = [s.seat_number for s in booking.showtime_seat]
        if len(new_seat_nos) != len(current_seats):
            return None, f"Validation Error: Must select exactly {len(current_seats)} seats"
        if len(new_seat_nos) != len(set(new_seat_nos)):
            return None, "Validation Error: Duplicate seats requested"

        showtime = booking.showtime
        theater = showtime.theater
        booking_status = booking.status
        old_total_price = booking.total_price
        new_real_seats = []
        new_total_price = 0.0

        for seat_no in new_seat_nos:
            if seat_no not in current_seats:
                if not showtime.is_seat_available(seat_no):
                    return None, f"Seat {seat_no} is already booked"
            seat = theater.search_seat_by_no(seat_no)
            if not seat:
                return None, f"Seat {seat_no} not found in theater"
            new_total_price += seat.type_seat.get_price()
            new_real_seats.append(seat)

        discount = user.get_discount()
        new_total_price = round(new_total_price * (1 - discount), 2)

        if booking_status == BookingStatus.CONFIRMED:
            if new_total_price > old_total_price:
                return None, "Cannot change to more expensive seats"
            showtime.remove_seats(current_seats)
            new_st_seats = showtime.add_seats(new_real_seats, BookingStatus.CONFIRMED)
            booking.showtime_seat = new_st_seats
            booking.total_price = new_total_price
            if booking.ticket:
                booking.ticket.seat_list = new_st_seats
            return booking, "Change booking (Confirmed) successful"

        elif booking_status == BookingStatus.PENDING:
            showtime.remove_seats(current_seats)
            new_st_seats = showtime.add_seats(new_real_seats, BookingStatus.PENDING)
            booking.showtime_seat = new_st_seats
            booking.total_price = new_total_price
            return booking, "Change booking (Pending) successful"

        return None, "Invalid booking status"

    # --- Order processes ---

    def process_order_goods(self, cineplex_id, goods_name, values, user_id,
                             account_id, coupon_id=None):
        member = self.search_user_by_id(user_id)
        if not member:
            return False, "Member not found"
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex:
            return False, "Cineplex not found"
        target_good = cineplex.search_goods_stock(goods_name, values)
        if not target_good:
            return False, "Out of stock or Not enough items"

        discount_amount = 0
        used_coupon_id = None
        if coupon_id:
            for c in self.__coupon_list:
                if c.get_coupon_id() == coupon_id:
                    discount_amount = c.get_discount()
                    used_coupon_id = coupon_id
                    c.update_status("Used")
                    break

        total_price = max((target_good.get_price() * values) - discount_amount, 0)
        order_id = f"ORD-{self.__order_counter:04d}"
        self.__order_counter += 1

        order = Order(order_id, goods_name, values, account_id, total_price, used_coupon_id)
        gateway = PaymentGateway(account_id, total_price)

        if order.pay(self.__bank, gateway):
            target_good.clearstock(values)
            self.__order_list.append(order)
            return True, {"order_id": order_id, "total_paid": total_price}
        else:
            return False, "Payment failed: Insufficient balance or invalid account."

    def process_cancel_order(self, cineplex_id, order_id, user_id):
        member = self.search_user_by_id(user_id)
        if not member:
            return False, "Member not found"
        order = self.search_order_by_id(order_id)
        if not order:
            return False, "Order not found"

        current_status = order.get_status()
        if current_status == OrderStatus.CANCELLED.value:
            return False, "Order is already cancelled"
        if current_status == OrderStatus.REFUNDED.value:
            return False, "Order has already been refunded"

        if current_status == OrderStatus.COMPLETED.value:
            account_id, total_paid = order.get_payment_details()
            if self.__bank.refund(account_id, total_paid):
                goods_name, values = order.get_items()
                cineplex = self.search_cineplex_by_id(cineplex_id)
                if cineplex:
                    target_good = cineplex.search_goods_stock(goods_name)
                    if target_good:
                        target_good.restore_stock(values)
                coupon_id = order.get_used_coupon()
                if coupon_id:
                    for c in self.__coupon_list:
                        if c.get_coupon_id() == coupon_id:
                            c.update_status("Available")
                            break
                order.update_status(OrderStatus.CANCELLED)
                return True, f"Cancel success, Refund {total_paid} THB"
            else:
                return False, "Refund failed"
        return False, "Cannot cancel order with current status"
