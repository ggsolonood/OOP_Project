from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from mock_data import system
from theater import Showtime
from enums import BookingStatus
from schemas import (
    CineplexCreate, MovieCreate, TheaterCreate, SeatCreate, SeatsBulkCreate, ShowtimeCreate,
    CouponCreate, BookingCreate, BookingChangeSeats,
    RewardCreate, RewardExchange,
)

admin_router   = APIRouter(prefix="/admin",   tags=["Cinema Management"])
store_router   = APIRouter(prefix="/store",   tags=["Store"])
booking_router = APIRouter(prefix="/booking", tags=["Booking"])
user_router    = APIRouter(prefix="/users",   tags=["Users"])
movie_router   = APIRouter(prefix="/movies",  tags=["Movies"])


# ── MOVIES ────────────────────────────────────────────────────────────────

@movie_router.get("/")
def get_all_movies():
    result = system.process_get_all_movies()
    return {"total": len(result), "movies": result}


@movie_router.get("/showtimes/today")
def get_today_showtimes():
    result = system.process_get_today_showtimes()
    today  = datetime.now().strftime("%Y-%m-%d")
    return {"date": today, "total": len(result), "showtimes": result}


@movie_router.get("/showtimes/search")
def get_showtimes_by_movie_name(movie_name: str = Query(..., description="ชื่อหนัง (บางส่วนก็ได้)")):
    result = system.process_get_showtimes_by_movie_name(movie_name)
    if not result:
        raise HTTPException(status_code=404, detail=f"ไม่พบรอบฉายของหนัง '{movie_name}'")
    return {"search": movie_name, "total": len(result), "showtimes": result}


@movie_router.get("/showtimes/{cineplex_id}/{showtime_id}/available-seats")
def get_available_seats(cineplex_id: str, showtime_id: str):
    """ดูที่นั่งว่างทั้งหมดในรอบฉาย พร้อมประเภทและราคา"""
    success, msg, data = system.process_get_available_seats(cineplex_id, showtime_id)
    if not success:
        raise HTTPException(status_code=404, detail=msg)
    return data


# ── ADMIN ─────────────────────────────────────────────────────────────────

@admin_router.post("/cineplex/")
def create_cineplex(body: CineplexCreate):
    success, msg = system.process_create_cineplex(body.name)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return msg


