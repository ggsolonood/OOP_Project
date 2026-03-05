from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from abc import ABC, abstractmethod
from enum import Enum
import uvicorn
from datetime import datetime

# --- ENUMS (ปรับชื่อไม่ให้ซ้ำกับ Class) ---
class OrderStatus(Enum):
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"

class MemberTier(Enum):
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"
    GUEST = "Guest"

class BookingStatus(Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class GoodsType(Enum):
    POPCORN = "Popcorn"
    DRINKS = "Drinks"
    SNACK = "Snack"

class SeatType(Enum):
    NORMALSEAT = "Normalseat"
    SOFA = "Sofa"
    HONEYMOONBED = "Honeymoonbed"

class TheaterType(Enum):
    STANDARD = "Standard"
    IMAX = "IMAX"
    _4DX = "4DX"

# --- CLASSES ---
class JamorCineplex:
    def __init__(self):
        self.__cineplex_list = []
        self.__user_list = []
        self.__booking_list = []
        self.__coupon_list = []

    def add_cineplex(self, cineplex):
        self.__cineplex_list.append(cineplex)

    def add_user(self, user):
        self.__user_list.append(user)

    def search_cineplex_by_id(self, cineplex_id):
        for i in self.__cineplex_list:
            if i.id == cineplex_id:
                return i
        return None

    def search_user_by_id(self, user_id):
        for i in self.__user_list:
            if i.id == user_id:
                return i
        return None

    # --- Logic: Change Booking ตาม Sequence Diagram ---
    def process_change_booking(self, user_id: str, booking_id: str, new_seat_nos: list):
        # 1. ค้นหา User
        user = self.search_user_by_id(user_id)
        if not user: return None, "User not found"

        # 2. ค้นหา Booking
        booking = user.search_booking_by_id(booking_id)
        if not booking: return None, "Booking not found"

        # 3. ตรวจสอบเบื้องต้น
        current_seats = [s.seat_number for s in booking.showtime_seat]
        if len(new_seat_nos) != len(current_seats):
            return None, f"Validation Error: Must select exactly {len(current_seats)} seats"

        if len(new_seat_nos) != len(set(new_seat_nos)):
            return None, "Validation Error: Duplicate seats requested"

        # 4. ดึงข้อมูลประกอบ
        showtime = booking.showtime
        theater = showtime.theater
        booking_status = booking.status
        old_total_price = booking.total_price

        # 5. วนลูปตรวจสอบและคำนวณราคา
        new_real_seats = []
        new_total_price = 0.0

        for seat_no in new_seat_nos:
            if seat_no not in current_seats:
                if not showtime.is_seat_available(seat_no):
                    return None, f"Seat {seat_no} is already booked"

            seat = theater.search_seat_by_no(seat_no)
            if not seat:
                return None, f"Seat {seat_no} not found in theater"
            
            # จำลองการคำนวณราคาเบื้องต้น (สามารถแก้สูตรได้ตามจริง)
            seat_price = 200 if seat.type_seat == SeatType.NORMALSEAT else 300
            new_total_price += seat_price
            new_real_seats.append(seat)

        # 6. คำนวณราคารวม (หักส่วนลด User)
        discount = user.get_discount()
        new_total_price = new_total_price * (1 - discount)

        # 7. อัปเดตข้อมูลตามสถานะ Booking
        if booking_status == BookingStatus.CONFIRMED: # เทียบเท่า Paid
            if new_total_price > old_total_price:
                return None, "Cannot change to more expensive seats"

            # ถอนที่นั่งเก่า ใส่ที่นั่งใหม่
            showtime.remove_seats(current_seats)
            new_st_seats = showtime.add_seats(new_real_seats, BookingStatus.CONFIRMED)

            # อัปเดต Booking
            booking.showtime_seat = new_st_seats
            booking.total_price = new_total_price

            # อัปเดต Ticket
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


class Cineplex:
    def __init__(self, cineplex_id, name):
        self.__cineplex_id = cineplex_id
        self.__name = name
        self.__movies_list = []
        self.__theaters_list = []
        self.__showtime_list = []
        self.__goods_list = []

    @property
    def id(self): return self.__cineplex_id

    def add_movie(self, movie): self.__movies_list.append(movie)
    def add_theater(self, theater): self.__theaters_list.append(theater)
    def add_showtime(self, showtime): self.__showtime_list.append(showtime)

class Movie:
    def __init__(self, id, name, duration, genre, age_rating):
        self.__movie_id = id
        self.__movie_name = name
        self.__duration = duration
        self.__genre = genre
        self.__age_rating = age_rating

    @property
    def id(self): return self.__movie_id
    @property
    def name(self): return self.__movie_name

class Theater:
    def __init__(self, theater_id, type_theater: TheaterType):
        self.__theater_id = theater_id
        self.__seats_list = []
        self.__type_theater = type_theater

    @property
    def id(self): return self.__theater_id

    def add_seat(self, seat):
        self.__seats_list.append(seat)

    def search_seat_by_no(self, seat_no):
        for s in self.__seats_list:
            if s.seat_number == seat_no:
                return s
        return None

class Seat:
    def __init__(self, seat_id, seat_number, type_seat: SeatType):
        self.__seat_id = seat_id
        self.__seat_number = seat_number
        self.__type_seat = type_seat

    @property
    def id(self): return self.__seat_id
    @property
    def seat_number(self): return self.__seat_number
    @property
    def type_seat(self): return self.__type_seat

class ShowtimeSeat(Seat):
    def __init__(self, seat: Seat, status: BookingStatus):
        super().__init__(seat.id, seat.seat_number, seat.type_seat)
        self.__status = status

    @property
    def status(self): return self.__status

class Showtime:
    def __init__(self, showtime_id, movie, theater, start_time, end_time, base_price):
        self.__id = showtime_id
        self.__movie = movie
        self.__theater = theater
        self.__start_time = start_time
        self.__end_time = end_time
        self.__base_price = base_price
        self.__showtime_seat = [] # เก็บ ShowtimeSeat
    @property
    def movie(self): return self.__movie
    @property
    def id(self): return self.__id
    @property
    def theater(self): return self.__theater

    def is_seat_available(self, seat_no):
        for s in self.__showtime_seat:
            if s.seat_number == seat_no:
                return False
        return True

    def remove_seats(self, seat_nos: list):
        self.__showtime_seat = [s for s in self.__showtime_seat if s.seat_number not in seat_nos]

    def add_seats(self, seats: list, status: BookingStatus):
        new_seats = []
        for s in seats:
            st_seat = ShowtimeSeat(s, status)
            self.__showtime_seat.append(st_seat)
            new_seats.append(st_seat)
        return new_seats

class Booking:
    def __init__(self, booking_id, user, showtime, timestamp, status: BookingStatus, total_price=0.0):
        self.__booking_id = booking_id
        self.__user = user
        self.__showtime = showtime
        self.__ticket = None
        self.__timestamp = timestamp
        self.__showtime_seat = []
        self.__status = status
        self.__total_price = total_price

    @property
    def id(self): return self.__booking_id
    @property
    def showtime(self): return self.__showtime
    @property
    def status(self): return self.__status
    @property
    def showtime_seat(self): return self.__showtime_seat
    @property
    def total_price(self): return self.__total_price
    @property
    def ticket(self): return self.__ticket

    @showtime_seat.setter
    def showtime_seat(self, seats): self.__showtime_seat = seats
    @total_price.setter
    def total_price(self, price): self.__total_price = price
    @status.setter
    def status(self, stat): self.__status = stat
    @ticket.setter
    def ticket(self, tk): self.__ticket = tk

class Ticket:
    def __init__(self, booking, cineplex, user, movie, theater, showtime, seat_list):
        self.__booking = booking
        self.__cineplex = cineplex
        self.__user = user
        self.__movie = movie
        self.__theater = theater
        self.__showtime = showtime
        self.seat_list = seat_list # Public เพื่อให้อัปเดตง่าย

class User:
    def __init__(self, id, name, email, phone_number, birthday, password):
        self.__id = id
        self.__name = name
        self.__email = email
        self.__phone_number = phone_number
        self.__birthday = birthday
        self.__password = password
        self.__point = 0
        self.__coupon_list = []
        self.__ticket_list = []
        self.__booking_list = []
        self.__totle_spending = 0
        self.__type_user = MemberTier.SILVER # จำลอง Tier

    @property
    def id(self): return self.__id
    @property
    def name(self): return self.__name
    @property
    def booking_list(self): return self.__booking_list

    def get_discount(self):
        if self.__type_user == MemberTier.GOLD: return 0.10
        elif self.__type_user == MemberTier.PLATINUM: return 0.15
        return 0.0

    def add_booking(self, booking):
        self.__booking_list.append(booking)

    def search_booking_by_id(self, booking_id):
        for b in self.__booking_list:
            if b.id == booking_id:
                return b
        return None


# --------------------------------------------
# System Initialization & Mock Data
# --------------------------------------------
system = JamorCineplex()

user1 = User("U01", "Ken", "ken@mail.com", "081", "2000-01-01", "1234")
system.add_user(user1)

cineplex = Cineplex("CPX01", "Siam Paragon")
system.add_cineplex(cineplex)

theater1 = Theater("T01", TheaterType.STANDARD)
theater1.add_seat(Seat("S01", "A1", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S02", "A2", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S03", "B1", SeatType.NORMALSEAT))
theater1.add_seat(Seat("S04", "B2", SeatType.NORMALSEAT))
cineplex.add_theater(theater1)

movie1 = Movie("M01", "The Matrix", 120, "Sci-Fi", "13+")
showtime1 = Showtime("ST01", movie1, theater1, "10:00", "12:00", 200)

# จำลองการสร้าง Booking แรกเริ่ม (Pending)
initial_seats = [theater1.search_seat_by_no("A1"), theater1.search_seat_by_no("A2")]
booking1 = Booking("BK01", user1, showtime1, datetime.now(), BookingStatus.PENDING, 400.0)
booking1.showtime_seat = showtime1.add_seats(initial_seats, BookingStatus.PENDING)
user1.add_booking(booking1)


# --------------------------------------------
# FastAPI Setup
# --------------------------------------------
app = FastAPI()

class ChangeBookingRequest(BaseModel):
    new_seat_nos: List[str]

@app.patch("/users/{user_id}/bookings/{booking_id}/change-seats")
async def api_change_booking(user_id: str, booking_id: str, req: ChangeBookingRequest):
    booking, msg = system.process_change_booking(user_id, booking_id, req.new_seat_nos)
    
    if not booking:
        raise HTTPException(status_code=400, detail=msg)
        
    return {
        "status": "success",
        "message": msg,
        "booking_id": booking.id,
        "booking_status": booking.status.value,
        "new_seats": [s.seat_number for s in booking.showtime_seat],
        "new_total_price": booking.total_price
    }

@app.get("/users/{user_id}/bookings")
async def get_user_bookings(user_id: str):
    user = system.search_user_by_id(user_id)
    if not user: raise HTTPException(status_code=404, detail="User not found")
    
    return [{
        "booking_id": b.id,
        "movie": b.showtime.movie.name,
        "status": b.status.value,
        "seats": [s.seat_number for s in b.showtime_seat],
        "price": b.total_price
    } for b in user.booking_list]

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)