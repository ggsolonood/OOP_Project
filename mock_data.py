from datetime import datetime, timedelta
from payment import Bank
from enums import MemberTier, TheaterType, SeatType, GoodsType
from theater import Movie, Theater, Seat, Showtime, Cineplex
from user import User, DiscountCoupon, ExchangeCoupon
from cineplex import JamorCineplex
from goods import Goods, Reward

bank = Bank()
system = JamorCineplex(bank)

def setup_mock_data():
    bank.create_account("ACC01", 10000)
    bank.create_account("ACC02", 10000)
    bank.create_account("ACC03", 10000)

    # 1. สร้าง User
    u1 = User("U01", "Pooh", MemberTier.SILVER)
    u2 = User("U02", "Ken", MemberTier.GOLD)
    u3 = User("U03", "GuestUser", MemberTier.GUEST)
    
    u1.add_coupon(DiscountCoupon("CP01", "Discount 50 THB", 50.0))
    u1.add_coupon(ExchangeCoupon("CP02", "Free Popcorn", ["G01"]))
    
    system.add_user(u1)
    system.add_user(u2)
    system.add_user(u3)

    # 2. สร้าง Cineplex
    cpx1 = Cineplex("C01", "Siam Paragon")
    cpx2 = Cineplex("C02", "Sukhumvit")
    system.add_cineplex(cpx1)
    system.add_cineplex(cpx2)

    # 3. สร้าง Movie (มีราคา Base Price ของหนังด้วย)
    m1 = Movie("M01", "Spider-Man", 150.0)
    m2 = Movie("M02", "Batman", 160.0)
    m3 = Movie("M03", "Dune (Siam Only)", 200.0)
    m4 = Movie("M04", "Inception (Suk Only)", 180.0)
    
    cpx1.add_movie(m1); cpx1.add_movie(m2); cpx1.add_movie(m3)
    cpx2.add_movie(m1); cpx2.add_movie(m2); cpx2.add_movie(m4)

    # 4. สร้าง Theater & Seat (เพิ่ม 4DX)
    def build_theater_for_cpx(t_id, cpx, t_type=TheaterType.STANDARD):
        t = Theater(t_id, t_type)
        for i in range(1, 7):
            s_type = SeatType.SOFA if i > 4 else SeatType.NORMALSEAT
            t.add_seat(Seat(f"S_{t_id}_{i:02d}", f"A{i}", s_type))
        cpx.add_theater(t)
        return t

    t1_siam = build_theater_for_cpx("T01", cpx1, TheaterType.STANDARD)
    t2_siam = build_theater_for_cpx("T02", cpx1, TheaterType.IMAX)
    t1_suk  = build_theater_for_cpx("T03", cpx2, TheaterType.STANDARD)
    t2_suk  = build_theater_for_cpx("T04", cpx2, TheaterType._4DX) # ใช้ 4DX ตามที่ขอ

    # 5. สร้าง Showtime
    now = datetime.now()
    t_early = now + timedelta(hours=2)
    t_late  = now + timedelta(hours=5)
    
    Showtime("ST01", m1, t1_siam, t_early)
    Showtime("ST02", m3, t2_siam, t_late)
    Showtime("ST03", m2, t1_suk,  t_early)
    Showtime("ST04", m4, t2_suk,  t_late)

    # 6. สร้าง สินค้าและรางวัล
    cpx1.add_goods(Goods("G01", "Popcorn", 100, 50, GoodsType.POPCORN))
    cpx2.add_goods(Goods("G02", "Cola", 50, 100, GoodsType.DRINKS))
    cpx1.add_reward(Reward("R01", "Free Ticket", 1000))

setup_mock_data()