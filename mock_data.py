from datetime import datetime, timedelta
from payment import Bank
from enums import MemberTier, TheaterType, SeatType, GoodsType, Genre, BookingStatus
from theater import Movie, Theater, Seat, Showtime, Cineplex
from user import User, FixedDiscountCoupon
from cineplex import JamorCineplex
from goods import Goods, Reward

bank = Bank()
system = JamorCineplex(bank)

def setup_mock_data():
    # --- Bank Setup ---
    bank.create_account("ACC01", 50000) # ของ Pooh (สำหรับเทสซื้อของรัวๆ)
    bank.create_account("ACC02", 50000) # ของ Ken
    bank.create_account("ACC03", 50000) # ของ Guest
    
    # --- User Setup ---
    u1 = User("U01", "Pooh", "1995-01-01", "pooh@mail.com", "081")
    u1.upgrade_tier() # เป็น Silver
    u2 = User("U02", "Ken", "1998-05-05", "ken@mail.com")
    u2.upgrade_tier(); u2.upgrade_tier() # เป็น Gold
    u2.add_points(1500) # ให้พ้อยท์ Ken สำหรับทดสอบแลกของ (UC13)
    u3 = User("U03", "GuestUser", "2000-10-10") # เป็น Guest
    
    u1.add_coupon(FixedDiscountCoupon("CP01", "Discount 50", 50.0))
    system.add_user(u1); system.add_user(u2); system.add_user(u3)

    # --- Cineplex & Movie Setup ---
    cpx1 = Cineplex("C01", "Siam Paragon")
    cpx2 = Cineplex("C02", "Sukhumvit")
    system.add_cineplex(cpx1); system.add_cineplex(cpx2)

    # เพิ่มหนัง Avatar และแก้รายชื่อหนังใหม่ ใช้ String Age Rating
    m1 = Movie("M01", "Spider-Man", 150.0, Genre.ACTION, "13+")
    m2 = Movie("M02", "Batman", 160.0, Genre.ACTION, "15+")
    m3 = Movie("M03", "Jurassic World", 200.0, Genre.SCI_FI, "13+") # แทน Dune
    m4 = Movie("M04", "Avengers", 180.0, Genre.ACTION, "13+")       # แทน Inception
    m5 = Movie("M05", "Avatar", 190.0, Genre.SCI_FI, "G")           # หนังใหม่
    
    # แจกจ่ายหนังลงสาขา
    cpx1.add_movie(m1); cpx1.add_movie(m2); cpx1.add_movie(m3); cpx1.add_movie(m5)
    cpx2.add_movie(m1); cpx2.add_movie(m2); cpx2.add_movie(m4); cpx2.add_movie(m5)

    # --- Theater & Seat Setup ---
    def build_theater_for_cpx(t_id, cpx, name, t_type=TheaterType.STANDARD):
        t = Theater(t_id, t_type, name)
        for i in range(1, 7):
            s_type = SeatType.SOFA if i > 4 else SeatType.NORMALSEAT
            t.add_seat(Seat(f"S_{t_id}_{i:02d}", f"A{i}", s_type))
        cpx.add_theater(t)
        return t

    t1_siam = build_theater_for_cpx("T01", cpx1, "Theater 1", TheaterType.STANDARD)
    t2_siam = build_theater_for_cpx("T02", cpx1, "Theater 2", TheaterType.IMAX)
    t1_suk  = build_theater_for_cpx("T03", cpx2, "Theater A", TheaterType.STANDARD)
    t2_suk  = build_theater_for_cpx("T04", cpx2, "Theater B", TheaterType._4DX)

    # --- Showtime Setup ---
    now = datetime.now()
    system._Showtime__st1 = Showtime("ST01", m1, t1_siam, now + timedelta(hours=2))
    Showtime("ST02", m3, t2_siam, now + timedelta(hours=5))
    Showtime("ST03", m2, t1_suk,  now + timedelta(hours=2))
    Showtime("ST04", m4, t2_suk,  now + timedelta(hours=5))
    Showtime("ST05", m5, t2_siam, now + timedelta(hours=8)) # รอบฉาย Avatar

    # --- Goods & Rewards Setup ---
    cpx1.add_goods(Goods("G01", "Popcorn", 100, 50, GoodsType.POPCORN))
    cpx2.add_goods(Goods("G02", "Cola", 50, 100, GoodsType.DRINKS))
    cpx1.add_reward(Reward("R01", "Free Ticket", 1000))

    # ==========================================
    # --- MOCK DATA FOR 17 USE CASES TESTING ---
    # ==========================================
    
    # 1. ให้ Pooh จองตั๋วแบบจ่ายเงินแล้วดูจบแล้ว (สถานะ COMPLETED) -> เพื่อใช้ทดสอบ "เขียนรีวิว (UC16)"
    system.book_ticket("U01", "ST01", ["S_T01_01"])
    u1_bkg1 = u1.bookings[-1]
    system.confirm_booking(u1_bkg1.id, "ACC01")
    u1_bkg1.status = BookingStatus.COMPLETED 

    # 2. ให้ Ken จองตั๋วไว้เฉยๆ (สถานะ PENDING) -> เพื่อใช้ทดสอบ "จ่ายเงินยืนยัน (UC5)" หรือ "ยกเลิกการจอง (UC6)"
    system.book_ticket("U02", "ST02", ["S_T02_03"])

    # 3. ให้ Pooh จองตั๋วและจ่ายเงินแล้ว (สถานะ CONFIRMED) -> เพื่อใช้ทดสอบ "เปลี่ยนที่นั่ง (UC15)"
    system.book_ticket("U01", "ST03", ["S_T03_02"])
    u1_bkg2 = u1.bookings[-1]
    system.confirm_booking(u1_bkg2.id, "ACC01")

    # 4. ให้ Ken สั่งซื้อของกินไว้ -> เพื่อใช้ทดสอบ "ยกเลิกสั่งซื้อ (UC9)"
    system.order_goods("U02", "C01", {"G01": 1}, "ACC02")

    # 5. เขียนรีวิวทิ้งไว้ให้ Spider-Man -> เพื่อทดสอบ "อ่านรีวิว (UC17)"
    system.write_review("U01", u1_bkg1.id, 5, "Amazing Spider-Man!")

setup_mock_data()