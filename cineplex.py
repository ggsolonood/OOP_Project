from typing import List, Optional
from datetime import datetime , timedelta
from enums import BookingStatus, MemberTier, OrderStatus
from goods import Goods
from theater import Movie, Theater, Seat, Showtime, ShowtimeSeat , Review
from payment import Bank, Order
from user import Booking, Ticket, User, Reward


# ── Coupon ────────────────────────────────────────────────────────────────

class Coupon:
    def __init__(self, id: str, name: str, last_date: datetime = None):
        self.__coupon_id = id
        self.__name      = name
        self.__last_date = last_date
        self._is_used    = False

    @property
    def id(self) -> str:
        return self.__coupon_id

    @property
    def coupon_name(self) -> str:
        return self.__name

    @property
    def last_date(self) -> Optional[datetime]:
        return self.__last_date

    def get_coupon_id(self) -> str:
        return self.__coupon_id

    def get_discount(self) -> float:
        return 0

    def is_expired(self) -> bool:
        if self.__last_date is None:
            return False
        return datetime.now() > self.__last_date

    def update_status(self, status: str):
        self._is_used = (status != "Available")
        return "success"


class DiscountCoupon(Coupon):
    def __init__(self, id: str, name: str, discount: float,
                 last_date: datetime = None):
        super().__init__(id, name, last_date)
        self.__discount = discount

    def get_discount(self) -> float:
        return self.__discount


class ExchangeCoupon(Coupon):
    def __init__(self, id: str, name: str, goods: list,
                 last_date: datetime = None):
        super().__init__(id, name, last_date)
        self.__list_goods = goods

    def get_goods_list(self) -> list:
        return self.__list_goods


# ── Cineplex ──────────────────────────────────────────────────────────────

class Cineplex:
    def __init__(self, cineplex_id: str, name: str):
        self.__cineplex_id    = cineplex_id
        self.__name           = name
        self.__movies_list:   List[Movie]    = []
        self.__theaters_list: List[Theater]  = []
        self.__showtime_list: List[Showtime] = []
        self.__goods_list:    List[Goods]    = []

    @property
    def id(self) -> str:
        return self.__cineplex_id

    @property
    def showtime_list(self) -> List[Showtime]:
        return self.__showtime_list

    @property
    def movies_list(self) -> List[Movie]:
        return self.__movies_list

    @property
    def goods_list(self):
        return self.__goods_list

    def get_cineplex_name(self) -> str:
        return self.__name

    def search_movie_by_id(self, movie_id: str) -> Optional[Movie]:
        for i in self.__movies_list:
            if i.id == movie_id:
                return i
        return None

    def search_theater_by_id(self, theater_id: str) -> Optional[Theater]:
        for i in self.__theaters_list:
            if i.id == theater_id:
                return i
        return None

    def search_showtime_by_id(self, showtime_id: str) -> Optional[Showtime]:
        for i in self.__showtime_list:
            if i.id == showtime_id:
                return i
        return None

    def add_movie(self, movie: Movie):
        self.__movies_list.append(movie)

    def add_theater(self, theater: Theater):
        self.__theaters_list.append(theater)

    def add_showtime(self, showtime: Showtime):
        self.__showtime_list.append(showtime)

    def add_goods(self, name: str, values: int, price: float,
                  goods_type: str, flavor: str = None):
        self.__goods_list.append(Goods.create(name, values, price, goods_type, flavor))

    def search_goods_stock(self, goods_name: str, amount_needed: int = 0) -> Optional[Goods]:
        for item in self.__goods_list:
            if item.get_name() == goods_name:
                if amount_needed == 0 or item.check_values(amount_needed):
                    return item
        return None


# ── JamorCineplex ─────────────────────────────────────────────────────────