@admin_router.post("/movie/")
def create_movie(body: MovieCreate):
    success, msg = system.process_create_movie(
        body.cineplex_id, body.name, body.duration, body.genre, body.age_rating
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return msg


@admin_router.post("/theater/")
def create_theater(body: TheaterCreate):
    """**type_theater**: `Standard` | `IMAX` | `4DX`  (case-insensitive)"""
    success, msg = system.process_create_theater(body.cineplex_id, body.type_theater)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return msg


@admin_router.post("/seat/")
def create_seat(body: SeatCreate):
    """สร้าง seat เดี่ยว — **type_seat**: `Normalseat` | `Sofa` | `Honeymoonbed`  (case-insensitive)"""
    success, msg = system.process_create_seat(
        body.cineplex_id, body.theater_id, body.seat_number, body.type_seat
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return msg


@admin_router.post("/seats/bulk")
def create_seats_bulk(body: SeatsBulkCreate):
    """
    สร้าง seat หลายที่นั่งพร้อมกัน
    **type_seat**: `Normalseat` | `Sofa` | `Honeymoonbed` (case-insensitive)
    ```json
    {
      "cineplex_id": "CPX01",
      "theater_id": "T01",
      "seats": [
        {"seat_number": "A1", "type_seat": "Normalseat"},
        {"seat_number": "B1", "type_seat": "Sofa"}
      ]
    }
    ```
    """
    seat_dicts = [s.model_dump() for s in body.seats]
    success, result = system.process_create_seats_bulk(
        body.cineplex_id, body.theater_id, seat_dicts
    )
    if not success:
        raise HTTPException(status_code=400, detail=result)
    return {
        "message":       f"Bulk seat creation done. Created: {len(result['created'])}, Failed: {len(result['failed'])}",
        "created":       result["created"],
        "failed":        result["failed"],
    }


@admin_router.post("/showtime/")
def create_showtime(body: ShowtimeCreate):
    """**start_time / end_time** format: `YYYY-MM-DD HH:MM`"""
    success, msg = system.process_create_showtime(
        body.cineplex_id, body.movie_id, body.theater_id,
        body.status, body.subtitle, body.start_time, body.base_price
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return msg


@admin_router.post("/coupon/")
def create_coupon(body: CouponCreate):
    success, msg = system.process_create_coupon(
        body.coupon_type, body.name, body.discount, body.goods_list, body.last_date
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return msg


@admin_router.post("/reward/")
def create_reward(body: RewardCreate):
    success, msg = system.process_create_reward(body.name, body.point_cost, body.stock)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return msg


@admin_router.get("/showtimes/")
def get_all_showtimes():
    now    = datetime.now()
    result = []
    for cineplex in system.cineplex_list:
        for showtime in cineplex.showtime_list:
            if showtime.is_upcoming():
                result.append({
                    "cineplex_name": cineplex.get_cineplex_name(),
                    "showtime_id":   showtime.id,
                    "movie_name":    showtime.movie.name,
                    "theater_id":    showtime.theater.id,
                    "theater_type":  showtime.theater.type_theater.value,
                    "start_time":    showtime.start_time.strftime(Showtime.DT_FORMAT),
                    "end_time":      showtime.end_time.strftime(Showtime.DT_FORMAT),
                    "price":         showtime.base_price,
                })
    return {
        "current_datetime": now.strftime(Showtime.DT_FORMAT),
        "total_available":  len(result),
        "showtimes":        result,
    }


# ── STORE ─────────────────────────────────────────────────────────────────

@store_router.post("/order/")
def order_goods(cineplex_id: str, goods_name: str, quantity: int,
                user_id: str, account_id: str, coupon_id: Optional[str] = None):
    success, msg = system.process_order_goods(cineplex_id, goods_name, quantity,
                                              user_id, account_id, coupon_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": "Order successful", "data": msg}


@store_router.delete("/order/{cineplex_id}/{order_id}")
def cancel_order(cineplex_id: str, order_id: str, user_id: str):
    success, msg = system.process_cancel_order(cineplex_id, order_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@store_router.get("/rewards/")
def get_all_rewards():
    result = system.process_get_all_rewards()
    return {"total": len(result), "rewards": result}


@store_router.post("/exchange_reward/")
def exchange_reward(body: RewardExchange):
    success, msg = system.process_exchange_reward(body.user_id, body.reward_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return msg


# ── BOOKING ───────────────────────────────────────────────────────────────

@booking_router.post("/")
def create_booking(body: BookingCreate):
    success, msg = system.process_create_booking(
        body.user_id, body.cineplex_id,
        body.showtime_id, body.seat_nos,
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": "Booking created", "data": msg}


@booking_router.post("/{booking_id}/confirm")
def confirm_booking(booking_id: str, user_id: str, account_id: str):
    success, msg = system.process_confirm_booking(booking_id, user_id, account_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@booking_router.delete("/{booking_id}")
def cancel_booking(booking_id: str, user_id: str):
    success, msg = system.process_cancel_booking(booking_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@booking_router.put("/{booking_id}/seats")
def change_booking_seats(booking_id: str, body: BookingChangeSeats):
    booking, msg = system.process_change_booking(body.user_id, booking_id, body.new_seat_nos)
    if not booking:
        raise HTTPException(status_code=400, detail=msg)
    return {
        "message":     msg,
        "booking_id":  booking.id,
        "status":      booking.status.value,
        "new_seats":   [s.seat_number for s in booking.showtime_seat],
        "total_price": booking.total_price,
    }


# ── USERS ─────────────────────────────────────────────────────────────────

@user_router.get("/")
def get_all_users():
    result = [
        {"id": u.id, "name": u.name, "tier": u.tier.value, "points": u.get_point()}
        for u in system.get_all_users()
    ]
    return {"users": result}


@user_router.get("/{user_id}/bookings")
def get_user_bookings(user_id: str, status_filter: Optional[str] = None):
    success, msg, data = system.process_get_booking_history(user_id, status_filter)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    user, bookings = data
    result = [{
        "booking_id": b.id,
        "movie":      b.showtime.movie.name,
        "status":     b.status.value,
        "seats":      [s.seat_number for s in b.showtime_seat],
        "price":      b.total_price,
    } for b in bookings]
    return {"member": user.name, "tier": user.tier.value, "bookings": result}


@user_router.get("/{user_id}/history_booking")
def view_booking_history(user_id: str):
    success, msg, booking_history = system.process_view_booking_history(user_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    booking_history_data = [{
        "booking_id": b.id,
        "movie":      b.showtime.movie.name,
        "status":     b.status.value,
        "seats":      [s.seat_number for s in b.showtime_seat],
        "price":      b.total_price,
    } for b in booking_history]
    return {"message": msg, "booking_history": booking_history_data}


@user_router.get("/{user_id}/points")
def view_point(user_id: str):
    user = system.search_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user_id,
        "name":    user.name,
        "points":  user.get_point(),
    }


@user_router.post("/{user_id}/addcouponmon")
def add_monthly_coupon(user_id: str):
    """รับคูปองส่วนลดรายเดือน (50 บาท) — รับได้ 1 ครั้ง/เดือน เฉพาะ member ที่ลงทะเบียนแล้ว"""
    success, msg, data = system.process_get_monthly_coupon(user_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "data": data}


@user_router.post("/")
def register(user_id: str, password: str):
    success, result = system.process_register(user_id, password)
    if not success:
        raise HTTPException(status_code=400, detail=result)
    return result


@user_router.post("/login")
def login(user_id: str, password: str):
    success, result = system.process_login(user_id, password)
    if not success:
        raise HTTPException(status_code=401, detail=result)
    return result

@user_router.post("/{user_id}/review_movie")
def review_movie(user_id:str,booking_id:str,star:int,comment:str) :
    success , msg = system.process_review_movie(user_id,booking_id,star,comment)
    if not success : raise HTTPException(status_code=400 , detail=msg)
    return  {"message":msg}