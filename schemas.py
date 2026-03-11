from pydantic import BaseModel
from typing import List, Optional


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
    type_theater: str


class SeatCreate(BaseModel):
    cineplex_id: str
    theater_id: str
    seat_number: str
    type_seat: str


class ShowtimeCreate(BaseModel):
    cineplex_id: str
    movie_id: str
    theater_id: str
    status: str
    subtitle: str
    start_time: str
    end_time: str
    base_price: float


class CouponCreate(BaseModel):
    coupon_type: str
    name: str
    discount: float = 0.0
    goods_list: List[str] = []
    last_date: Optional[str] = None


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


class RewardCreate(BaseModel):
    name: str
    point_cost: int
    stock: int


class RewardExchange(BaseModel):
    user_id: str
    reward_id: str