class JamorCineplex:
    def __init__(self, bank: Optional[Bank] = None):
        self.__bank           = bank   # Bank instance (ถ้า None จะใช้ pay_direct)
        self.__cineplex_list: List[Cineplex] = []
        self.__user_list:     List[User]     = []
        self.__booking_list:  List[Booking]  = []
        self.__order_list:    List[Order]    = []
        self.__coupon_list:   List[Coupon]   = []
        self.__ticket_list:   List[Ticket]   = []
        self.__reward_list:   List[Reward]   = []

        # Counters for Auto-Generate ID
        self.__cineplex_counter = 1
        self.__movie_counter    = 1
        self.__theater_counter  = 1
        self.__seat_counter     = 1
        self.__showtime_counter = 1
        self.__coupon_counter   = 1
        self.__order_counter    = 1
        self.__reward_counter   = 1
        self.__user_counter     = 1
        self.__booking_id       = 0

    @property
    def bank(self) -> Optional[Bank]:
        return self.__bank

    @property
    def cineplex_list(self) -> List[Cineplex]:
        return self.__cineplex_list

    @property
    def booking_id(self):
        return self.__booking_id

    def search_cineplex_by_id(self, cineplex_id: str) -> Optional[Cineplex]:
        for i in self.__cineplex_list:
            if i.id == cineplex_id:
                return i
        return None

    def search_user_by_id(self, user_id: str) -> Optional[User]:
        for i in self.__user_list:
            if i.id == user_id:
                return i
        return None

    def search_order_by_id(self, order_id: str) -> Optional[Order]:
        for o in self.__order_list:
            if o.get_order_id() == order_id:
                return o
        return None

    def search_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        for b in self.__booking_list:
            if b.id == booking_id:
                return b
        return None

    def add_cineplex(self, cineplex: Cineplex):
        self.__cineplex_list.append(cineplex)

    def add_user(self, user: User):
        self.__user_list.append(user)

    def get_all_users(self) -> List[User]:
        return self.__user_list

    def register_member(self, name: str, birthday: str, member_id: str,
                        registered_date: str, email: str = None,
                        phone_number: str = None,
                        tier: MemberTier = MemberTier.SILVER):
        user = User(member_id, name, email or "", phone_number or "", birthday, "")
        user.set_tier(tier)
        self.__user_list.append(user)

    def process_register_guest(self, name: str, email: str = "") -> tuple:
        """
        สร้าง User ใหม่แบบ Guest (ยังไม่มี password)
        ต้องการแค่ name ส่วน email ถ้ามีก็ใส่ได้
        """
        # ตรวจ email ซ้ำ (ถ้ามี email)
        if email:
            for u in self.__user_list:
                if u.email and u.email.lower() == email.strip().lower():
                    return False, "Email already in use."

        user_id = f"USR-{self.__user_counter:04d}"
        self.__user_counter += 1
        new_user = User(user_id, name.strip(), email.strip() if email else "")
        # tier = GUEST โดย default อยู่แล้ว
        self.__user_list.append(new_user)
        return True, {
            "user_id": user_id,
            "name":    new_user.name,
            "email":   new_user.email,
            "tier":    new_user.tier.value,
            "message": "Guest user created. Use /register to become a member.",
        }

    # ── admin process ──

    def process_create_cineplex(self, name: str):
        # ห้ามชื่อซ้ำ (case-insensitive)
        for c in self.__cineplex_list:
            if c.get_cineplex_name().lower() == name.strip().lower():
                return False, f"Cineplex name '{name}' already exists."
        cineplex_id = f"CPX-{self.__cineplex_counter:04d}"
        self.__cineplex_counter += 1
        self.__cineplex_list.append(Cineplex(cineplex_id, name))
        return True, {"message": "Cineplex created successfully.", "cineplex_id": cineplex_id}

    def process_create_movie(self, cineplex_id, name, duration, genre, age_rating):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex:
            return False, "Cineplex not found."
        # ห้ามชื่อหนังซ้ำใน cineplex เดียวกัน
        for m in cineplex.movies_list:
            if m.name.lower() == name.strip().lower():
                return False, f"Movie '{name}' already exists in this cineplex."
        movie_id = f"MOV-{self.__movie_counter:04d}"
        self.__movie_counter += 1
        cineplex.add_movie(Movie(movie_id, name, duration, genre, age_rating))
        return True, {"message": "Movie created successfully.", "movie_id": movie_id}

    def process_create_theater(self, cineplex_id: str, type_theater: str):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex:
            return False, "Cineplex not found."
        # theater_id ใช้ counter ของ cineplex นั้นๆ → ต่างกัน cineplex ซ้ำกันได้
        theater_id = f"THT-{self.__theater_counter:04d}"
        self.__theater_counter += 1
        try:
            cineplex.add_theater(Theater.create(theater_id, type_theater))
        except ValueError as e:
            return False, str(e)
        return True, {"message": "Theater created successfully.", "theater_id": theater_id}

    def process_create_seat(self, cineplex_id: str, theater_id: str,
                            seat_number: str, type_seat: str):
        """สร้าง seat เดี่ยว (ใช้ภายใน / backward-compat)"""
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex:
            return False, "Cineplex not found."
        theater = cineplex.search_theater_by_id(theater_id)
        if not theater:
            return False, "Theater not found."
        if theater.search_seat_by_no(seat_number):
            return False, f"Seat number '{seat_number}' already exists in this theater."
        seat_id = f"ST-{self.__seat_counter:04d}"
        self.__seat_counter += 1
        try:
            from enums import SeatType
            theater.add_seat(Seat(seat_id, seat_number, SeatType.from_str(type_seat)))
        except ValueError as e:
            return False, str(e)
        return True, {"message": "Seat created successfully.", "seat_id": seat_id}

    def process_create_seats_bulk(self, cineplex_id: str, theater_id: str,
                                  seats: list):
        """
        สร้าง seat หลายที่นั่งพร้อมกัน
        seats: list of {"seat_number": str, "type_seat": str}
        คืน: (True, {created:[...], failed:[...]}) หรือ (False, error_str)
        """
        from enums import SeatType
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex:
            return False, "Cineplex not found."
        theater = cineplex.search_theater_by_id(theater_id)
        if not theater:
            return False, "Theater not found."

        created = []
        failed  = []
        for item in seats:
            seat_number = item.get("seat_number", "")
            type_seat   = item.get("type_seat", "")
            if theater.search_seat_by_no(seat_number):
                failed.append({"seat_number": seat_number, "reason": "Already exists"})
                continue
            try:
                seat_type = SeatType.from_str(type_seat)
            except ValueError as e:
                failed.append({"seat_number": seat_number, "reason": str(e)})
                continue
            seat_id = f"ST-{self.__seat_counter:04d}"
            self.__seat_counter += 1
            theater.add_seat(Seat(seat_id, seat_number, seat_type))
            created.append({"seat_id": seat_id, "seat_number": seat_number, "type_seat": type_seat})

        return True, {"created": created, "failed": failed}

    def process_create_showtime(self, cineplex_id, movie_id, theater_id, status,
                             subtitle, start_time, base_price,
                             duration_minutes=None, end_time=None):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex:
            return False, "Cineplex not found."
        movie = cineplex.search_movie_by_id(movie_id)
        if not movie:
            return False, "Movie not found."
        theater = cineplex.search_theater_by_id(theater_id)
        if not theater:
            return False, "Theater not found."

        try:
            dt_start = datetime.strptime(start_time, Showtime.DT_FORMAT)
        except ValueError:
            return False, f"Invalid start_time format. Use '{Showtime.DT_FORMAT}'"

        if end_time:
            try:
                dt_end = datetime.strptime(end_time, Showtime.DT_FORMAT)
            except ValueError:
                return False, f"Invalid end_time format. Use '{Showtime.DT_FORMAT}'"
            if dt_end <= dt_start:
                return False, "end_time must be after start_time."
        elif duration_minutes is not None:
            if not isinstance(duration_minutes, (int, float)) or duration_minutes <= 0:
                return False, "duration_minutes must be a positive number."
            dt_end = dt_start + timedelta(minutes=duration_minutes)
        else:
            return False, "Must provide either 'duration_minutes' or 'end_time'."

        # ✅ has_conflict ตรวจเฉพาะ theater นั้น ๆ — คนละ theater ไม่กระทบกัน
        if theater.has_conflict(dt_start, dt_end):
            conflict = next(
                st for st in theater.showtime_list
                if dt_start < st.end_time and dt_end > st.start_time
            )
            return False, (
                f"Time conflict in theater '{theater_id}': "
                f"showtime '{conflict.id}' "
                f"({conflict.start_time.strftime(Showtime.DT_FORMAT)}"
                f" – {conflict.end_time.strftime(Showtime.DT_FORMAT)})"
                f" overlaps with the requested slot "
                f"({dt_start.strftime(Showtime.DT_FORMAT)}"
                f" – {dt_end.strftime(Showtime.DT_FORMAT)})."
            )

        showtime_id  = f"STIME-{self.__showtime_counter:04d}"
        self.__showtime_counter += 1

        new_showtime = Showtime(
            showtime_id, movie, theater, status, subtitle,
            dt_start, base_price,
            end_time=dt_end,          # ✅ ส่ง end_time จริงไปเก็บ
        )
        cineplex.add_showtime(new_showtime)
        theater.add_showtime(new_showtime)   # ✅ ต้องมีทั้งสองบรรทัด!
        return True, {"message": "Showtime created successfully.", "showtime_id": showtime_id}

    def process_create_coupon(self, coupon_type, name, discount=0.0,
                              goods_list=None, last_date: str = None):
        dt_last = None
        if last_date:
            try:
                dt_last = datetime.strptime(last_date, "%Y-%m-%d %H:%M")
            except ValueError:
                return False, "Invalid last_date format. Use 'YYYY-MM-DD HH:MM'"

        coupon_id = f"CPN-{self.__coupon_counter:04d}"
        self.__coupon_counter += 1

        if coupon_type.lower() == "discount":
            new_coupon = DiscountCoupon(coupon_id, name, discount, dt_last)
        elif coupon_type.lower() == "exchange":
            new_coupon = ExchangeCoupon(coupon_id, name, goods_list or [], dt_last)
        else:
            return False, "Invalid coupon_type. Use 'discount' or 'exchange'."

        self.__coupon_list.append(new_coupon)
        return True, {"message": "Coupon created successfully.", "coupon_id": coupon_id}

    # ── reward process ──

    def search_reward_by_id(self, reward_id: str) -> Optional[Reward]:
        for r in self.__reward_list:
            if r.id == reward_id:
                return r
        return None

    def process_create_reward(self, name: str, point_cost: int, stock: int):
        reward_id = f"RWD-{self.__reward_counter:04d}"
        self.__reward_counter += 1
        new_reward = Reward(reward_id, name, point_cost, stock)
        self.__reward_list.append(new_reward)
        return True, {"message": "Reward created successfully.", "reward_id": reward_id}

    def process_get_all_rewards(self):
        return [
            {"reward_id": r.id, "name": r.name, "point_cost": r.point_cost, "stock": r.stock}
            for r in self.__reward_list
        ]

    def process_get_user_coupons(self, user_id: str):
        """
        ดูคูปองทั้งหมดในระบบ (global coupon pool)
        คืน (success, msg, list)
        """
        user = self.search_user_by_id(user_id)
        if not user:
            return False, "User not found.", None

        result = []
        for c in self.__coupon_list:
            result.append({
                "coupon_id":   c.get_coupon_id(),
                "name":        c.coupon_name,
                "type":        "discount" if isinstance(c, DiscountCoupon) else
                               "exchange" if isinstance(c, ExchangeCoupon) else "base",
                "discount":    c.get_discount(),
                "is_used":     c._is_used,
                "is_expired":  c.is_expired(),
                "valid_until": c.last_date.strftime("%Y-%m-%d %H:%M") if c.last_date else "ไม่มีวันหมดอายุ",
            })
        return True, f"Found {len(result)} coupon(s)", result

    def process_get_goods_all(self):
        """ดูสินค้าทั้งหมดที่มีในทุก Cineplex"""
        result = []
        for cineplex in self.__cineplex_list:
            for g in cineplex.goods_list:
                result.append({
                    "cineplex_id":   cineplex.id,
                    "cineplex_name": cineplex.get_cineplex_name(),
                    "name":          g.get_name(),
                    "type":          g.goods_type.value,
                    "flavor":        g.flavor or "-",
                    "price":         g.get_price(),
                    "stock":         g.stock,
                })
        return result

    def process_exchange_reward(self, user_id: str, reward_id: str):
        user = self.search_user_by_id(user_id)
        if not user:
            return False, "User not found."
        if user.tier == MemberTier.GUEST:
            return False, "Guest members cannot exchange rewards. Please register first."

        reward = self.search_reward_by_id(reward_id)
        if not reward:
            return False, "Reward not found."

        if reward.stock <= 0:
            return False, "This reward is out of stock."

        if user.get_point() < reward.point_cost:
            return False, f"Not enough points. Required: {reward.point_cost}, Your points: {user.get_point()}"

        if user.deduct_point(reward.point_cost):
            reward.decrease_stock()
            user.add_reward_history(reward.id, reward.name, reward.point_cost)
            return True, {
                "message":          f"Successfully exchanged '{reward.name}'",
                "remaining_points": user.get_point(),
            }

        return False, "System error during point deduction."

    def process_get_reward_history(self, user_id: str):
        """ดูประวัติการแลกของรางวัลของ user"""
        user = self.search_user_by_id(user_id)
        if not user:
            return False, "User not found.", None
        if user.tier == MemberTier.GUEST:
            return False, "Guest members do not have reward history. Please register first.", None
        history = user.get_reward_history()
        return True, f"Found {len(history)} reward(s) exchanged", history

    # ── monthly coupon process ──

    def process_get_monthly_coupon(self, user_id: str):
        """
        User รับคูปองส่วนลดรายเดือนได้ 1 ครั้ง/เดือน
        คืน: (success, message, data)
        """
        user = self.search_user_by_id(user_id)
        if not user:
            return False, "User not found.", None
        if user.tier == MemberTier.GUEST:
            return False, "Guest members cannot receive monthly coupon. Please register first.", None

        current_ym = datetime.now().strftime("%Y-%m")
        if user.get_last_monthly_coupon() == current_ym:
            return False, f"You have already received the monthly coupon for {current_ym}.", None

        # สร้าง coupon ส่วนลดรายเดือน (50 บาท) อายุถึงสิ้นเดือน
        import calendar
        now = datetime.now()
        last_day = calendar.monthrange(now.year, now.month)[1]
        last_date_str = f"{now.year}-{now.month:02d}-{last_day:02d} 23:59"

        success, result = self.process_create_coupon(
            "discount",
            f"Monthly Coupon {current_ym} ({user.name})",
            discount=50.0,
            last_date=last_date_str,
        )
        if not success:
            return False, "Failed to create coupon.", None

        user.set_last_monthly_coupon(current_ym)
        coupon_id = result["coupon_id"]
        return True, "Monthly coupon received successfully.", {
            "coupon_id":    coupon_id,
            "discount":     50,
            "valid_until":  last_date_str,
            "month":        current_ym,
        }

    # ── showtime seat query ──

    def process_get_available_seats(self, cineplex_id: str, showtime_id: str):
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex:
            return False, "Cineplex not found.", None
        showtime = cineplex.search_showtime_by_id(showtime_id)
        if not showtime:
            return False, "Showtime not found.", None

        available = showtime.get_available_seats()
        return True, "OK", {
            "showtime_id":  showtime_id,
            "movie":        showtime.movie.name,
            "start_time":   showtime.start_time.strftime(Showtime.DT_FORMAT),
            "total_available": len(available),
            "seats":        available,
        }

    # ── booking process ──

    def process_get_booking_history(self, user_id: str, status_filter: str = None):
        user = self.search_user_by_id(user_id)
        if not user:
            return False, "Member not found", None
        if user.tier == MemberTier.GUEST:
            return False, "Guest members cannot view booking history", None
        bookings = user.booking_list
        if status_filter:
            try:
                filter_enum = BookingStatus(status_filter)
                bookings = [b for b in bookings if b.status == filter_enum]
            except ValueError:
                return False, f"Invalid status. Use: {[s.value for s in BookingStatus]}", None
        return True, "OK", (user, bookings)

    def generate(self):
        self.__booking_id += 1
        return self.__booking_id

    def process_create_booking(self, user_id: str, cineplex_id: str,
                               showtime_id: str, seat_nos: list):
        user = self.search_user_by_id(user_id)
        if not user:
            return False, "Member not found"
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex:
            return False, "Cineplex not found"
        showtime = cineplex.search_showtime_by_id(showtime_id)
        if not showtime:
            return False, "Showtime not found"

        booking_id = f"BKG-{self.generate():05d}"
        if self.search_booking_by_id(booking_id):
            return False, "Booking ID already exists"

        theater = showtime.theater
        seats   = []
        for seat_no in seat_nos:
            if not showtime.is_seat_available(seat_no):
                return False, f"Seat {seat_no} is already booked"
            seat = theater.search_seat_by_no(seat_no)
            if not seat:
                return False, f"Seat {seat_no} not found in theater"
            seats.append(seat)

        seat_total  = sum(s.type_seat.get_price() for s in seats)
        raw_total   = showtime.base_price + seat_total
        discount    = user.get_discount()
        total_price = round(raw_total * (1 - discount), 2)

        booking = Booking(booking_id, user, showtime, datetime.now(),
                          BookingStatus.PENDING, total_price)
        booking.showtime_seat = showtime.add_seats(seats, BookingStatus.PENDING)
        self.__booking_list.append(booking)
        user.add_booking(booking)
        return True, {
            "booking_id":  booking_id,
            "seats":       seat_nos,
            "total_price": total_price,
            "discount":    int(discount * 100),
        }

    def process_cancel_booking(self, booking_id: str, user_id: str):
        user = self.search_user_by_id(user_id)
        if not user:
            return False, "Member not found"
        booking = self.search_booking_by_id(booking_id)
        if not booking:
            return False, "Booking not found"
        if booking.status == BookingStatus.CANCELLED:
            return False, "Booking is already cancelled"
        if booking.status == BookingStatus.COMPLETED:
            return False, "Cannot cancel a completed booking"
        if booking.status == BookingStatus.CONFIRMED:
            self.__bank.refund(booking.account, booking.total_price)
        booking.showtime.remove_seats([s.seat_number for s in booking.showtime_seat])
        booking.status = BookingStatus.CANCELLED
        return True, f"Booking {booking_id} cancelled "

    def process_confirm_booking(self, booking_id: str, user_id: str, account_id: str):
        user = self.search_user_by_id(user_id)
        if not user:
            return False, "Member not found"
        booking = self.search_booking_by_id(booking_id)
        if not booking:
            return False, "Booking not found"
        if booking.status != BookingStatus.PENDING:
            return False, f"Booking status is '{booking.status.value}', cannot confirm"

        total  = booking.total_price
        result = self.__bank.payment(account_id, total)
        if result == "Account not found" : return False , result
        if not result:
            return False, "Failed: Insufficient balance"

        booking.account = account_id
        booking.status = BookingStatus.CONFIRMED
        showtime = booking.showtime
        ticket = Ticket(
            booking=booking, cineplex=None, user=user,
            movie=showtime.movie, theater=showtime.theater,
            showtime=showtime, seat_list=booking.showtime_seat,
        )
        booking.ticket = ticket
        user.add_ticket(ticket)
        self.__ticket_list.append(ticket)
        points = len(booking.showtime_seat) * 10
        user.add_point(points)
        return True, f"Confirm booking success | Total Paid: {total} THB | Points earned: {points}"

    def process_change_booking(self, user_id: str, booking_id: str, new_seat_nos: list):
        user = self.search_user_by_id(user_id)
        if not user:
            return None, "User not found"
        if user.tier == MemberTier.GUEST:
            return None, "Guest members cannot change seats. Please register first."
        booking = user.search_booking_by_id(booking_id)
        if not booking:
            return None, "Booking not found"

        current_seats = [s.seat_number for s in booking.showtime_seat]
        if len(new_seat_nos) != len(current_seats):
            return None, f"Validation Error: Must select exactly {len(current_seats)} seats"
        if len(new_seat_nos) != len(set(new_seat_nos)):
            return None, "Validation Error: Duplicate seats requested"

        showtime       = booking.showtime
        theater        = showtime.theater
        booking_status = booking.status
        old_total      = booking.total_price
        new_real_seats = []
        new_total      = 0.0

        for seat_no in new_seat_nos:
            if seat_no not in current_seats:
                if not showtime.is_seat_available(seat_no):
                    return None, f"Seat {seat_no} is already booked"
            seat = theater.search_seat_by_no(seat_no)
            if not seat:
                return None, f"Seat {seat_no} not found in theater"
            new_total += seat.type_seat.get_price()
            new_real_seats.append(seat)

        new_total = round(new_total * (1 - user.get_discount()), 2)

        if booking_status == BookingStatus.CONFIRMED:
            if new_total > old_total:
                return None, "Cannot change to more expensive seats"
            showtime.remove_seats(current_seats.state)
            new_st = showtime.add_seats(new_real_seats, BookingStatus.CONFIRMED)
            booking.showtime_seat = new_st
            booking.total_price   = new_total
            if booking.ticket:
                booking.ticket.seat_list = new_st
            return booking, "Change booking (Confirmed) successful"

        elif booking_status == BookingStatus.PENDING:
            showtime.remove_seats(current_seats)
            new_st = showtime.add_seats(new_real_seats, BookingStatus.PENDING)
            booking.showtime_seat = new_st
            booking.total_price   = new_total
            return booking, "Change booking (Pending) successful"

        return None, "Invalid booking status"

    # ── order process ──

    def process_order_goods(self, cineplex_id, goods_name, values, user_id,
                            account_id, coupon_id=None):
        member = self.search_user_by_id(user_id)
        if not member:
            return False, "Member not found"
        cineplex = self.search_cineplex_by_id(cineplex_id)
        if not cineplex:
            return False, "Cineplex not found"
        target_good = cineplex.search_goods_stock(goods_name, values)
        if not target_good:
            return False, "Out of stock or Not enough items"

        discount_amount = 0
        used_coupon_id  = None
        if coupon_id:
            for c in self.__coupon_list:
                if c.get_coupon_id() == coupon_id:
                    if c.is_expired():
                        last = c.last_date.strftime("%Y-%m-%d %H:%M") if c.last_date else "-"
                        return False, f"Coupon '{coupon_id}' has expired (last_date: {last})"
                    discount_amount = c.get_discount()
                    used_coupon_id  = coupon_id
                    c.update_status("Used")
                    break
            else:
                return False, f"Coupon '{coupon_id}' not found"

        total_price = max((target_good.get_price() * values) - discount_amount, 0)
        order_id    = f"ORD-{self.__order_counter:04d}"
        self.__order_counter += 1

        order  = Order(order_id, goods_name, values, account_id, total_price, used_coupon_id, user_id=user_id)
        result = self.__bank.payment(account_id, total_price) if self.__bank else True
        if result:
            target_good.clearstock(values)
            self.__order_list.append(order)
            return True, {"order_id": order_id, "total_paid": total_price}
        return False, "Payment failed: Insufficient balance or invalid account."

    def process_cancel_order(self, cineplex_id, order_id, user_id):
        member = self.search_user_by_id(user_id)
        if not member:
            return False, "Member not found"
        order = self.search_order_by_id(order_id)
        if not order:
            return False, "Order not found"

        current_status = order.get_status()
        if current_status == OrderStatus.CANCELLED.value:
            return False, "Order is already cancelled"
        if current_status == OrderStatus.REFUNDED.value:
            return False, "Order has already been refunded"

        if current_status == OrderStatus.COMPLETED.value:
            account_id, total_paid = order.get_payment_details()
            # คืนเงิน: ถ้ามี bank ใช้ refund จริง ถ้าไม่มี refund เสมอสำเร็จ
            refund_ok = self.__bank.refund(account_id, total_paid) if self.__bank else True
            if refund_ok:
                goods_name, values = order.get_items()
                cineplex = self.search_cineplex_by_id(cineplex_id)
                if cineplex:
                    g = cineplex.search_goods_stock(goods_name)
                    if g:
                        g.restore_stock(values)
                cid = order.get_used_coupon()
                if cid:
                    for c in self.__coupon_list:
                        if c.get_coupon_id() == cid:
                            c.update_status("Available")
                            break
                order.update_status(OrderStatus.CANCELLED)
                return True, f"Cancel success, Refund {total_paid} THB"
            return False, "Refund failed"
        return False, "Cannot cancel order with current status"

    def process_get_order_history(self, user_id: str, status_filter: str = None):
        """
        ดูประวัติการสั่งซื้อสินค้าของ user
        status_filter: "Completed" | "Cancelled" | "Refunded" | None = ทั้งหมด
        """
        user = self.search_user_by_id(user_id)
        if not user:
            return False, "User not found.", None

        orders = [o for o in self.__order_list if o.get_user_id() == user_id]

        if status_filter:
            try:
                filter_status = OrderStatus(status_filter)
            except ValueError:
                return False, f"Invalid status. Use: {[s.value for s in OrderStatus]}", None
            orders = [o for o in orders if o.get_status() == filter_status.value]

        result = []
        for o in orders:
            goods_name, values = o.get_items()
            _, total_paid      = o.get_payment_details()
            result.append({
                "order_id":   o.get_order_id(),
                "goods_name": goods_name,
                "quantity":   values,
                "total_paid": total_paid,
                "coupon_id":  o.get_used_coupon(),
                "status":     o.get_status(),
            })
        return True, f"Found {len(result)} order(s)", result

    # ── movie / showtime query ──

    def process_get_all_movies(self):
        seen = set()
        result = []
        for cineplex in self.__cineplex_list:
            for movie in cineplex.movies_list:
                if movie.id not in seen:
                    seen.add(movie.id)
                    result.append({
                        "movie_id":  movie.id,
                        "name":      movie.name,
                        "cineplex":  cineplex.get_cineplex_name(),
                    })
        return result

    def process_get_today_showtimes(self):
        today  = datetime.now().date()
        result = []
        for cineplex in self.__cineplex_list:
            for showtime in cineplex.showtime_list:
                if showtime.start_time.date() == today:
                    result.append({
                        "cineplex_name": cineplex.get_cineplex_name(),
                        "showtime_id":   showtime.id,
                        "movie_name":    showtime.movie.name,
                        "theater_id":    showtime.theater.id,
                        "theater_type":  showtime.theater.type_theater.value,
                        "subtitle":      showtime.subtitle,
                        "start_time":    showtime.start_time.strftime(Showtime.DT_FORMAT),
                        "end_time":      showtime.end_time.strftime(Showtime.DT_FORMAT),
                        "base_price":    showtime.base_price,
                        "status":        showtime.status,
                    })
        return result

    def process_get_showtimes_by_date(self, date_str: str):
        """
        ดูรอบฉายของวันใดก็ได้
        date_str: "YYYY-MM-DD"
        """
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return False, "Invalid date format. Use 'YYYY-MM-DD'", None

        result = []
        for cineplex in self.__cineplex_list:
            for showtime in cineplex.showtime_list:
                if showtime.start_time.date() == target_date:
                    result.append({
                        "cineplex_name": cineplex.get_cineplex_name(),
                        "showtime_id":   showtime.id,
                        "movie_name":    showtime.movie.name,
                        "theater_id":    showtime.theater.id,
                        "theater_type":  showtime.theater.type_theater.value,
                        "subtitle":      showtime.subtitle,
                        "start_time":    showtime.start_time.strftime(Showtime.DT_FORMAT),
                        "end_time":      showtime.end_time.strftime(Showtime.DT_FORMAT),
                        "base_price":    showtime.base_price,
                        "status":        showtime.status,
                    })
        return True, f"Showtimes on {date_str}", result

    def process_get_showtimes_by_movie_name(self, movie_name: str):
        keyword = movie_name.strip().lower()
        result  = []
        for cineplex in self.__cineplex_list:
            for showtime in cineplex.showtime_list:
                if keyword in showtime.movie.name.lower():
                    try:
                        end_time_str = showtime.end_time.strftime(Showtime.DT_FORMAT)
                    except Exception:
                        end_time_str = "N/A"
                    result.append({
                        "cineplex_name": cineplex.get_cineplex_name(),
                        "showtime_id":   showtime.id,
                        "movie_id":      showtime.movie.id,
                        "movie_name":    showtime.movie.name,
                        "theater_id":    showtime.theater.id,
                        "theater_type":  showtime.theater.type_theater.value,
                        "subtitle":      showtime.subtitle,
                        "start_time":    showtime.start_time.strftime(Showtime.DT_FORMAT),
                        "end_time":      end_time_str,
                        "base_price":    showtime.base_price,
                        "status":        showtime.status,
                    })
        return result

    def process_view_booking_history(self, user_id):
        user = self.search_user_by_id(user_id)
        if user:
            booking_list = user.booking_list
            if booking_list:
                return True, "This is your booking history.", booking_list
            else:
                return True, "You have never made a booking.", None
        else:
            return False, "User not found.", None

    # ── auth process ──

    def process_register(self, user_id: str, password: str,
                         phone_number: str = "", birthday: str = "") -> tuple:
        """
        สมัครสมาชิก — เปลี่ยน Guest → Silver
        รับ phone_number และ birthday เพิ่มเติม (ถ้ามี)
        """
        user = self.search_user_by_id(user_id)
        if not user:
            return False, "User not found"
        if user.has_password():
            return False, "User already registered. Use change password instead."
        if not password or len(password) < 4:
            return False, "Password must be at least 4 characters"
        user.add_password(password)
        user.set_profile(phone_number=phone_number, birthday=birthday)
        user.change_type(MemberTier.SILVER)
        return True, {
            "user_id":      user_id,
            "name":         user.name,
            "email":        user.email,
            "phone_number": user.phone_number,
            "birthday":     user.birthday,
            "tier":         user.tier.value,
            "message":      "Register successful",
        }

    def process_login(self, user_id: str, password: str) -> tuple:
        user = self.search_user_by_id(user_id)
        if not user:
            return False, "User not found"
        if not user.has_password():
            return False, "User has not registered yet. Please register first."
        if not user.check_password(password):
            return False, "Incorrect password"
        return True, {
            "user_id": user_id,
            "name":    user.name,
            "tier":    user.tier.value,
            "points":  user.get_point(),
            "message": "Login successful",
        }

    def process_review_movie(self,user_id,booking_id,star,comment) :
            if star not in [1,2,3,4,5] :
                return False , "Can rate 1 - 5 star only"
            user = self.search_user_by_id(user_id)
            if user :
                booking = user.search_booking_by_id(booking_id)
                if booking :
                    if booking.status == BookingStatus.COMPLETED :
                        movie = booking.showtime.movie
                        review = Review(star,comment,user.name)
                        movie.add_review(review)
                        return True , "Review success"
                    else :
                        return False , "You haven't watch the movie"
                else :
                    return False , "Booking not found"
            else :
                return False , "User not found."

    def process_read_review(self,movie_id) :
        result = []
        check = 1
        for cineplex in self.__cineplex_list:
            for movie in cineplex.movies_list:
                if movie.id == movie_id :
                    check = 0
                    for review in movie.review :
                        result.append(review.read)
        if check :
            return "Movie not found"
        if not result :
            return "No review"
        return result
    
    def complete(self,booking_id) :
        for i in self.__booking_list :
            if i.id == booking_id :
                i.status = BookingStatus.COMPLETED