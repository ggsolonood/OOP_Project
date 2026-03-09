import datetime
from datetime import date
from fastapi import FastAPI
from abc import ABC , abstractmethod

app = FastAPI()

class JamorPlinicex :
    def __init__(self):
        self.__member_list = []
        self.__coupon_list = []
        self.__cineplex_list = []
        self.__booking_list = []
    
    def add_cineplex(self,name) :
        cineplex = Cineplex(name)
        self.__cineplex_list.append(cineplex)
        return cineplex

    def register_member(self,account_id,name,birthday:date,member_id,registered_date:date,email,phone_number=None) :
        try :
            for i in self.__member_list :
                if i.get_member_id() == member_id :
                    return "Failed, member existed"
            payment = PaymentGateway(account_id,50)
            check = payment.pay()
            if check == "Account not found" :
                return check
            elif check == True :
                member = SilverMember(name,birthday,member_id,registered_date,email,phone_number)
                self.__member_list.append(member)
                text = f"Success, Name : {name}, birthday : {birthday}, member_id : {member_id}, registered_date : {registered_date}, email : {email}"
                if phone_number is not None :
                    text += f", phone_number : {phone_number}"
                return text
            else :
                return "Failed, Payment Issue"
        except Exception as e :
            return f"Failed, {str(e)}"
    
    def add_discount_coupon(self,coupon_id,name,discount) :
        discount_coupon = DiscountCoupon(coupon_id,name,discount)
        self.__coupon_list.append(discount_coupon)  

    def add_exchange_coupon(self,coupon_id,name,goods:list) :
        exchange_coupon = ExchangeCoupon(coupon_id,name,goods)
        self.__coupon_list.append(exchange_coupon)

    def find_cineplex(self,cineplex_name) :
        for i in self.__cineplex_list :
            if cineplex_name == i.get_cineplex_name() :
                return i
            
    def calculate_total_price(self,member,booking) :
        member_discount = member.get_discount()
        cineplex = self.find_cineplex(booking.get_cineplex_name())
        showtime = booking.get_showtime()
        movie_price = showtime.get_price()
        theater = cineplex.find_theater(booking.get_theater_id())
        theater_price = theater.get_price()
        seat = theater.find_seat(booking.get_seat_no())
        seat_price = seat.get_price()
        return booking.calculate_total(theater_price,movie_price,seat_price,member_discount)

    def change_seat_status(self,booking,status) :
        cineplex = self.find_cineplex(booking.get_cineplex_name())
        theater = cineplex.find_theater(booking.get_theater_id())
        seat = theater.find_seat(booking.get_seat_no())
        if status == "buy" :
            seat.buy()
        elif status == "release" :
            seat.release()

    def add_booking(self,booking_id,member_id,cineplex_name,theater_id,seat_no,movie,showtime) :
        booking = Booking(booking_id,member_id,cineplex_name,theater_id,seat_no,movie,showtime)
        self.__booking_list.append(booking)
        for i in self.__member_list :
            if member_id == i.get_member_id() :
                i.add_booking(booking)
        cineplex = self.find_cineplex(cineplex_name)
        theater = cineplex.find_theater(theater_id)
        seat = theater.find_seat(seat_no)
        seat.reserve()

    def confirm_booking(self,booking_id,user_id,account_id) :
        try :
            member = self.find_member(user_id)
        except :
            return "Member not found"
        try :
            booking = self.find_booking(booking_id)
        except :
            return "Booking not found"
        if booking.get_member_id() == user_id :
            total = self.calculate_total_price(member,booking)
            payment = PaymentGateway(account_id,total)
            check = payment.pay()
            if check == "Account not found" :
                return check
            elif check == True :
                booking.success()
                self.change_seat_status(booking,"buy")
                return f"Success, Total Paid : {total}"
            else :
                return "Failed"
        else :
            return "This booking is not belong to this member."

    def find_member(self,user_id) :
        for i in self.__member_list :
            if user_id == i.get_member_id() :
                return i
        raise ValueError("Member not found.")
    
    def find_booking(self,booking_id) :
        for i in self.__booking_list :
            if booking_id == i.get_booking_id() :
                return i
        raise ValueError("Booking not found.")


