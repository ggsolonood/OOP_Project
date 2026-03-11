"""
routes_mcp.py
─────────────────────────────────────────────────────────────────────────────
MCP tool definitions สำหรับ JamorCineplex
แปลงมาจาก routes.py ทุก endpoint

ติดตั้ง dependency:
    pip install fastmcp

รันผ่าน:
    python mainfastmcp.py
─────────────────────────────────────────────────────────────────────────────
"""

from typing import Optional
from datetime import datetime
from fastmcp import FastMCP

from mock_data import system
from theater import Showtime

# ── shared MCP instance (import เข้า mainfastmcp.py) ──────────────────────
mcp = FastMCP("JamorCineplex")


# ═══════════════════════════════════════════════════════════════════════════
#  MOVIES
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_all_movies() -> dict:
    """ดูหนังทั้งหมดในระบบจากทุก Cineplex"""
    result = system.process_get_all_movies()
    return {"total": len(result), "movies": result}


@mcp.tool()
def get_today_showtimes() -> dict:
    """ดูรอบฉายทั้งหมดของวันนี้"""
    result = system.process_get_today_showtimes()
    today  = datetime.now().strftime("%Y-%m-%d")
    return {"date": today, "total": len(result), "showtimes": result}


@mcp.tool()
def get_showtimes_by_date(date: str) -> dict:
    """
    ดูรอบฉายของวันที่ระบุ (วันไหนก็ได้)

    Args:
        date: วันที่ต้องการ รูปแบบ "YYYY-MM-DD" เช่น "2026-03-11"
    """
    success, msg, result = system.process_get_showtimes_by_date(date)
    if not success:
        return {"error": msg}
    return {"date": date, "total": len(result), "showtimes": result}


@mcp.tool()
def search_showtimes_by_movie_name(movie_name: str) -> dict:
    """
    ค้นหารอบฉายจากชื่อหนัง (บางส่วนก็ได้)

    Args:
        movie_name: ชื่อหนัง หรือบางส่วนของชื่อ เช่น "Matrix"
    """
    result = system.process_get_showtimes_by_movie_name(movie_name)
    if not result:
        return {"error": f"ไม่พบรอบฉายของหนัง '{movie_name}'"}
    return {"search": movie_name, "total": len(result), "showtimes": result}


@mcp.tool()
def get_available_seats(cineplex_id: str, showtime_id: str) -> dict:
    """
    ดูที่นั่งว่างทั้งหมดในรอบฉาย พร้อมประเภทและราคา

    Args:
        cineplex_id: รหัส Cineplex เช่น "CPX01"
        showtime_id: รหัสรอบฉาย เช่น "ST01"
    """
    success, msg, data = system.process_get_available_seats(cineplex_id, showtime_id)
    if not success:
        return {"error": msg}
    return data


ADMIN_PASSWORD = "admin"

def _require_admin(admin_id: str) -> Optional[str]:
    """คืน None ถ้าผ่าน, คืน error string ถ้าไม่ผ่าน"""
    if admin_id != ADMIN_PASSWORD:
        return "Unauthorized: admin access required."
    return None


# ═══════════════════════════════════════════════════════════════════════════
#  ADMIN — Cinema Management
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def admin_get_all_showtimes(admin_id: str) -> dict:
    """
    (Admin) ดูรอบฉายที่ยังไม่เริ่มทั้งหมดในระบบ

    Args:
        admin_id: รหัส admin
    """
    if err := _require_admin(admin_id): return {"error": err}
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


@mcp.tool()
def admin_create_cineplex(admin_id: str, name: str) -> dict:
    """
    (Admin) สร้าง Cineplex ใหม่ — ชื่อต้องไม่ซ้ำกับที่มีอยู่

    Args:
        admin_id: รหัส admin
        name:     ชื่อ Cineplex เช่น "Central World"
    """
    if err := _require_admin(admin_id): return {"error": err}
    success, msg = system.process_create_cineplex(name)
    if not success:
        return {"error": msg}
    return msg


