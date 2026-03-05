from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from abc import ABC, abstractmethod
from enum import Enum
import uvicorn

app = FastAPI()

# ==========================================
# 1. Pydantic Models (สำหรับ API รับข้อมูล)
# ==========================================
class CineplexCreate(BaseModel):
    cineplex_id: int
    name: str

class MovieCreate(BaseModel):
    cineplex_id: int
    movie_id: int
    name: str
    duration: int
    genre: str
    age_rating: str

class TheaterCreate(BaseModel):
    cineplex_id: int
    theater_id: str
    type_theater: str

class SeatCreate(BaseModel):
    cineplex_id: int
    theater_id: str
    seat_id: str
    seat_number: str
    type_seat: str

class ShowtimeCreate(BaseModel):
    cineplex_id: int
    showtime_id: str
    movie_id: int
    theater_id: str
    status: str
    subtitle: str
    start_time: str
    end_time: str
    base_price: float

class CouponCreate(BaseModel):
    coupon_type: str  # "discount" หรือ "exchange"
    coupon_id: str
    name: str
    discount: Optional[float] = 0.0
    goods_list: Optional[List[str]] = []

# ==========================================
# 2. Classes Structure
# ==========================================
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

    def search_movie_by_id(self, movie_id):
        for i in self.__movies_list:
            if i.id == movie_id: return i
        return False

    def search_theater_by_id(self, theater_id):
        for i in self.__theaters_list:
            if i.id == theater_id: return i
        return False

    def search_showtime_by_id(self, showtime_id):
        for i in self.__showtime_list:
            if i.id == showtime_id: return i
        return False

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

class Theater:
    def __init__(self, theater_id, type_theater):
        self.__theater_id = theater_id
        self.__seats_list = []
        self.__type_theater = type_theater

    @property
    def id(self): return self.__theater_id
    
    def add_seat(self, seat): self.__seats_list.append(seat)

class Seat:
    def __init__(self, seat_id, seat_number, type_seat):
        self.__seat_id = seat_id
        self.__seat_number = seat_number
        self.__type_seat = type_seat

    @property
    def id(self): return self.__seat_id

class Showtime:
    def __init__(self, showtime, movie, theater, status, subtitle, start_time, end_time, base_price):
        self.__id = showtime
        self.__movie = movie
        self.__theater = theater
        self.__status = status
        self.__subtitle = subtitle
        self.__start_time = start_time
        self.__end_time = end_time
        self.__base_price = base_price
        self.__showtime_seat = []

    @property
    def id(self): return self.__id

class coupon:
    def __init__(self, id, name):
        self.__coupon_id = id
        self.__name = name

class DiscountCoupon(coupon):
    def __init__(self, id, name, discount):
        super().__init__(id, name)
        self.__discount = discount

class ExchangeCoupon(coupon):
    def __init__(self, id, name, goods):
        super().__init__(id, name)
        self.__list_goods = goods

# ==========================================
# 3. System (Controller)
# ==========================================
class JamorCineplex:
    def __init__(self):
        self.__cineplex_list = []
        self.__user_list = []
        self.__booking_list = []
        self.__coupon_list = []

    def search_cineplex_by_id(self, cineplex_id):
        for i in self.__cineplex_list:
            if i.id == cineplex_id: return i
        return False

    def search_user_by_id(self, user_id):
        for i in self.__user_list:
            if i.id == user_id: return i
        return False

    # --- Process Methods (Business Logic) ---
    def process_create_cineplex(self, cineplex_id, name):
        if self.search_cineplex_by_id(cineplex_id):
            return False, "Cineplex ID already exists."
        new_cineplex = Cineplex(cineplex_id, name)
        self.__cineplex_list.append(new_cineplex)
        return True, "Cineplex created successfully."

    def process_create_movie(self, cineplex_id, movie_id, name, duration, genre, age_rating):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex: return False, "Cineplex not found."
        if cineplex.search_movie_by_id(movie_id): return False, "Movie ID already exists in this Cineplex."
        
        new_movie = Movie(movie_id, name, duration, genre, age_rating)
        cineplex.add_movie(new_movie)
        return True, "Movie created successfully."

    def process_create_theater(self, cineplex_id, theater_id, type_theater):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex: return False, "Cineplex not found."
        if cineplex.search_theater_by_id(theater_id): return False, "Theater ID already exists."
        
        new_theater = Theater(theater_id, type_theater)
        cineplex.add_theater(new_theater)
        return True, "Theater created successfully."

    def process_create_seat(self, cineplex_id, theater_id, seat_id, seat_number, type_seat):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex: return False, "Cineplex not found."
        theater = cineplex.search_theater_by_id(theater_id)
        if not theater: return False, "Theater not found."
        
        new_seat = Seat(seat_id, seat_number, type_seat)
        theater.add_seat(new_seat)
        return True, "Seat created successfully."

    def process_create_showtime(self, cineplex_id, showtime_id, movie_id, theater_id, status, subtitle, start_time, end_time, base_price):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex: return False, "Cineplex not found."
        movie = cineplex.search_movie_by_id(movie_id)
        if not movie: return False, "Movie not found."
        theater = cineplex.search_theater_by_id(theater_id)
        if not theater: return False, "Theater not found."
        if cineplex.search_showtime_by_id(showtime_id): return False, "Showtime ID already exists."
        
        new_showtime = Showtime(showtime_id, movie, theater, status, subtitle, start_time, end_time, base_price)
        cineplex.add_showtime(new_showtime)
        return True, "Showtime created successfully."

    def process_create_coupon(self, coupon_type, coupon_id, name, discount, goods_list):
        if coupon_type.lower() == "discount":
            new_coupon = DiscountCoupon(coupon_id, name, discount)
        elif coupon_type.lower() == "exchange":
            new_coupon = ExchangeCoupon(coupon_id, name, goods_list)
        else:
            return False, "Invalid coupon_type. Use 'discount' or 'exchange'."
        
        self.__coupon_list.append(new_coupon)
        return True, "Coupon created successfully."

# ==========================================
# 4. API Routes (Clean Layer)
# ==========================================
system = JamorCineplex()

@app.post("/create_cineplex")
async def create_cineplex(req: CineplexCreate):
    success, msg = system.process_create_cineplex(req.cineplex_id, req.name)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}

@app.post("/create_movie")
async def create_movie(req: MovieCreate):
    success, msg = system.process_create_movie(
        req.cineplex_id, req.movie_id, req.name, req.duration, req.genre, req.age_rating
    )
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}

@app.post("/create_theater")
async def create_theater(req: TheaterCreate):
    success, msg = system.process_create_theater(req.cineplex_id, req.theater_id, req.type_theater)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}

@app.post("/create_seat")
async def create_seat(req: SeatCreate):
    success, msg = system.process_create_seat(
        req.cineplex_id, req.theater_id, req.seat_id, req.seat_number, req.type_seat
    )
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}

@app.post("/create_showtime")
async def create_showtime(req: ShowtimeCreate):
    success, msg = system.process_create_showtime(
        req.cineplex_id, req.showtime_id, req.movie_id, req.theater_id, 
        req.status, req.subtitle, req.start_time, req.end_time, req.base_price
    )
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}

@app.post("/create_coupon")
async def create_coupon(req: CouponCreate):
    success, msg = system.process_create_coupon(
        req.coupon_type, req.coupon_id, req.name, req.discount, req.goods_list
    )
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)