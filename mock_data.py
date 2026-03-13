from datetime import datetime, timedelta
from payment import Bank
from enums import MemberTier, TheaterType, SeatType, GoodsType, Genre, BookingStatus, TicketStatus
from theater import Movie, Theater, Seat, Showtime, Cineplex
from user import User, FixedDiscountCoupon
from cineplex import JamorCineplex
from goods import Goods, Reward

bank = Bank()
system = JamorCineplex(bank)

def setup_mock_data():
    # --- Bank Setup ---
    bank.create_account("11111", "Pooh", 50000) 
    bank.create_account("22222", "Ken", 50000) 
    bank.create_account("33333", "GuestUser", 50000) 
    
    # --- User Setup ---
    u1 = User("U01", "Pooh", "1995-01-01", "pooh@mail.com", "081")
    u1.upgrade_tier() 
    u2 = User("U02", "Ken", "1998-05-05", "ken@mail.com")
    u2.upgrade_tier(); u2.upgrade_tier() 
    u2.add_points(1500) 
    u3 = User("U03", "GuestUser", "2000-10-10") 
    
    u1.add_coupon(FixedDiscountCoupon("CP01", "Discount 50", 50.0))
    system.add_user(u1); system.add_user(u2); system.add_user(u3)

    # --- Cineplex & Movie Setup ---
    cpx1 = Cineplex("C01", "Robinson")
    cpx2 = Cineplex("C02", "Mega")
    system.add_cineplex(cpx1); system.add_cineplex(cpx2)

    m1 = Movie("M01", "Spider-Man", 150.0, Genre.ACTION, "13+")
    m2 = Movie("M02", "Batman", 160.0, Genre.ACTION, "15+")
    m3 = Movie("M03", "Jurassic World", 200.0, Genre.SCI_FI, "13+")
    m4 = Movie("M04", "Avengers", 180.0, Genre.ACTION, "13+")
    m5 = Movie("M05", "Avatar", 190.0, Genre.SCI_FI, "7+")
    
    cpx1.add_movie(m1); cpx1.add_movie(m2); cpx1.add_movie(m3); cpx1.add_movie(m5)
    cpx2.add_movie(m1); cpx2.add_movie(m2); cpx2.add_movie(m4); cpx2.add_movie(m5)

    # --- Theater & Seat Setup ---
    t1_robin = Theater("T01", TheaterType.STANDARD, "Theater 1")
    seats_t1_robin = [
        Seat("S_T01_01", "A1", SeatType.NORMALSEAT), Seat("S_T01_02", "A2", SeatType.NORMALSEAT),
        Seat("S_T01_03", "A3", SeatType.NORMALSEAT), Seat("S_T01_04", "A4", SeatType.NORMALSEAT),
        Seat("S_T01_05", "A5", SeatType.SOFA),       Seat("S_T01_06", "A6", SeatType.SOFA)
    ]
    for s in seats_t1_robin: t1_robin.add_seat(s)
    cpx1.add_theater(t1_robin)

    t2_robin = Theater("T02", TheaterType.IMAX, "Theater 2")
    seats_t2_robin = [
        Seat("S_T02_01", "A1", SeatType.NORMALSEAT), Seat("S_T02_02", "A2", SeatType.NORMALSEAT),
        Seat("S_T02_03", "A3", SeatType.NORMALSEAT), Seat("S_T02_04", "A4", SeatType.NORMALSEAT),
        Seat("S_T02_05", "A5", SeatType.SOFA),       Seat("S_T02_06", "A6", SeatType.SOFA)
    ]
    for s in seats_t2_robin: t2_robin.add_seat(s)
    cpx1.add_theater(t2_robin)

    t1_mega = Theater("T03", TheaterType.STANDARD, "Theater A")
    seats_t1_mega = [
        Seat("S_T03_01", "A1", SeatType.NORMALSEAT), Seat("S_T03_02", "A2", SeatType.NORMALSEAT),
        Seat("S_T03_03", "A3", SeatType.NORMALSEAT), Seat("S_T03_04", "A4", SeatType.NORMALSEAT),
        Seat("S_T03_05", "A5", SeatType.SOFA),       Seat("S_T03_06", "A6", SeatType.SOFA)
    ]
    for s in seats_t1_mega: t1_mega.add_seat(s)
    cpx2.add_theater(t1_mega)

    t2_mega = Theater("T04", TheaterType._4DX, "Theater B")
    seats_t2_mega = [
        Seat("S_T04_01", "A1", SeatType.NORMALSEAT), Seat("S_T04_02", "A2", SeatType.NORMALSEAT),
        Seat("S_T04_03", "A3", SeatType.NORMALSEAT), Seat("S_T04_04", "A4", SeatType.NORMALSEAT),
        Seat("S_T04_05", "A5", SeatType.SOFA),       Seat("S_T04_06", "A6", SeatType.SOFA)
    ]
    for s in seats_t2_mega: t2_mega.add_seat(s)
    cpx2.add_theater(t2_mega)

    # --- Showtime Setup ---
    now = datetime.now()
    Showtime("ST01", m1, t1_robin, now + timedelta(hours=2))
    Showtime("ST02", m3, t2_robin, now + timedelta(hours=5))
    Showtime("ST03", m2, t1_mega,  now + timedelta(hours=2))
    Showtime("ST04", m4, t2_mega,  now + timedelta(hours=5))
    Showtime("ST05", m5, t2_robin, now + timedelta(hours=8))

    # --- Goods & Rewards Setup ---
    cpx1.add_goods(Goods("G01", "Popcorn", 100, 50, GoodsType.POPCORN))
    cpx2.add_goods(Goods("G02", "Cola", 50, 100, GoodsType.DRINKS))
    cpx1.add_reward(Reward("R01", "Free Ticket", 1000))

    # --- Mock Activity Data ---
    system.book_ticket("U01", "ST01", ["S_T01_01"])
    u1_bkg1 = u1.bookings[-1]
    system.confirm_booking(u1_bkg1.id, "11111")
    u1_bkg1.status = BookingStatus.COMPLETED 
    for t in u1.tickets:
        if t.booking_id == u1_bkg1.id: t.status = TicketStatus.USED

    system.book_ticket("U02", "ST02", ["S_T02_03"])

    system.book_ticket("U01", "ST03", ["S_T03_02"])
    u1_bkg2 = u1.bookings[-1]
    system.confirm_booking(u1_bkg2.id, "11111")

    system.order_goods("U02", "Robinson", {"G01": 1}, "22222") 

    system.write_review("U01", u1_bkg1.id, 5, "Amazing Spider-Man!")

setup_mock_data()