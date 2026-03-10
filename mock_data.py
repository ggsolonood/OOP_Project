from datetime import datetime
from enums import SeatType, BookingStatus
from theater import Seat, Theater, Movie, Showtime
from user import Booking, User
from cineplex import Cineplex, JamorCineplex

# ไม่มี Bank — JamorCineplex ไม่ต้องการ bank อีกต่อไป
system = JamorCineplex()

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

# Users — สร้างด้วย register_member (ยังไม่มี password = GUEST จนกว่าจะ /register)
system.register_member("J",   "01-01-1990", "M001", "2023-01-01")
system.register_member("Ken", "01-01-2000", "U01",  "2023-01-01",
                       email="ken@mail.com", phone_number="081")

# Reset tier เป็น GUEST เพื่อรอ register ผ่าน API
from enums import MemberTier
system.search_user_by_id("M001").change_type(MemberTier.GUEST)
system.search_user_by_id("U01").change_type(MemberTier.GUEST)