class Cineplex :
    def __init__(self,name):
        self.__name = name
        self.__movie_list = []
        self.__theater_list = []
        self.__stock = []

    def add_standard_theater(self,theater_id,seat:list) :
        theater = StandardTheater(theater_id,seat)
        self.__theater_list.append(theater)

    def add_imax_theater(self,theater_id,seat:list) :
        theater = IMAXTheater(theater_id,seat)
        self.__theater_list.append(theater)

    def add_4dx_theater(self,theater_id,seat:list) :
        theater = FourDXTheater(theater_id,seat)
        self.__theater_list.append(theater)

    def add_movie(self,name,duration,genre,age_rating,showtime:list) :
        movie = Movie(name,duration,genre,age_rating,showtime)
        self.__movie_list.append(movie)

    def add_popcorn(self,name, values:int, price,flavor) :
        popcorn = Popcorn(name, values, price,flavor)
        self.__stock.append(popcorn)

    def add_drinks(self,name, values:int, price,flavor) :
        drinks = Drinks(name, values, price,flavor)
        self.__stock.append(drinks)

    def add_snack(self,name, values:int, price) :
        snack = Snack(name, values, price)
        self.__stock.append(snack)

    def check_stock(self) :
        return self.__stock
    
    def get_cineplex_name(self) :
        return self.__name
    
    def find_theater(self,theater_id) :
        for i in self.__theater_list :
            if theater_id == i.get_theater_id() :
                return i

    def find_movie(self,movie_name) :
        for i in self.__movie_list :
            if movie_name == i.get_movie_name() :
                return i

class Member(ABC) :
    def __init__(self,name,birthday,member_id,registered_date,email=None,phone_number=None):
        self._name = name
        self._member_id = member_id
        self._birthday = birthday
        self._registered_date = registered_date
        self._email = email
        self._phone_number = phone_number
        self._coupon_list = []
        self._ticket_list = []
        self._booking_list = []
        self._transaction_list = []
        self._point = 0
        self._total_spend = 0
        self._status = "Active"
        self._discount = 20

    @abstractmethod
    def get_discount(self) :
        pass
    
    def add_booking(self,booking) :
        self._booking_list.append(booking)

    def get_member_id(self) :
        return self._member_id
    
class SilverMember(Member) :
    def __init__(self, name, birthday, member_id, registered_date, email=None, phone_number=None):
        super().__init__(name, birthday, member_id, registered_date, email, phone_number)

    def get_discount(self) :
        return self._discount
    
class GoldMember(Member) :
    def __init__(self, name, birthday, member_id, registered_date, email=None, phone_number=None):
        super().__init__(name, birthday, member_id, registered_date, email, phone_number)
        self._discount = 50
    
    def get_discount(self) :
        return self._discount
    
class PlatinumMember(Member) :
    def __init__(self, name, birthday, member_id, registered_date, email=None, phone_number=None):
        super().__init__(name, birthday, member_id, registered_date, email, phone_number)
        self._discount = 100

    def get_discount(self) :
        return self._discount
    
class Coupon(ABC) :
    def __init__(self,coupon_id,name):
        self._coupon_id = coupon_id
        self._name = name
        self._type = None

    @abstractmethod
    def get_type(self) :
        pass

class DiscountCoupon(Coupon) :
    def __init__(self, coupon_id, name,discount):
        super().__init__(coupon_id, name)
        self._discount = discount
        self._type = "DiscountCoupon"

    def get_discount(self) :
        return self._discount
    
    def get_type(self) :
        return self._type
    
class ExchangeCoupon(Coupon) :
    def __init__(self, coupon_id, name,goods:list):
        super().__init__(coupon_id, name)
        self._good_list = goods
        self._type = "ExchangeCoupon"

    def get_exchange(self) :
        return self._good_list
    
    def get_type(self) :
        return self._type
    
class Theater(ABC) :
    def __init__(self,theater_id,seat:list,price) :
        self._theater_id = theater_id
        self._seat_list = seat
        self._price = price

    def get_seat_map(self) :
        return self._seat_list
    
    @abstractmethod
    def get_price(self) :
        pass
    
    def get_theater_id(self) :
        return self._theater_id
    
    def find_seat(self,seat_no) :
        for i in self._seat_list :
            if seat_no == i.get_seat_no() :
                return i

class StandardTheater(Theater) :
    def __init__(self, theater_id, seat):
        super().__init__(theater_id, seat,100)
    
    def get_price(self) :
        return self._price

class IMAXTheater(Theater) :
    def __init__(self, theater_id, seat):
        super().__init__(theater_id, seat,150)
    
    def get_price(self) :
        return self._price

class FourDXTheater(Theater) :
    def __init__(self, theater_id, seat):
        super().__init__(theater_id, seat,200)
    
    def get_price(self) :
        return self._price

class Seat(ABC) :
    def __init__(self,seat_no) :
        self._seat_no = seat_no
        self._price = 20
        self._status = "Available"

    @abstractmethod
    def get_price(self) :
        pass
    
    def reserve(self) :
        self._status = "Reserved"

    def release(self) :
        self._status = "Available"

    def buy(self) :
        self._status = "Occupied"

    def get_seat_no(self) :
        return self._seat_no

class NormalSeat(Seat) :
    def __init__(self, seat_no):
        super().__init__(seat_no)
    
    def get_price(self) :
        return self._price