@mcp.tool()
def admin_create_movie(
    admin_id: str,
    cineplex_id: str,
    name: str,
    duration: int,
    genre: str,
    age_rating: str,
) -> dict:
    """
    (Admin) เพิ่มหนังใหม่เข้า Cineplex — ชื่อหนังต้องไม่ซ้ำภายใน Cineplex เดียวกัน

    Args:
        admin_id:    รหัส admin
        cineplex_id: รหัส Cineplex เช่น "CPX01"
        name:        ชื่อหนัง
        duration:    ความยาว (นาที)
        genre:       ประเภท เช่น "Action", "Sci-Fi"
        age_rating:  เรต เช่น "G", "13+", "18+"
    """
    if err := _require_admin(admin_id): return {"error": err}
    success, msg = system.process_create_movie(cineplex_id, name, duration, genre, age_rating)
    if not success:
        return {"error": msg}
    return msg


@mcp.tool()
def admin_create_theater(admin_id: str, cineplex_id: str, type_theater: str) -> dict:
    """
    (Admin) สร้างโรงภาพยนตร์ใหม่ใน Cineplex

    Args:
        admin_id:     รหัส admin
        cineplex_id:  รหัส Cineplex เช่น "CPX01"
        type_theater: ประเภทโรง — "Standard" | "IMAX" | "4DX" (case-insensitive)
    """
    if err := _require_admin(admin_id): return {"error": err}
    success, msg = system.process_create_theater(cineplex_id, type_theater)
    if not success:
        return {"error": msg}
    return msg


@mcp.tool()
def admin_create_seat(
    admin_id: str,
    cineplex_id: str,
    theater_id: str,
    seat_number: str,
    type_seat: str,
) -> dict:
    """
    (Admin) สร้างที่นั่งเดี่ยว

    Args:
        admin_id:    รหัส admin
        cineplex_id: รหัส Cineplex เช่น "CPX01"
        theater_id:  รหัสโรง เช่น "T01"
        seat_number: หมายเลขที่นั่ง เช่น "A1"
        type_seat:   ประเภท — "Normalseat" | "Sofa" | "Honeymoonbed" (case-insensitive)
    """
    if err := _require_admin(admin_id): return {"error": err}
    success, msg = system.process_create_seat(cineplex_id, theater_id, seat_number, type_seat)
    if not success:
        return {"error": msg}
    return msg


@mcp.tool()
def admin_create_seats_bulk(
    admin_id: str,
    cineplex_id: str,
    theater_id: str,
    seats: list[dict],
) -> dict:
    """
    (Admin) สร้างที่นั่งหลายที่พร้อมกัน

    Args:
        admin_id:    รหัส admin
        cineplex_id: รหัส Cineplex เช่น "CPX01"
        theater_id:  รหัสโรง เช่น "T01"
        seats:       รายการที่นั่ง รูปแบบ:
                     [{"seat_number": "A1", "type_seat": "Normalseat"}, ...]
                     type_seat: "Normalseat" | "Sofa" | "Honeymoonbed"
    """
    if err := _require_admin(admin_id): return {"error": err}
    success, result = system.process_create_seats_bulk(cineplex_id, theater_id, seats)
    if not success:
        return {"error": result}
    return {
        "message": f"Bulk seat creation done. Created: {len(result['created'])}, Failed: {len(result['failed'])}",
        "created": result["created"],
        "failed":  result["failed"],
    }


@mcp.tool()
def admin_create_showtime(
    admin_id: str,
    cineplex_id: str,
    movie_id: str,
    theater_id: str,
    status: str,
    subtitle: str,
    start_time: str,
    duration_minutes: int,
    base_price: float,
) -> dict:
    """
    (Admin) สร้างรอบฉายใหม่ — คำนวณ end_time จาก start_time + duration_minutes อัตโนมัติ

    Args:
        admin_id:         รหัส admin
        cineplex_id:      รหัส Cineplex เช่น "CPX01"
        movie_id:         รหัสหนัง เช่น "M01"
        theater_id:       รหัสโรง เช่น "T01"
        status:           สถานะ เช่น "Active"
        subtitle:         ภาษาซับ/พากย์ เช่น "TH", "EN"
        start_time:       เวลาเริ่ม รูปแบบ "YYYY-MM-DD HH:MM"
        duration_minutes: ความยาวรอบฉาย (นาที) เช่น 120
        base_price:       ราคาพื้นฐาน (บาท)
    """
    if err := _require_admin(admin_id): return {"error": err}
    success, msg = system.process_create_showtime(
        cineplex_id, movie_id, theater_id,
        status, subtitle, start_time, duration_minutes, base_price,
    )
    if not success:
        return {"error": msg}
    return msg


