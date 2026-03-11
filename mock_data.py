from datetime import datetime
from enums import SeatType, MemberTier, ShowtimeStatus
from theater import Movie, Theater, Seat, Showtime
from cineplex import Cineplex, JamorCineplex
from payment import Bank

bank = Bank("KrungThai")
bank.create_account("Popo","13579",1000)
system = JamorCineplex(bank)

# ── Cineplex C – goods only ────────────────────────────────────────────────
cineplex_c = Cineplex("CPX_C", "C")
cineplex_c.add_goods("Popcorn", 100, 50, "Popcorn", flavor="Cheese")
system.add_cineplex(cineplex_c)

# ── Cineplex Siam Paragon ─────────────────────────────────────────────────
cineplex_siam = Cineplex("CPX01", "Siam Paragon")

# Theater 1 — Standard
theater1 = Theater.create("T01", "Standard")
theater1.add_seat(Seat("S01", "A1", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S02", "A2", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S03", "B1", SeatType.SOFA))
theater1.add_seat(Seat("S04", "B2", SeatType.SOFA))
theater1.add_seat(Seat("S05", "C1", SeatType.HONEYMOONBED))
theater1.add_seat(Seat("S06", "C2", SeatType.HONEYMOONBED))
cineplex_siam.add_theater(theater1)

# Theater 2 — IMAX
theater2 = Theater.create("T02", "IMAX")
theater2.add_seat(Seat("S07", "A1", SeatType.NORMALSEAT))
theater2.add_seat(Seat("S08", "A2", SeatType.NORMALSEAT))
theater2.add_seat(Seat("S09", "B1", SeatType.NORMALSEAT))
theater2.add_seat(Seat("S10", "B2", SeatType.NORMALSEAT))
cineplex_siam.add_theater(theater2)

# Movies
movie1 = Movie("M01", "The Matrix", 120, "Sci-Fi", "13+")
movie2 = Movie("M02", "Avengers: Endgame", 181, "Action", "13+")
movie3 = Movie("M03", "Avatar: The way of water",192, "Action", "13+")
movie4 = Movie("M04","Jurassic World", 124, "Action", "13+")

cineplex_siam.add_movie(movie1)
cineplex_siam.add_movie(movie2)
cineplex_siam.add_movie(movie3)
cineplex_siam.add_movie(movie4)

# Showtimes
showtime1 = Showtime(
    "ST01", movie1, theater1, ShowtimeStatus.ACTIVE, "TH",
    start_time=datetime(2026, 3, 11, 10, 0),
    base_price=200,
)
showtime2 = Showtime(
    "ST02", movie1, theater1, ShowtimeStatus.ACTIVE, "EN",
    start_time=datetime(2026, 3, 11, 14, 0),
    base_price=200,
)
showtime3 = Showtime(
    "ST03", movie2, theater2, ShowtimeStatus.ACTIVE, "TH",
    start_time=datetime(2026, 3, 11, 13, 0),
    base_price=350,
)
cineplex_siam.add_showtime(showtime1)
cineplex_siam.add_showtime(showtime2)
cineplex_siam.add_showtime(showtime3)
theater1.add_showtime(showtime1)
theater1.add_showtime(showtime2)
theater2.add_showtime(showtime3)

# Goods
cineplex_siam.add_goods("Popcorn Butter", 200, 60, "Popcorn", flavor="Butter")
cineplex_siam.add_goods("Popcorn Caramel", 150, 60, "Popcorn", flavor="Caramel")
cineplex_siam.add_goods("Coke", 300, 50, "Drinks", flavor="Original")
cineplex_siam.add_goods("Nachos", 100, 80, "Snack")

system.add_cineplex(cineplex_siam)
# ── Cineplex EmQuartier ───────────────────────────────────────────────────
cineplex_emq = Cineplex("CPX02", "EmQuartier")

# Theater 3 — 4DX (สาขานี้เน้นเทคโนโลยี 4DX)
theater3 = Theater.create("T03", "4DX")
theater3.add_seat(Seat("S11", "A1", SeatType.NORMALSEAT))
theater3.add_seat(Seat("S12", "A2", SeatType.NORMALSEAT))
theater3.add_seat(Seat("S13", "B1", SeatType.SOFA))
theater3.add_seat(Seat("S14", "B2", SeatType.SOFA))
cineplex_emq.add_theater(theater3)

# เพิ่มหนังที่ต้องการฉายในสาขานี้
cineplex_emq.add_movie(movie3) # Avatar: The way of water
cineplex_emq.add_movie(movie4) # Jurassic World

# --- รอบฉายที่ Completed ไปแล้ว (ฉายเมื่อวานนี้) ---
showtime_past = Showtime(
    "ST04", movie3, theater3, ShowtimeStatus.COMPLETED, "EN",
    start_time=datetime(2026, 3, 10, 19, 0), # 10 มีนาคม 2026
    base_price=400,
)

# --- รอบฉายที่กำลัง Active (ฉายวันนี้ช่วงเย็น) ---
showtime_active = Showtime(
    "ST05", movie4, theater3, ShowtimeStatus.ACTIVE, "TH",
    start_time=datetime(2026, 3, 11, 18, 0), # 11 มีนาคม 2026 (วันนี้)
    base_price=300,
)

# บันทึกรอบฉายลงในรายการของสาขาและโรง
cineplex_emq.add_showtime(showtime_past)
cineplex_emq.add_showtime(showtime_active)
theater3.add_showtime(showtime_past)
theater3.add_showtime(showtime_active)

# เพิ่มสาขา EmQuartier ลงในระบบหลัก
system.add_cineplex(cineplex_emq)

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

system.process_create_booking("U01","CPX01","ST01",["A1"])
system.process_create_booking("M001","CPX01","ST01",["A2"])