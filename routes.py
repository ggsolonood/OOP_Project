from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from mock_data import system

# ==========================================
# Routers
# ==========================================

admin_router   = APIRouter(prefix="/admin",   tags=["Cinema Management"])
store_router   = APIRouter(prefix="/store",   tags=["Store"])
booking_router = APIRouter(prefix="/booking", tags=["Booking"])
user_router    = APIRouter(prefix="/users",   tags=["Users"])


# ==========================================
# Cinema Management Routes
# ==========================================

@admin_router.post("/cineplex/")
def create_cineplex(cineplex_id: str, name: str):
    success, msg = system.process_create_cineplex(cineplex_id, name)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.post("/movie/")
def create_movie(cineplex_id: str, movie_id: str, name: str,
                 duration: int, genre: str, age_rating: str):
    success, msg = system.process_create_movie(cineplex_id, movie_id, name, duration, genre, age_rating)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.post("/theater/")
def create_theater(cineplex_id: str, theater_id: str, type_theater: str):
    success, msg = system.process_create_theater(cineplex_id, theater_id, type_theater)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.post("/seat/")
def create_seat(cineplex_id: str, theater_id: str, seat_id: str,
                seat_number: str, type_seat: str):
    success, msg = system.process_create_seat(cineplex_id, theater_id, seat_id, seat_number, type_seat)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.post("/showtime/")
def create_showtime(cineplex_id: str, showtime_id: str, movie_id: str, theater_id: str,
                    status: str, subtitle: str, start_time: str, end_time: str, base_price: float):
    success, msg = system.process_create_showtime(
        cineplex_id, showtime_id, movie_id, theater_id,
        status, subtitle, start_time, end_time, base_price,
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.post("/coupon/")
def create_coupon(coupon_type: str, coupon_id: str, name: str,
                  discount: float = 0.0,
                  goods_list: List[str] = Query(default=[])):
    success, msg = system.process_create_coupon(coupon_type, coupon_id, name, discount, goods_list)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@admin_router.get("/showtimes/")
def get_all_showtimes():
    current_time = datetime.now().time()
    result = []

    for cineplex in system.cineplex_list:
        for showtime in cineplex.showtime_list:
            try:
                st_time = datetime.strptime(showtime.start_time, "%H:%M").time()
            except ValueError:
                continue

            if st_time >= current_time:
                result.append({
                    "cineplex_name": cineplex.get_cineplex_name(),
                    "showtime_id": showtime.id,
                    "movie_name": showtime.movie.name,
                    "theater_id": showtime.theater.id,
                    "start_time": showtime.start_time,
                    "end_time": showtime.end_time,
                    "price": showtime.base_price,
                })

    return {
        "current_time_now": current_time.strftime("%H:%M"),
        "total_available": len(result),
        "showtimes": result,
    }


# ==========================================
# Store Routes
# ==========================================

@store_router.post("/order/")
def order_goods(cineplex_id: str, goods_name: str, quantity: int,
                user_id: str, account_id: str,
                coupon_id: Optional[str] = None):
    success, msg = system.process_order_goods(cineplex_id, goods_name, quantity, user_id, account_id, coupon_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": "Order successful", "data": msg}


@store_router.delete("/order/{cineplex_id}/{order_id}")
def cancel_order(cineplex_id: str, order_id: str, user_id: str):
    success, msg = system.process_cancel_order(cineplex_id, order_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


# ==========================================
# Booking Routes
# ==========================================

@booking_router.post("/")
def create_booking(booking_id: str, user_id: str, cineplex_id: str, showtime_id: str,
                   seat_nos: List[str] = Query(..., description="รายการที่นั่ง เช่น A1, A2")):
    success, msg = system.process_create_booking(booking_id, user_id, cineplex_id, showtime_id, seat_nos)
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
def change_booking_seats(booking_id: str, user_id: str,
                         new_seat_nos: List[str] = Query(..., description="รายการที่นั่งใหม่ที่ต้องการเปลี่ยน")):
    booking, msg = system.process_change_booking(user_id, booking_id, new_seat_nos)
    if not booking:
        raise HTTPException(status_code=400, detail=msg)
    return {
        "message": msg,
        "booking_id": booking.id,
        "status": booking.status.value,
        "new_seats": [s.seat_number for s in booking.showtime_seat],
        "total_price": booking.total_price,
    }


# ==========================================
# User & History Routes
# ==========================================

@user_router.get("/")
def get_all_users():
    users = system.get_all_users()
    result = [
        {"id": u.id, "name": u.name, "tier": u.tier.value, "points": u.get_point()}
        for u in users
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
        "movie": b.showtime.movie.name,
        "status": b.status.value,
        "seats": [s.seat_number for s in b.showtime_seat],
        "price": b.total_price,
    } for b in bookings]
    return {"member": user.name, "tier": user.tier.value, "bookings": result}