@mcp.tool()
def admin_create_coupon(
    admin_id: str,
    coupon_type: str,
    name: str,
    discount: float = 0.0,
    goods_list: Optional[list[str]] = None,
    last_date: Optional[str] = None,
) -> dict:
    """
    (Admin) สร้างคูปองใหม่

    Args:
        admin_id:    รหัส admin
        coupon_type: "discount" หรือ "exchange"
        name:        ชื่อคูปอง
        discount:    ส่วนลด (บาท) ใช้กับ type "discount"
        goods_list:  รายการสินค้า ใช้กับ type "exchange"
        last_date:   วันหมดอายุ รูปแบบ "YYYY-MM-DD HH:MM" (ไม่บังคับ)
    """
    if err := _require_admin(admin_id): return {"error": err}
    success, msg = system.process_create_coupon(
        coupon_type, name, discount, goods_list or [], last_date
    )
    if not success:
        return {"error": msg}
    return msg


@mcp.tool()
def admin_create_reward(admin_id: str, name: str, point_cost: int, stock: int) -> dict:
    """
    (Admin) สร้างของรางวัลสำหรับแลกคะแนน

    Args:
        admin_id:   รหัส admin
        name:       ชื่อของรางวัล
        point_cost: แต้มที่ต้องใช้แลก
        stock:      จำนวนสต็อก
    """
    if err := _require_admin(admin_id): return {"error": err}
    success, msg = system.process_create_reward(name, point_cost, stock)
    if not success:
        return {"error": msg}
    return msg


# ═══════════════════════════════════════════════════════════════════════════
#  STORE
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_all_rewards() -> dict:
    """ดูรายการของรางวัลทั้งหมดพร้อมแต้มที่ต้องใช้"""
    result = system.process_get_all_rewards()
    return {"total": len(result), "rewards": result}


@mcp.tool()
def get_all_coupon(user_id: str) -> dict:
    """
    ดูคูปองทั้งหมดในระบบ พร้อมสถานะและวันหมดอายุ

    Args:
        user_id: รหัสผู้ใช้ (ต้องมีอยู่ในระบบ)
    """
    success, msg, result = system.process_get_user_coupons(user_id)
    if not success:
        return {"error": msg}
    return {"message": msg, "total": len(result), "coupons": result}


@mcp.tool()
def get_goods_all() -> dict:
    """ดูสินค้าทั้งหมดที่มีให้ซื้อในทุก Cineplex พร้อมราคาและสต็อก"""
    result = system.process_get_goods_all()
    return {"total": len(result), "goods": result}


@mcp.tool()
def order_goods(
    cineplex_id: str,
    goods_name: str,
    quantity: int,
    user_id: str,
    account_id: str,
    coupon_id: Optional[str] = None,
) -> dict:
    """
    สั่งซื้อสินค้า (ป๊อปคอร์น, เครื่องดื่ม, ขนม) — ชำระเงินผ่านบัญชีธนาคาร

    วิธีใช้:
        1. เรียก get_goods_all() เพื่อดูสินค้าและราคาที่มี
        2. เรียก get_all_coupon(user_id) เพื่อดูคูปองที่ใช้ได้ (ถ้ามี)
        3. เรียก order_goods() พร้อมระบุ account_id ของบัญชีที่จะตัดเงิน

    Args:
        cineplex_id: รหัส Cineplex ที่ต้องการซื้อสินค้า เช่น "CPX01"
        goods_name:  ชื่อสินค้า ต้องตรงกับที่แสดงใน get_goods_all() เช่น "Popcorn Butter"
        quantity:    จำนวนที่ต้องการซื้อ
        user_id:     รหัสผู้ใช้ที่สั่งซื้อ
        account_id:  รหัสบัญชีธนาคารสำหรับตัดเงิน เช่น "13579"
        coupon_id:   รหัสคูปองส่วนลด (optional) เช่น "CPN-0001"
    """
    success, msg = system.process_order_goods(
        cineplex_id, goods_name, quantity, user_id, account_id, coupon_id
    )
    if not success:
        return {"error": msg}
    return {"message": "Order successful", "data": msg}


