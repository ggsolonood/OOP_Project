from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from theater import Showtime
from enums import BookingStatus

admin_router   = APIRouter(prefix="/admin",   tags=["Cinema Management"])
store_router   = APIRouter(prefix="/store",   tags=["Store"])
booking_router = APIRouter(prefix="/booking", tags=["Booking"])
user_router    = APIRouter(prefix="/users",   tags=["Users"])
movie_router   = APIRouter(prefix="/movies",  tags=["Movies"])


def get_system():
    from mock_data import system
    return system


## ── ROUTES_MOVIES ─────────────────────────────────────────────────────────

@movie_router.get("/")
def get_all_movies():
    """
    ดูหนังทั้งหมดในระบบ
    - รวมทุก cineplex, ไม่ซ้ำ movie_id
    """
    result = get_system().process_get_all_movies()
    return {
        "total": len(result),
        "movies": result,
    }


@movie_router.get("/showtimes/today")
def get_today_showtimes():
    """
    ดูรอบฉายวันนี้ทั้งหมด
    - กรองเฉพาะ showtime ที่ start_time เป็นวันเดียวกับวันนี้
    """
    result = get_system().process_get_today_showtimes()
    today  = datetime.now().strftime("%Y-%m-%d")
    return {
        "date":   today,
        "total":  len(result),
        "showtimes": result,
    }


@movie_router.get("/showtimes/search")
def get_showtimes_by_movie_name(movie_name: str = Query(..., description="ชื่อหนัง (บางส่วนก็ได้)")):
    """
    ดูรอบฉายตามชื่อหนัง
    - รองรับ partial match และ case-insensitive
    - เช่น `?movie_name=matrix` จะเจอ "The Matrix"
    """
    result = get_system().process_get_showtimes_by_movie_name(movie_name)
    if not result:
        raise HTTPException(status_code=404, detail=f"ไม่พบรอบฉายของหนัง '{movie_name}'")
    return {
        "search":    movie_name,
        "total":     len(result),
        "showtimes": result,
    }


## ── ROUTES_ADMIN ──────────────────────────────────────────────────────────

@admin_router.post("/cineplex/")
def create_cineplex(cineplex_id: str, name: str):
    success, msg = get_system().process_create_cineplex(cineplex_id, name)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.post("/movie/")
def create_movie(cineplex_id: str, movie_id: str, name: str,
                 duration: int, genre: str, age_rating: str):
    success, msg = get_system().process_create_movie(cineplex_id, movie_id, name, duration, genre, age_rating)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.post("/theater/")
def create_theater(cineplex_id: str, theater_id: str, type_theater: str):
    """**type_theater**: `Standard` | `IMAX` | `4DX`  (case-insensitive)"""
    success, msg = get_system().process_create_theater(cineplex_id, theater_id, type_theater)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.post("/seat/")
def create_seat(cineplex_id: str, theater_id: str, seat_id: str,
                seat_number: str, type_seat: str):
    """**type_seat**: `Normalseat` | `Sofa` | `Honeymoonbed`  (case-insensitive)"""
    success, msg = get_system().process_create_seat(cineplex_id, theater_id, seat_id, seat_number, type_seat)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.post("/showtime/")
def create_showtime(cineplex_id: str, showtime_id: str, movie_id: str, theater_id: str,
                    status: str, subtitle: str, start_time: str, end_time: str, base_price: float):
    """
    **start_time / end_time** format: `YYYY-MM-DD HH:MM`  เช่น `2026-03-10 14:30`
    ระบบเช็ค time conflict อัตโนมัติ
    """
    success, msg = get_system().process_create_showtime(
        cineplex_id, showtime_id, movie_id, theater_id,
        status, subtitle, start_time, end_time, base_price,
    )
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.post("/coupon/")
def create_coupon(coupon_type: str, coupon_id: str, name: str,
                  discount: float = 0.0,
                  goods_list: List[str] = Query(default=[]),
                  last_date: Optional[str] = None):
    """**last_date** format: `YYYY-MM-DD HH:MM`  ละไว้ = ไม่มีวันหมดอายุ"""
    success, msg = get_system().process_create_coupon(coupon_type, coupon_id, name, discount,
                                                      goods_list, last_date)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.get("/showtimes/")
def get_all_showtimes():
    """แสดงรอบฉายที่ยังไม่เริ่ม (start_time >= ปัจจุบัน)"""
    now    = datetime.now()
    result = []
    for cineplex in get_system().cineplex_list:
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


## ── ROUTES_STORE ──────────────────────────────────────────────────────────

@store_router.post("/order/")
def order_goods(cineplex_id: str, goods_name: str, quantity: int,
                user_id: str, account_id: str, coupon_id: Optional[str] = None):
    success, msg = get_system().process_order_goods(cineplex_id, goods_name, quantity,
                                                    user_id, account_id, coupon_id)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": "Order successful", "data": msg}


@store_router.delete("/order/{cineplex_id}/{order_id}")
def cancel_order(cineplex_id: str, order_id: str, user_id: str):
    success, msg = get_system().process_cancel_order(cineplex_id, order_id, user_id)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


## ── ROUTES_BOOKING ────────────────────────────────────────────────────────

@booking_router.post("/")
def create_booking(booking_id: str, user_id: str, cineplex_id: str, showtime_id: str,
                   seat_nos: List[str] = Query(..., description="รายการที่นั่ง เช่น A1, A2")):
    success, msg = get_system().process_create_booking(booking_id, user_id, cineplex_id,
                                                       showtime_id, seat_nos)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": "Booking created", "data": msg}


@booking_router.post("/{booking_id}/confirm")
def confirm_booking(booking_id: str, user_id: str, account_id: str):
    success, msg = get_system().process_confirm_booking(booking_id, user_id, account_id)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@booking_router.delete("/{booking_id}")
def cancel_booking(booking_id: str, user_id: str):
    success, msg = get_system().process_cancel_booking(booking_id, user_id)
    if not success: raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@booking_router.put("/{booking_id}/seats")
def change_booking_seats(booking_id: str, user_id: str,
                         new_seat_nos: List[str] = Query(...)):
    booking, msg = get_system().process_change_booking(user_id, booking_id, new_seat_nos)
    if not booking: raise HTTPException(status_code=400, detail=msg)
    return {
        "message":     msg,
        "booking_id":  booking.id,
        "status":      booking.status.value,
        "new_seats":   [s.seat_number for s in booking.showtime_seat],
        "total_price": booking.total_price,
    }


## ── ROUTES_USERS ──────────────────────────────────────────────────────────

@user_router.get("/")
def get_all_users():
    result = [
        {"id": u.id, "name": u.name, "tier": u.tier.value, "points": u.get_point()}
        for u in get_system().get_all_users()
    ]
    return {"users": result}


@user_router.get("/{user_id}/bookings")
def get_user_bookings(user_id: str, status_filter: Optional[str] = None):
    success, msg, data = get_system().process_get_booking_history(user_id, status_filter)
    if not success: raise HTTPException(status_code=400, detail=msg)
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
    success , msg , booking_history = get_system().process_view_booking_history(user_id)
    if not success : raise HTTPException(status_code=400 , detail=msg)
    booking_history_data = []
    for b in booking_history :
        booking_history_data.append({
            "booking_id": b.id,
            "movie":      b.showtime.movie.name,
            "status":     b.status.value,
            "seats":      [s.seat_number for s in b.showtime_seat],
            "price":      b.total_price,
        })
    return {"message":msg,"booking history":booking_history_data}
