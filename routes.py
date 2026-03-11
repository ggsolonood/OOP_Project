from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from mock_data import system
from theater import Showtime
from enums import BookingStatus
from schemas import (
    CineplexCreate, MovieCreate, TheaterCreate, SeatCreate, SeatsBulkCreate, ShowtimeCreate,
    CouponCreate, BookingCreate, BookingChangeSeats,
    RewardCreate, RewardExchange, GuestCreate, RegisterMember, OrderGoodsRequest,
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


@movie_router.get("/showtimes/date")
def get_showtimes_by_date(date: str = Query(..., description="วันที่ต้องการดู รูปแบบ YYYY-MM-DD เช่น 2026-03-11")):
    """ดูรอบฉายของวันที่ระบุ (วันไหนก็ได้)"""
    success, msg, result = system.process_get_showtimes_by_date(date)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"date": date, "total": len(result), "showtimes": result}


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

@store_router.get("/goods/")
def get_all_goods():
    """ดูสินค้าทั้งหมดที่มีให้ซื้อในทุก Cineplex พร้อมราคาและสต็อก"""
    result = system.process_get_goods_all()
    return {"total": len(result), "goods": result}


@store_router.post("/order/")
def order_goods(body: OrderGoodsRequest):
    """
    สั่งซื้อสินค้า
    - **goods_name**: ต้องตรงกับชื่อใน `GET /store/goods/`
    - **account_id**: รหัสบัญชีธนาคารสำหรับตัดเงิน
    - **coupon_id**: รหัสคูปอง (optional) ดูได้จาก `GET /users/{user_id}/coupons`
    """
    success, msg = system.process_order_goods(
        body.cineplex_id, body.goods_name, body.quantity,
        body.user_id, body.account_id, body.coupon_id
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": "Order successful", "data": msg}


@store_router.delete("/order/{cineplex_id}/{order_id}")
def cancel_order(cineplex_id: str, order_id: str, user_id: str):
    success, msg = system.process_cancel_order(cineplex_id, order_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@store_router.get("/orders/{user_id}")
def get_order_history(user_id: str, status: Optional[str] = None):
    """
    ดูประวัติการสั่งซื้อสินค้าของ user
    - **status** (optional): `Completed` | `Cancelled` | `Refunded`
    """
    success, msg, result = system.process_get_order_history(user_id, status)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "total": len(result), "orders": result}


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


# ⚠️ Static routes (/guest, /login) ต้องอยู่ก่อน dynamic routes (/{user_id})
# มิฉะนั้น FastAPI จะ match "guest" และ "login" เป็น user_id แทน

@user_router.post("/guest")
def create_guest(body: GuestCreate):
    """
    สร้าง User ใหม่แบบ Guest
    - ต้องการแค่ **name** (email ถ้ามีก็ใส่ได้)
    - tier = GUEST, ยังไม่มี password
    - ใช้ user_id ที่ได้รับไปเรียก `/{user_id}/register` เพื่อสมัครสมาชิก
    """
    success, result = system.process_register_guest(body.name, body.email)
    if not success:
        raise HTTPException(status_code=400, detail=result)
    return result


@user_router.post("/login")
def login(user_id: str, password: str):
    success, result = system.process_login(user_id, password)
    if not success:
        raise HTTPException(status_code=401, detail=result)
    return result


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


@user_router.get("/{user_id}/coupons")
def get_user_coupons(user_id: str):
    """ดูคูปองทั้งหมดในระบบ พร้อมสถานะและวันหมดอายุ"""
    success, msg, result = system.process_get_user_coupons(user_id)
    if not success:
        raise HTTPException(status_code=404, detail=msg)
    return {"message": msg, "total": len(result), "coupons": result}


@user_router.get("/{user_id}/reward-history")
def get_reward_history(user_id: str):
    """ดูประวัติการแลกของรางวัล — Guest ไม่สามารถใช้งานได้"""
    success, msg, result = system.process_get_reward_history(user_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "total": len(result), "reward_history": result}


@user_router.post("/{user_id}/addcouponmon")
def add_monthly_coupon(user_id: str):
    """รับคูปองส่วนลดรายเดือน (50 บาท) — รับได้ 1 ครั้ง/เดือน เฉพาะ member ที่ลงทะเบียนแล้ว"""
    success, msg, data = system.process_get_monthly_coupon(user_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "data": data}


@user_router.post("/{user_id}/register")
def register(user_id: str, body: RegisterMember):
    """
    สมัครสมาชิก — เปลี่ยน Guest → Silver
    - **password**: อย่างน้อย 4 ตัวอักษร (required)
    - **phone_number**: เบอร์โทร (optional)
    - **birthday**: วันเกิด รูปแบบ DD-MM-YYYY (optional)
    """
    success, result = system.process_register(
        user_id, body.password, body.phone_number, body.birthday
    )
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

@user_router.get("/{user_id}/view_review")
def read_review(movie_id: str):
    result = system.process_read_review(movie_id)
    return {"message": result}