@mcp.tool()
def cancel_order(cineplex_id: str, order_id: str, user_id: str) -> dict:
    """
    ยกเลิกคำสั่งซื้อสินค้าและรับเงินคืน

    Args:
        cineplex_id: รหัส Cineplex เช่น "CPX01"
        order_id:    รหัสคำสั่งซื้อ เช่น "ORD-0001"
        user_id:     รหัสผู้ใช้
    """
    success, msg = system.process_cancel_order(cineplex_id, order_id, user_id)
    if not success:
        return {"error": msg}
    return {"message": msg}


@mcp.tool()
def exchange_reward(user_id: str, reward_id: str) -> dict:
    """
    แลกของรางวัลด้วยคะแนนสะสม

    Args:
        user_id:   รหัสผู้ใช้
        reward_id: รหัสของรางวัล เช่น "RWD-0001"
    """
    success, msg = system.process_exchange_reward(user_id, reward_id)
    if not success:
        return {"error": msg}
    return msg


# ═══════════════════════════════════════════════════════════════════════════
#  BOOKING
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def create_booking(
    user_id: str,
    cineplex_id: str,
    showtime_id: str,
    seat_nos: list[str],
) -> dict:
    """
    จองที่นั่งในรอบฉาย (สถานะ Pending รอชำระเงิน)

    Args:
        user_id:     รหัสผู้ใช้
        cineplex_id: รหัส Cineplex เช่น "CPX01"
        showtime_id: รหัสรอบฉาย เช่น "ST01"
        seat_nos:    รายการหมายเลขที่นั่ง เช่น ["A1", "A2"]
    """
    success, msg = system.process_create_booking(user_id, cineplex_id, showtime_id, seat_nos)
    if not success:
        return {"error": msg}
    return {"message": "Booking created", "data": msg}


@mcp.tool()
def confirm_booking(booking_id: str, user_id: str, account_id: str) -> dict:
    """
    ยืนยันการจองและชำระเงิน (เปลี่ยนสถานะเป็น Confirmed พร้อมออก Ticket)

    Args:
        booking_id: รหัสการจอง เช่น "BKG-00001"
        user_id:    รหัสผู้ใช้
        account_id: รหัสบัญชีสำหรับชำระเงิน
    """
    success, msg = system.process_confirm_booking(booking_id, user_id, account_id)
    if not success:
        return {"error": msg}
    return {"message": msg}


@mcp.tool()
def cancel_booking(booking_id: str, user_id: str) -> dict:
    """
    ยกเลิกการจอง (ไม่มีการคืนเงิน)

    Args:
        booking_id: รหัสการจอง เช่น "BKG-00001"
        user_id:    รหัสผู้ใช้
    """
    success, msg = system.process_cancel_booking(booking_id, user_id)
    if not success:
        return {"error": msg}
    return {"message": msg}


