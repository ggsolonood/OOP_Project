from datetime import datetime
from enums import SeatType, BookingStatus
from payment import Bank
from theater import Seat, Theater, Movie, Showtime
from user import Booking, User
from cineplex import Cineplex, JamorCineplex

kbank = Bank("KBank")
kbank.create_account("J", "A123", balance=5000)

system = JamorCineplex(kbank)

# Cineplex C – goods only
cineplex_c = Cineplex("CPX_C", "C")
cineplex_c.add_goods("Popcorn", 100, 50, "Popcorn", flavor="Cheese")
system.add_cineplex(cineplex_c)

# Cineplex Siam Paragon
cineplex_siam = Cineplex("CPX01", "Siam Paragon")
theater1 = Theater.create("T01", "Standard")
theater1.add_seat(Seat("S01", "A1", SeatType.NORMALSEAT))
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
theater1.add_showtime(showtime1)
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
