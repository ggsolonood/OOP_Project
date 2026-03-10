from typing import List, Optional
from pydantic import BaseModel


class CineplexCreate(BaseModel):
    name: str

class MovieCreate(BaseModel):
    cineplex_id: str
    name: str
    duration: int
    genre: str
    age_rating: str

class TheaterCreate(BaseModel):
    cineplex_id: str
    type_theater: str   # "Standard" | "IMAX" | "4DX"  (case-insensitive)

class SeatCreate(BaseModel):
    cineplex_id: str
    theater_id: str
    seat_number: str
    type_seat: str      # "Normalseat" | "Sofa" | "Honeymoonbed"  (case-insensitive)

class ShowtimeCreate(BaseModel):
    cineplex_id: str
    movie_id: str
    theater_id: str
    status: str
    subtitle: str
    start_time: str   # "YYYY-MM-DD HH:MM"
    end_time: str     # "YYYY-MM-DD HH:MM"
    base_price: float

class CouponCreate(BaseModel):
    coupon_type: str
    name: str
    discount: float = 0.0
    goods_list: List[str] = []
    last_date: Optional[str] = None   # "YYYY-MM-DD HH:MM"  หรือ null

class OrderGoodsRequest(BaseModel):
    cineplex_id: str
    goods_name: str
    quantity: int
    user_id: str
    account_id: str
    coupon_id: Optional[str] = None

class BookingCreate(BaseModel):
    user_id: str
    cineplex_id: str
    showtime_id: str
    seat_nos: List[str]

class BookingConfirm(BaseModel):
    user_id: str
    account_id: str

class BookingChangeSeats(BaseModel):
    user_id: str
    new_seat_nos: List[str]