@mcp.tool()
def change_booking_seats(
    booking_id: str,
    user_id: str,
    new_seat_nos: list[str],
) -> dict:
    """
    เปลี่ยนที่นั่งในการจองที่มีอยู่ (จำนวนที่นั่งต้องเท่าเดิม)

    Args:
        booking_id:   รหัสการจอง เช่น "BKG-00001"
        user_id:      รหัสผู้ใช้
        new_seat_nos: รายการหมายเลขที่นั่งใหม่ เช่น ["B1", "B2"]
    """
    booking, msg = system.process_change_booking(user_id, booking_id, new_seat_nos)
    if not booking:
        return {"error": msg}
    return {
        "message":     msg,
        "booking_id":  booking.id,
        "status":      booking.status.value,
        "new_seats":   [s.seat_number for s in booking.showtime_seat],
        "total_price": booking.total_price,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  USERS
# ═══════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_all_users() -> dict:
    """ดูรายชื่อผู้ใช้ทั้งหมดในระบบ พร้อม tier และแต้มสะสม"""
    result = [
        {"id": u.id, "name": u.name, "tier": u.tier.value, "points": u.get_point()}
        for u in system.get_all_users()
    ]
    return {"users": result}


@mcp.tool()
def get_user_bookings(user_id: str, status_filter: Optional[str] = None) -> dict:
    """
    ดูประวัติการจองของผู้ใช้ (เฉพาะ Member ที่ลงทะเบียนแล้ว)

    Args:
        user_id:       รหัสผู้ใช้
        status_filter: กรองสถานะ — "Pending" | "Confirmed" | "Completed" | "Cancelled"
    """
    success, msg, data = system.process_get_booking_history(user_id, status_filter)
    if not success:
        return {"error": msg}
    user, bookings = data
    result = [{
        "booking_id": b.id,
        "movie":      b.showtime.movie.name,
        "status":     b.status.value,
        "seats":      [s.seat_number for s in b.showtime_seat],
        "price":      b.total_price,
    } for b in bookings]
    return {"member": user.name, "tier": user.tier.value, "bookings": result}


@mcp.tool()
def view_booking_history(user_id: str) -> dict:
    """
    ดูประวัติการจองทั้งหมดของผู้ใช้ (ไม่มี filter)

    Args:
        user_id: รหัสผู้ใช้
    """
    success, msg, booking_history = system.process_view_booking_history(user_id)
    if not success:
        return {"error": msg}
    if not booking_history:
        return {"message": msg, "booking_history": []}
    booking_history_data = [{
        "booking_id": b.id,
        "movie":      b.showtime.movie.name,
        "status":     b.status.value,
        "seats":      [s.seat_number for s in b.showtime_seat],
        "price":      b.total_price,
    } for b in booking_history]
    return {"message": msg, "booking_history": booking_history_data}


@mcp.tool()
def view_user_points(user_id: str) -> dict:
    """
    ดูแต้มสะสมของผู้ใช้

    Args:
        user_id: รหัสผู้ใช้
    """
    user = system.search_user_by_id(user_id)
    if not user:
        return {"error": "User not found"}
    return {"user_id": user_id, "name": user.name, "points": user.get_point()}


@mcp.tool()
def add_monthly_coupon(user_id: str) -> dict:
    """
    รับคูปองส่วนลดรายเดือน (50 บาท)
    รับได้ 1 ครั้งต่อเดือน เฉพาะ member ที่ลงทะเบียนแล้ว (ไม่ใช่ GUEST)

    Args:
        user_id: รหัสผู้ใช้
    """
    success, msg, data = system.process_get_monthly_coupon(user_id)
    if not success:
        return {"error": msg}
    return {"message": msg, "data": data}


@mcp.tool()
def create_guest_user(name: str, email: str = "") -> dict:
    """
    สร้าง User ใหม่แบบ Guest (ยังไม่มี password)
    ใช้ user_id ที่ได้รับไปเรียก register_user เพื่อสมัครสมาชิก

    Args:
        name:  ชื่อผู้ใช้ (required)
        email: อีเมล (optional)
    """
    success, result = system.process_register_guest(name, email)
    if not success:
        return {"error": result}
    return result


@mcp.tool()
def register_user(
    user_id: str,
    password: str,
    phone_number: str = "",
    birthday: str = "",
) -> dict:
    """
    สมัครสมาชิก — เปลี่ยน Guest → Silver พร้อมตั้งรหัสผ่าน

    Args:
        user_id:      รหัสผู้ใช้ที่ได้จาก create_guest_user
        password:     รหัสผ่าน (อย่างน้อย 4 ตัวอักษร)
        phone_number: เบอร์โทร (optional)
        birthday:     วันเกิด รูปแบบ DD-MM-YYYY (optional)
    """
    success, result = system.process_register(user_id, password, phone_number, birthday)
    if not success:
        return {"error": result}
    return result


@mcp.tool()
def login_user(user_id: str, password: str) -> dict:
    """
    เข้าสู่ระบบ

    Args:
        user_id:  รหัสผู้ใช้
        password: รหัสผ่าน
    """
    success, result = system.process_login(user_id, password)
    if not success:
        return {"error": result}
    return result