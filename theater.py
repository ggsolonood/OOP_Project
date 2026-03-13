from datetime import datetime
from enums import SeatType, TheaterType, SeatStatus, Genre

class Review:
    def __init__(self, star: int, comment: str, user_name: str):
        self.__star = star
        self.__comment = comment
        self.__user_name = user_name
    
    @property
    def star(self): return self.__star
    @property
    def comment(self): return self.__comment
    @property
    def user_name(self): return self.__user_name

class Seat:
    def __init__(self, seat_id: str, number: str, s_type: SeatType):
        self.__id = seat_id
        self.__number = number
        self.__type = s_type

    @property
    def id(self): return self.__id
    @property
    def number(self): return self.__number
    @property
    def type(self): return self.__type
    @property
    def price(self) -> float:
        if self.__type == SeatType.NORMALSEAT: return 100.0
        if self.__type == SeatType.SOFA: return 200.0
        if self.__type == SeatType.HONEYMOONBED: return 350.0
        return 0.0

class ShowtimeSeat(Seat): 
    def __init__(self, seat_id: str, number: str, s_type: SeatType):
        super().__init__(seat_id, number, s_type)
        self.__status = SeatStatus.BOOKED 

    @property
    def status(self): return self.__status
    
    # Method เปลี่ยนสถานะ
    def book(self): self.__status = SeatStatus.BOOKED
    def occupy(self): self.__status = SeatStatus.OCCUPIED

class Theater:
    def __init__(self, theater_id: str, t_type: TheaterType, name: str):
        self.__id = theater_id
        self.__type = t_type
        self.__name = name
        self.__seats = []

    @property
    def id(self): return self.__id
    @property
    def type(self): return self.__type
    @property
    def name(self): return self.__name
    @property
    def seats(self): return self.__seats
    
    @property
    def additional_price(self) -> float:
        if self.__type == TheaterType.IMAX: return 100.0
        if self.__type == TheaterType._4DX: return 150.0
        return 0.0

    def add_seat(self, seat: Seat): self.__seats.append(seat)

class Movie:
    def __init__(self, movie_id: str, name: str, base_price: float, genre: Genre, age_rating: str):
        self.__id = movie_id
        self.__name = name
        self.__base_price = base_price
        self.__genre = genre
        self.__age_rating = age_rating
        self.__showtimes = []
        self.__reviews = []
    
    @property
    def id(self): return self.__id
    @property
    def name(self): return self.__name
    @property
    def base_price(self): return self.__base_price
    @property
    def genre(self): return self.__genre
    @property
    def age_rating(self): return self.__age_rating
    @property
    def showtimes(self): return self.__showtimes
    @property
    def reviews(self): return self.__reviews

    def add_showtime(self, showtime): self.__showtimes.append(showtime)
    def add_review(self, review: Review): self.__reviews.append(review)

class Showtime:
    def __init__(self, showtime_id: str, movie: Movie, theater: Theater, start_time: datetime):
        self.__id = showtime_id
        self.__movie = movie
        self.__theater = theater
        self.__start_time = start_time
        self.__showtime_seats = {} 
        movie.add_showtime(self)

    @property
    def id(self): return self.__id
    @property
    def movie(self): return self.__movie
    @property
    def theater(self): return self.__theater
    @property
    def start_time(self): return self.__start_time
    @property
    def showtime_seats(self): return self.__showtime_seats

class Cineplex:
    def __init__(self, cineplex_id: str, name: str):
        self.__id = cineplex_id
        self.__name = name
        self.__theaters = []
        self.__movies = []
        self.__goods = []
        self.__rewards = []

    @property
    def id(self): return self.__id
    @property
    def name(self): return self.__name
    @property
    def theaters(self): return self.__theaters
    @property
    def movies(self): return self.__movies
    @property
    def goods(self): return self.__goods
    @property
    def rewards(self): return self.__rewards

    def add_theater(self, theater: Theater): self.__theaters.append(theater)
    def add_movie(self, movie: Movie): self.__movies.append(movie)
    def add_goods(self, item): self.__goods.append(item)
    def add_reward(self, reward): self.__rewards.append(reward)