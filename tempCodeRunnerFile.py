from datetime import datetime
from enums import SeatType, MemberTier
from theater import Movie, Theater, Seat, Showtime
from goods import Goods
from cineplex import Cineplex, JamorCineplex

system = JamorCineplex()

# ── Cineplex C – goods only ────────────────────────────────────────────────
cineplex_c = Cineplex("CPX_C", "C")
cineplex_c.add_goods("Popcorn", 100, 50, "Popcorn", flavor="Cheese")
system.add_cineplex(cineplex_c)

# ── Cineplex Siam Paragon ─────────────────────────────────────────────────
cineplex_siam = Cineplex("CPX01", "Siam Paragon")

theater1 = Theater.create("T01", "Standard")
theater1.add_seat(Seat("S01", "A1", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S02", "A2", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S03", "B1", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S04", "B2", SeatType.NORMALSEAT))
cineplex_siam.add_theater(theater1)

movie1 = Movie("M01", "The Matrix", 120, "Sci-Fi", "13+")
showtime1 = Showtime(
    "ST01", movie1, theater1, "Active", "TH",
    start_time=datetime(2026, 3, 10, 10, 0),
    end_time=datetime(2026, 3, 10, 12, 0),
    base_price=200,
)
cineplex_siam.add_showtime(showtime1)
theater1.add_showtime(showtime1)
system.add_cineplex(cineplex_siam)

# ── Users ─────────────────────────────────────────────────────────────────
system.register_member("J",   "01-01-1990", "M001", "2023-01-01")
system.register_member("Ken", "01-01-2000", "U01",  "2023-01-01",
                       email="ken@mail.com", phone_number="081")

# ให้แต้ม M001 ไว้เทสระบบแลกของรางวัล
test_user = system.search_user_by_id("M001")
if test_user:
    test_user.add_point(500)

# Reset tier to GUEST (pending /register via API)
system.search_user_by_id("M001").change_type(MemberTier.GUEST)
system.search_user_by_id("U01").change_type(MemberTier.GUEST)

# ── Coupons ───────────────────────────────────────────────────────────────
system.process_create_coupon("discount", "Discount 10", discount=10)
system.process_create_coupon("discount", "Discount 20 (limited)", discount=20,
                             last_date="2026-12-31 23:59")

# ── Rewards ───────────────────────────────────────────────────────────────
system.process_create_reward("Free Popcorn (M)", 100, 50)
system.process_create_reward("Movie Ticket (Standard)", 300, 10)

system.process_create_booking("U01","CPX01","ST01","A1")
system.process_create_booking("M001","CPX01","ST01","A2")