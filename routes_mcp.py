from fastmcp import FastMCP
from mock_data import system

mcp = FastMCP("JamorCineplex")

@mcp.tool()
def search_showtime_details(movie_name: str, cineplex_name: str) -> dict:
    """ช่วย AI ค้นหา showtime_id ของหนังที่ฉายในสาขานั้นๆ จากชื่อ"""
    success, res = system.search_showtime_details(movie_name, cineplex_name)
    return {"success": success, "result": res}

@mcp.tool()
def get_all_movies() -> list:
    """แสดงรายการหนังทั้งหมดพร้อม Genre/Age Rating"""
    return system.get_all_movies()

@mcp.tool()
def get_showtimes_by_movie(movie_id: str) -> dict:
    """แสดงรอบฉาย (สาขา, โรง, ประเภทโรง, เวลา)"""
    success, res = system.get_showtimes_by_movie(movie_id)
    return {"success": success, "result": res}

@mcp.tool()
def get_available_seats(showtime_id: str) -> dict:
    """แสดงที่นั่งว่าง พร้อมราคาสุทธิรวมทุกอย่าง"""
    success, res = system.get_available_seats(showtime_id)
    return {"success": success, "result": res}

@mcp.tool()
def book_ticket(user_id: str, showtime_id: str, seat_ids: list[str], coupon_id: str = None) -> dict:
    """จองตั๋ว แสดงผลสถานที่และที่นั่งที่จอง"""
    success, res = system.book_ticket(user_id, showtime_id, seat_ids, coupon_id)
    return {"success": success, "result": res}

@mcp.tool()
def confirm_booking(booking_id: str, account_number: str) -> dict:
    """ยืนยันการจองและตัดเงิน โดยใช้ เลขบัญชี 5 หลัก (account_number) พร้อมสร้างตั๋วที่นั่ง"""
    success, res = system.confirm_booking(booking_id, account_number)
    return {"success": success, "result": res}

@mcp.tool()
def cancel_booking(booking_id: str) -> dict:
    """ยกเลิกการจอง คืนเงิน"""
    success, res = system.cancel_booking(booking_id)
    return {"success": success, "result": res}

@mcp.tool()
def get_goods_by_cineplex(cineplex_name: str) -> dict:
    """แสดงรายการสินค้าขนม/เครื่องดื่มในสาขานั้นๆ โดยค้นหาผ่านชื่อสาขา (cineplex_name) เช่น 'Siam Paragon'"""
    success, res = system.get_goods_by_cineplex(cineplex_name)
    return {"success": success, "result": res}

@mcp.tool()
def order_goods(user_id: str, cineplex_name: str, items_dict: dict, account_number: str, coupon_id: str = None) -> dict:
    """สั่งซื้อขนม/น้ำ โดยใช้ชื่อสาขาและเลขบัญชีธนาคาร 5 หลัก"""
    success, res = system.order_goods(user_id, cineplex_name, items_dict, account_number, coupon_id)
    return {"success": success, "result": res}

@mcp.tool()
def cancel_order(order_id: str, cineplex_name: str) -> dict:
    """ยกเลิกสั่งซื้อและคืนเงิน"""
    success, res = system.cancel_order(order_id, cineplex_name)
    return {"success": success, "result": res}

@mcp.tool()
def upgrade_member(user_id: str, account_number: str) -> dict:
    """สมัคร/ต่ออายุสมาชิก อัปเกรดอัตโนมัติตามจำนวนครั้ง (ใช้เลขบัญชี 5 หลักจ่ายเงิน)"""
    success, res = system.upgrade_member(user_id, account_number)
    return {"success": success, "result": res}

@mcp.tool()
def view_history(user_id: str) -> dict:
    """ดูประวัติการจอง (Guest ดูได้แค่อันที่ยังไม่เสร็จ)"""
    success, res = system.view_history(user_id)
    return {"success": success, "result": res}

@mcp.tool()
def show_points_and_rewards(user_id: str) -> dict:
    """ดูพ้อยท์และรางวัล (บอกพ้อยท์ที่ต้องใช้)"""
    success, res = system.show_points_and_rewards(user_id)
    return {"success": success, "result": res}

@mcp.tool()
def redeem_reward(user_id: str, reward_id: str) -> dict:
    """แลกของรางวัล"""
    success, res = system.redeem_reward(user_id, reward_id)
    return {"success": success, "result": res}

@mcp.tool()
def collect_monthly_coupon(user_id: str, coupon_id: str) -> dict:
    """เก็บคูปอง (Member ได้ดีกว่าตามขั้น)"""
    success, res = system.collect_monthly_coupon(user_id, coupon_id)
    return {"success": success, "result": res}

@mcp.tool()
def change_seats(user_id: str, booking_id: str, new_seat_ids: list[str]) -> dict:
    """เปลี่ยนที่นั่ง แจ้งส่วนต่างการคืนเงิน"""
    success, res = system.change_seats(user_id, booking_id, new_seat_ids)
    return {"success": success, "result": res}

@mcp.tool()
def write_review(user_id: str, booking_id: str, star: int, comment: str) -> dict:
    """เขียนรีวิว (ต้องดูจบแล้วเท่านั้น)"""
    success, res = system.write_review(user_id, booking_id, star, comment)
    return {"success": success, "result": res}

@mcp.tool()
def read_reviews(movie_id: str) -> dict:
    """อ่านรีวิวใครเขียน กี่ดาว"""
    success, res = system.read_reviews(movie_id)
    return {"success": success, "result": res}