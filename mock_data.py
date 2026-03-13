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
    bank.create_account("11111", "Pooh", 50000) 
    bank.create_account("22222", "Ken", 50000) 
    bank.create_account("33333", "GuestUser", 50000) 
    
    u1 = User("U01", "Pooh", "1995-01-01", "pooh@mail.com", "081")
    u1.upgrade_tier() 
    u2 = User("U02", "Ken", "1998-05-05", "ken@mail.com")
    u2.upgrade_tier(); u2.upgrade_tier() 
    u2.add_points(1500) 
    u3 = User("U03", "GuestUser", "2000-10-10") 
    
    u1.add_coupon(FixedDiscountCoupon("CP01", "Discount 50", 50.0))
    system.add_user(u1); system.add_user(u2); system.add_user(u3)

    cpx1 = Cineplex("C01", "Siam Paragon")
    cpx2 = Cineplex("C02", "Sukhumvit")
    system.add_cineplex(cpx1); system.add_cineplex(cpx2)

    m1 = Movie("M01", "Spider-Man", 150.0, Genre.ACTION, "13+")
    m2 = Movie("M02", "Batman", 160.0, Genre.ACTION, "15+")
    m3 = Movie("M03", "Jurassic World", 200.0, Genre.SCI_FI, "13+")
    m4 = Movie("M04", "Avengers", 180.0, Genre.ACTION, "13+")
    m5 = Movie("M05", "Avatar", 190.0, Genre.SCI_FI, "7+")
    
    cpx1.add_movie(m1); cpx1.add_movie(m2); cpx1.add_movie(m3); cpx1.add_movie(m5)
    cpx2.add_movie(m1); cpx2.add_movie(m2); cpx2.add_movie(m4); cpx2.add_movie(m5)

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

    now = datetime.now()
    system._Showtime__st1 = Showtime("ST01", m1, t1_siam, now + timedelta(hours=2))
    Showtime("ST02", m3, t2_siam, now + timedelta(hours=5))
    Showtime("ST03", m2, t1_suk,  now + timedelta(hours=2))
    Showtime("ST04", m4, t2_suk,  now + timedelta(hours=5))
    Showtime("ST05", m5, t2_siam, now + timedelta(hours=8))

    cpx1.add_goods(Goods("G01", "Popcorn", 100, 50, GoodsType.POPCORN))
    cpx2.add_goods(Goods("G02", "Cola", 50, 100, GoodsType.DRINKS))
    cpx1.add_reward(Reward("R01", "Free Ticket", 1000))

    system.book_ticket("U01", "ST01", ["S_T01_01"])
    u1_bkg1 = u1.bookings[-1]
    system.confirm_booking(u1_bkg1.id, "11111")
    u1_bkg1.status = BookingStatus.COMPLETED 

    system.book_ticket("U02", "ST02", ["S_T02_03"])

    system.book_ticket("U01", "ST03", ["S_T03_02"])
    u1_bkg2 = u1.bookings[-1]
    system.confirm_booking(u1_bkg2.id, "11111")

    system.order_goods("U02", "Siam Paragon", {"G01": 1}, "22222") 

    system.write_review("U01", u1_bkg1.id, 5, "Amazing Spider-Man!")

setup_mock_data()