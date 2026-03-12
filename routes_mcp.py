from fastmcp import FastMCP
from mock_data import system

mcp = FastMCP("JamorCineplex")

@mcp.tool()
def get_all_movies() -> list:
    """แสดงรายการหนังทั้งหมดที่มีให้ดู"""
    return system.get_all_movies()

@mcp.tool()
def get_showtimes_by_movie(movie_id: str) -> dict:
    """แสดงรอบฉายของหนังจาก movie_id (เช่น M01)"""
    success, res = system.get_showtimes_by_movie(movie_id)
    return {"success": success, "result": res}

@mcp.tool()
def get_available_seats(showtime_id: str) -> dict:
    """แสดงที่นั่งว่างและราคาในรอบฉายนั้นๆ (เช่น ST01)"""
    success, res = system.get_available_seats(showtime_id)
    return {"success": success, "result": res}

@mcp.tool()
def book_ticket(user_id: str, showtime_id: str, seat_ids: list[str], coupon_id: str = None) -> dict:
    """จองตั๋วที่นั่งของรอบฉาย (เช่น user_id="U01", showtime_id="ST01", seat_ids=["S_T01_01"])"""
    success, res = system.book_ticket(user_id, showtime_id, seat_ids, coupon_id)
    return {"success": success, "result": res}

@mcp.tool()
def confirm_booking(booking_id: str, account_id: str) -> dict:
    """ยืนยันการจองโดยการจ่ายเงิน (ตัดเงินจาก account_id เช่น ACC01)"""
    success, res = system.confirm_booking(booking_id, account_id)
    return {"success": success, "result": res}

@mcp.tool()
def cancel_booking(booking_id: str) -> dict:
    """ยกเลิกการจองพร้อมคืนเงิน (ถ้าจ่ายไปแล้ว)"""
    success, res = system.cancel_booking(booking_id)
    return {"success": success, "result": res}

@mcp.tool()
def order_goods(user_id: str, cineplex_id: str, items_dict: dict, account_id: str, coupon_id: str = None) -> dict:
    """สั่งซื้อขนม/น้ำ (เช่น items_dict={"G01": 2, "G02": 1})"""
    success, res = system.order_goods(user_id, cineplex_id, items_dict, account_id, coupon_id)
    return {"success": success, "result": res}

@mcp.tool()
def cancel_order(order_id: str, cineplex_id: str) -> dict:
    """ยกเลิกคำสั่งซื้อสินค้าและคืนเงิน"""
    success, res = system.cancel_order(order_id, cineplex_id)
    return {"success": success, "result": res}

@mcp.tool()
def upgrade_member(user_id: str, account_id: str) -> dict:
    """อัปเกรดผู้ใช้ Guest เป็น Silver Member (จ่าย 500 บาท)"""
    success, res = system.upgrade_member(user_id, account_id)
    return {"success": success, "result": res}

@mcp.tool()
def view_history(user_id: str) -> dict:
    """ดูประวัติการจองของผู้ใช้"""
    success, res = system.view_history(user_id)
    return {"success": success, "result": res}

@mcp.tool()
def show_points_and_rewards(user_id: str) -> dict:
    """ดูพ้อยท์ปัจจุบันของ Member และรายการของรางวัลที่แลกได้"""
    success, res = system.show_points_and_rewards(user_id)
    return {"success": success, "result": res}

@mcp.tool()
def redeem_reward(user_id: str, reward_id: str) -> dict:
    """ใช้พ้อยท์แลกของรางวัล (เช่น reward_id="R01")"""
    success, res = system.redeem_reward(user_id, reward_id)
    return {"success": success, "result": res}

@mcp.tool()
def collect_monthly_coupon(user_id: str, coupon_id: str) -> dict:
    """เก็บคูปองส่วนลดประจำเดือน (เฉพาะ Member)"""
    success, res = system.collect_monthly_coupon(user_id, coupon_id)
    return {"success": success, "result": res}

@mcp.tool()
def change_seats(user_id: str, booking_id: str, new_seat_ids: list[str]) -> dict:
    """เปลี่ยนที่นั่งในการจอง (เฉพาะ Member)"""
    success, res = system.change_seats(user_id, booking_id, new_seat_ids)
    return {"success": success, "result": res}

@mcp.tool()
def write_review(user_id: str, booking_id: str, star: int, comment: str) -> dict:
    """เขียนรีวิวให้หนัง (ต้องดูจบแล้วเท่านั้น / Booking=COMPLETED)"""
    success, res = system.write_review(user_id, booking_id, star, comment)
    return {"success": success, "result": res}

@mcp.tool()
def read_reviews(movie_id: str) -> dict:
    """อ่านรีวิวของหนังเรื่องนั้นๆ"""
    success, res = system.read_reviews(movie_id)
    return {"success": success, "result": res}