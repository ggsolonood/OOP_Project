from datetime import datetime

from enums import BookingStatus, SeatType, TheaterType
from payment import Bank
from theater import Seat, Theater, Movie, Showtime
from user import User, Booking
from cineplex import Cineplex, JamorCineplex

# ==========================================
# Setup Mock Data
# ==========================================

kbank = Bank("KBank")
kbank.create_account("J", "A123", balance=5000)

system = JamorCineplex(kbank)

# --- Cineplex C (มีแค่ popcorn) ---
cineplex_c = Cineplex("CPX_C", "C")
cineplex_c.add_popcorn("Popcorn", 100, 50, "Cheese")
system.add_cineplex(cineplex_c)

# --- Cineplex Siam Paragon ---
cineplex_siam = Cineplex("CPX01", "Siam Paragon")

theater1 = Theater("T01", TheaterType.STANDARD)
theater1.add_seat(Seat("S01", "A1", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S02", "A2", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S03", "B1", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S04", "B2", SeatType.NORMALSEAT))
cineplex_siam.add_theater(theater1)

movie1 = Movie("M01", "The Matrix", 120, "Sci-Fi", "13+")
showtime1 = Showtime("ST01", movie1, theater1, "Active", "TH", "10:00", "12:00", 200)
cineplex_siam.add_showtime(showtime1)

system.add_cineplex(cineplex_siam)

# --- Users ---
system.register_member("J", "01-01-1990", "M001", "2023-01-01")

user1 = User("U01", "Ken", "ken@mail.com", "081", "2000-01-01", "1234")
system.add_user(user1)

# --- Coupon ---
system.process_create_coupon("discount", "C10", "Discount 10", 10)

# --- Pre-existing Booking ---
initial_seats = [theater1.search_seat_by_no("A1"), theater1.search_seat_by_no("A2")]
booking1 = Booking("BK01", user1, showtime1, datetime.now(), BookingStatus.PENDING, 400.0)
booking1.showtime_seat = showtime1.add_seats(initial_seats, BookingStatus.PENDING)
user1.add_booking(booking1)