class SofaSeat(Seat) :
    def __init__(self, seat_no):
        super().__init__(seat_no)
        self._price = 50

    def get_price(self) :
        return self._price

class HoneyMoonBed(Seat) :
    def __init__(self, seat_no):
        super().__init__(seat_no)
        self._price = 120

    def get_price(self) :
        return self._price

class Movie :
    def __init__(self,name,duration,genre,age_rating,showtime:list):
        self.__movie_name = name
        self.__duration = duration
        self.__genre = genre
        self.__age_rating = age_rating
        self.__showtime_list = showtime

    def get_movie_name(self) :
        return self.__movie_name
    
    def find_showtime(self,showtime) :
        for i in self.__showtime_list :
            if showtime == i :
                return i

class Showtime :
    def __init__(self,name,start_time,end_time,subtitle,price):
        self.__movie_name = name
        self.__start_time = start_time
        self.__end_time = end_time
        self.__subtitle = subtitle
        self.__price = price
        self.__status = "Scheduled"

    def is_bookable(self) :
        if datetime.datetime.time() < self.__start_time and self.__status == "Open" :
            return True
        return False
    
    def open_booking(self) :
        self.__status = "Open"

    def get_price(self) :
        return self.__price
    
    def get_start_time(self) :
        return self.__start_time
        
class Goods(ABC) :
    def __init__(self,name,values:int,price):
        self._name = name
        self._values = values
        self._price = price

    @abstractmethod
    def get_price(self) :
        pass
    
class Popcorn(Goods) :
    def __init__(self, name, values:int, price,flavor):
        super().__init__(name, values, price)
        self._flavor = flavor

    def get_price(self) :
        return self._price
    
class Drinks(Goods) :
    def __init__(self, name, values:int, price,flavor):
        super().__init__(name, values, price)
        self._flavor = flavor

    def get_price(self) :
        return self._price
    
class Snack(Goods) :
    def __init__(self, name, values:int, price):
        super().__init__(name, values, price)

    def get_price(self) :
        return self._price
    
class Booking :
    def __init__(self,booking_id,member_id,cineplex_name,theater_id,seat_no,movie,showtime):
        self.__booking_id = booking_id
        self.__member_id = member_id
        self.__seat_no = seat_no
        self.__movie_name = movie
        self.__showtime = showtime
        self.__status = "Pending"
        self.__total_price = None
        self.__cineplex_name = cineplex_name
        self.__theater_id = theater_id

    def get_booking_id(self) :
        return self.__booking_id
    
    def get_member_id(self) :
        return self.__member_id
    
    def get_cineplex_name(self) :
        return self.__cineplex_name
    
    def get_theater_id(self) :
        return self.__theater_id
    
    def get_seat_no(self) :
        return self.__seat_no
    
    def get_movie_name(self) :
        return self.__movie_name
    
    def get_showtime(self) :
        return self.__showtime

    def calculate_total(self,theater_price,movie_price,seat_price,member_discount) :
        total = theater_price + movie_price + seat_price - member_discount
        self.__total_price = total
        return total
    
    def success(self) :
        self.__status = "Paid"
                
class PaymentGateway :
    def __init__(self,account_id,price):
        self.__price = price
        self.__account_id = account_id

    def pay(self) :
        return krungjean.payment(self.__account_id,self.__price)
    
class Bank :
    def __init__(self,name):
        self.__name = name
        self.__account_list = []
    
    def create_account(self,name,id,balance) :
        account = Account(name,id,balance)
        self.__account_list.append(account)

    def check_account(self,account_id) :
        for i in self.__account_list :
            if i.get_id() == account_id :
                return i
    
    def payment(self,account_id,price) :
        account = self.check_account(account_id)
        if account != None :
            return account.deduct(price)
        else :
            return "Account not found"

class Account :
    def __init__(self,name,id,balance) :
        self.__name = name
        self.__balance = balance
        self.__id = id

    def deduct(self,amount) :
        if self.__balance >= amount :
            self.__balance -= amount
            return True
        return False
    
    def get_id(self) :
        return self.__id
    

testjamorplinicex = JamorPlinicex()
krungjean = Bank("krungjean")
krungjean.create_account("Potapo","1112",2500)

from fastapi import Query

@app.post("/register-member")
def register_member_api(
    account_id: str = Query(...),
    name: str = Query(...),
    birthday: date = Query(...,example="YYYY-MM-DD"),
    member_id: str = Query(...),
    registered_date: date = Query(...,example="YYYY-MM-DD"),
    email: str = Query(...),
    phone_number: str | None = Query(None,example="Optional")
):

    result = testjamorplinicex.register_member(
        account_id,
        name,
        birthday,
        member_id,
        registered_date,
        email,
        phone_number
    )
    return result