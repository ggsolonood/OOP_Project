#for import
from abc import ABC,abstractmethod
from enum import Enum

#for class diagram
class JamorCineplex:
    def __init__(self):
        self.__cineplex_list = []
        self.__user_list = []
        self.__booking_list = []
        self.__coupon_list = []
    #return class cineplex
    def search_cineplex_by_id(self,cineplex_id):
        for i in self.__cineplex_list:
            if i.id == cineplex_id:
                return i
        return False
    #return class user
    def search_user_by_id(self,user_id):
        for i in self.__user_list:
            if i.id == user_id:
                return i
        return False
class Cineplex:
    def __init__(self,cineplex_id,name):
        self.__cineplex_id = cineplex_id
        self.__name = name
        self.__movies_list = []
        self.__theaters_list = []
        self.__showtime_list = []
        self.__goods_list = []
    @property
    def id(self):
        return self.__cineplex_id
    #return class movie
    def search_movie_by_id(self,movie_id):
        for i in self.__movies_list:
            if i.id == movie_id:
                return i
        return False
    #return class theater
    def search_theater_by_id(self,theater_id):
        for i in self.__theaters_list:
            if i.id == theater_id:
                return i
        return False
    #return class showtime
    def search_showtime_by_id(self,showtime_id):
        for i in self.search_showtime_by_id:
            if i.id == showtime_id:
                return i
        return False
    #return class goods
    def search_goods_by_id(self,goods_id):
        for i in self.__goods_list:
            if i.id == goods_id:
                return i
        return False
class Showtime:
    def __init__(self,showtime,movie,theater,status,subtitle,start_time,end_time,base_price):
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
    def id(self):
        return self.__id
    def calculate_price(self):
        pass
    def get_info(self):
        return print("Movie Name : ",self.__movie,"At Theater :",self.__theater,"Start at :",self.__start_time,"End at :",self.__end_time)
    def is_seat_available(self,seat):
        for i in self.__showtime_seat:
            if i == seat:
                return False
        return True
class Movie:
    def __init__(self,id,name,duration,genre,aga_rating):
        self.__movie_id = id
        self.__movie_name = name
        self.__duration = duration
        self.__genre = genre
        self.__age_rating = aga_rating
    @property
    def id(self):
        return self.__movie_id
class Theater:
    def __init__(self,theater_id,type_theater):
        self.__theater_id = theater_id
        self.__seats_list = []
        self.__type_theater = type_theater
    @property
    def id(self):
        return self.__theater_id
    def search_seats_list_avalible(self,seats):
        for i in self.__seats_list:
            for b in seats:
                if b == i:
                    return False
        return True
class Seat:
    def __init__(self,seat_id,seat_number,type_seat):
        self.__seat_id = seat_id
        self.__seat_number = seat_number
        self.__type_seat = type_seat
    @property
    def id(self):
        return self.__seat_id
class ShowtimeSeat(Seat):
    def __init__(self,seat_id,seat_number,type_seat,status):
        super().__init__(seat_id,seat_number,type_seat)
        self.__status = status
    @property
    def status(self):
        return self.__status
class Goods:
    def __init__(self,values,name,price,type_goods):
        self.__values = values
        self.__name = name
        self.__price = price
        self.__type_goods = type_goods
    
class Order:
    def __init__(self,goods,user_id):
        self.__goods = goods
        self.__user_id = user_id
        self.__totle_cost = None
class Booking:
    def __init__(self,booking_id,user,showtime,timestamp,status):
        self.__booking_id = booking_id
        self.__user = user
        self.__showtime = showtime
        self.__ticket = None
        self.__timestamp = timestamp
        self.__showtime_seat = []
        self.__status = status
    @property
    def id(self):
        return self.__booking_id
class Ticket:
    def __init__(self,booking,cineplex,user,movie,theater,showtime,seat_list):
        self.__booking = booking
        self.__cineplex = cineplex
        self.__user = user
        self.__movie = movie
        self.__theater = theater
        self.__showtime = showtime
        self.__seat_list = seat_list
class Bank:
    def __init__(self,name):
        self.__name = name
        self.__account_list = []
class Account:
    def __init__(self,name,balance,id):
        self.__id = id
        self.__name = name
        self.__balance = balance
    @property
    def id(self):
        return self.__id
class User:
    def __init__(self,id,name,email,phone_number,birthday,password):
        self.__id = id
        self.__name = name
        self.__email = email
        self.__phone_number = phone_number
        self.__birthday = birthday
        self.__password = password
        self.__point = 0
        self.__coupon_list = []
        self.__ticket_list = []
        self.__booking_list = []
        self.__totle_spending = 0
        self.__type_user = "guest"
    @property
    def id(self):
        return self.__id
class coupon:
    def __init__(self,id,name):
        self.__coupon_id = id
        self.__name = name
class DiscountCoupon(coupon):
    def __init__(self, id, name, discount):
        super().__init__(id, name)
        self.__discount = discount
class ExchangeCoupon(coupon):
    def __init__(self, id, name,goods):
        super().__init__(id, name)
        self.__list_goods = goods
class OrderStatus(Enum):
    COMPLETED = "Conpleted"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"
class Member(Enum):
    SIVER = "Siver"
    GOLD = "Gold"
    PATINUM = "Patinum"
    GUEST = "Guest"
class BookingStatus(Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
class Goods(Enum):
    Popcorn = "Popcorn"
    DRINKS = "Drinks"
    SNACK = "Snack"
class SeatStatus(Enum):
    NORMALSEAT = "Normalseat"
    SOFA = "Sofa"
    HONEYMOONBED = "Honeymoonbed"
class Theater(Enum):
    STANDARD = "Standard"
    IMAX = "IMAX"
    _4DX = "4DX"
#test script
# --------------------------------------------

#----------------------------------------------

#api