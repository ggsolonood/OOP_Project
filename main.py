from typing import List, Optional
from fastmcp import FastMCP

# ==========================================
# 1. Classes Structure (โครงสร้างคลาสหลัก เหมือนเดิม 100%)
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
# 2. System (Controller) (ลอจิกเดิมของคุณ Ken ครับ)
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
# 3. MCP Tools (ส่วนที่แปลงจาก API Routes)
# ==========================================
# สร้าง MCP Server แทน FastAPI
mcp = FastMCP("JamorCineplex")
system = JamorCineplex()

@mcp.tool()
def create_cineplex(cineplex_id: int, name: str) -> str:
    """สร้างสาขาโรงภาพยนตร์ใหม่ (Cineplex)"""
    success, msg = system.process_create_cineplex(cineplex_id, name)
    return f"Success: {msg}" if success else f"Error: {msg}"

@mcp.tool()
def create_movie(cineplex_id: int, movie_id: int, name: str, duration: int, genre: str, age_rating: str) -> str:
    """เพิ่มภาพยนตร์เรื่องใหม่เข้าไปในระบบของสาขา"""
    success, msg = system.process_create_movie(cineplex_id, movie_id, name, duration, genre, age_rating)
    return f"Success: {msg}" if success else f"Error: {msg}"

@mcp.tool()
def create_theater(cineplex_id: int, theater_id: str, type_theater: str) -> str:
    """สร้างโรงฉายภาพยนตร์ย่อยภายในสาขา"""
    success, msg = system.process_create_theater(cineplex_id, theater_id, type_theater)
    return f"Success: {msg}" if success else f"Error: {msg}"

@mcp.tool()
def create_seat(cineplex_id: int, theater_id: str, seat_id: str, seat_number: str, type_seat: str) -> str:
    """เพิ่มที่นั่งในโรงฉายภาพยนตร์"""
    success, msg = system.process_create_seat(cineplex_id, theater_id, seat_id, seat_number, type_seat)
    return f"Success: {msg}" if success else f"Error: {msg}"

@mcp.tool()
def create_showtime(cineplex_id: int, showtime_id: str, movie_id: int, theater_id: str, status: str, subtitle: str, start_time: str, end_time: str, base_price: float) -> str:
    """สร้างรอบฉายภาพยนตร์"""
    success, msg = system.process_create_showtime(cineplex_id, showtime_id, movie_id, theater_id, status, subtitle, start_time, end_time, base_price)
    return f"Success: {msg}" if success else f"Error: {msg}"

@mcp.tool()
def create_coupon(coupon_type: str, coupon_id: str, name: str, discount: float = 0.0, goods_list: List[str] = []) -> str:
    """สร้างคูปองส่วนลด (discount) หรือ คูปองแลกของ (exchange)"""
    success, msg = system.process_create_coupon(coupon_type, coupon_id, name, discount, goods_list)
    return f"Success: {msg}" if success else f"Error: {msg}"

if __name__ == "__main__":
    # รันเซิร์ฟเวอร์ MCP (ตั้งค่าให้คุยผ่าน Stdio อัตโนมัติ)
    mcp.run()