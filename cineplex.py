from datetime import datetime
from payment import Bank
from goods import Order
from theater import Cineplex, ShowtimeSeat, Review
from user import User, Booking, Ticket, FixedDiscountCoupon
from enums import MemberTier, BookingStatus, OrderStatus, SeatStatus, TicketStatus

class JamorCineplex:
    def __init__(self, bank: Bank):
        self.__bank = bank
        self.__cineplexes = {} 
        self.__users = {}
        self.__order_counter = 1
        self.__booking_counter = 1
        self.__ticket_counter = 1

    def __gen_bkg_id(self):
        uid = f"B{self.__booking_counter:03d}"; self.__booking_counter += 1; return uid
    def __gen_ord_id(self):
        uid = f"O{self.__order_counter:03d}"; self.__order_counter += 1; return uid
    def __gen_tkt_id(self):
        uid = f"TK{self.__ticket_counter:03d}"; self.__ticket_counter += 1; return uid

    def add_cineplex(self, cpx: Cineplex): self.__cineplexes[cpx.id] = cpx
    def add_user(self, user: User): self.__users[user.id] = user

    def search_movie_by_name(self, name: str):
        for cpx in self.__cineplexes.values():
            for m in cpx.movies:
                if name.lower() in m.name.lower(): return m
        return None

    def search_cineplex_by_name(self, name: str):
        for cpx in self.__cineplexes.values():
            if name.lower() in cpx.name.lower(): return cpx
        return None

    def search_showtime_details(self, movie_name: str, cineplex_name: str):
        cpx = self.search_cineplex_by_name(cineplex_name)
        if not cpx: return False, "Cineplex not found"
        results = []
        for m in cpx.movies:
            if movie_name.lower() in m.name.lower():
                for st in m.showtimes:
                    results.append({"showtime_id": st.id, "time": st.start_time.strftime("%Y-%m-%d %H:%M")})
        return True, results

    def __find_movie(self, movie_id: str):
        for cpx in self.__cineplexes.values():
            for m in cpx.movies:
                if m.id == movie_id: return m
        return None

    def __find_showtime(self, showtime_id: str):
        for cpx in self.__cineplexes.values():
            for m in cpx.movies:
                for st in m.showtimes:
                    if st.id == showtime_id: return st, cpx
        return None, None

    def __find_booking(self, booking_id: str):
        for u in self.__users.values():
            for b in u.bookings:
                if b.id == booking_id: return b, u
        return None, None

    def __find_order(self, order_id: str):
        for u in self.__users.values():
            for o in u.orders:
                if o.id == order_id: return o, u
        return None, None

    # ================= USE CASES =================

    def get_all_movies(self):
        unique = {m.id: m for cpx in self.__cineplexes.values() for m in cpx.movies}
        return [{"id": m.id, "name": m.name, "genre": m.genre.value, "age_rating": m.age_rating} for m in unique.values()]

    def get_showtimes_by_movie(self, movie_id: str):
        m = self.__find_movie(movie_id)
        if not m: return False, "Movie not found"
        results = []
        for cpx in self.__cineplexes.values():
            for st in m.showtimes:
                if st.movie.id == movie_id:
                    # โชว์ ID รอบฉายชัดเจน
                    results.append({
                        "showtime_id": st.id,
                        "cineplex": cpx.name,
                        "theater": st.theater.name,
                        "theater_type": st.theater.type.value,
                        "time": st.start_time.strftime("%Y-%m-%d %H:%M")
                    })
        return True, results

    def get_available_seats(self, showtime_id: str):
        st, _ = self.__find_showtime(showtime_id)
        if not st: return False, "Showtime not found"
        
        avail = []
        base_price = st.movie.base_price + st.theater.additional_price
        for seat in st.theater.seats:
            if seat.id not in st.showtime_seats:
                total_seat_price = base_price + seat.price
                avail.append({
                    "id": seat.id, 
                    "number": seat.number, 
                    "type": seat.type.value,
                    "total_price": total_seat_price
                })
        return True, avail

    def book_ticket(self, user_id: str, showtime_id: str, seat_ids: list, coupon_id: str = None):
        if user_id not in self.__users: return False, "User not found"
        user = self.__users[user_id]
        st, cpx = self.__find_showtime(showtime_id)
        if not st: return False, "Showtime not found"

        now = datetime.now()
        if user.penalty_end and now < user.penalty_end: return False, "You are penalized"
        if (st.start_time - now).total_seconds() < 900: return False, "Too late to book"

        theater_seats = {s.id: s for s in st.theater.seats}
        total_raw_price = 0
        base_price = st.movie.base_price + st.theater.additional_price
        seat_names = []
        
        for s_id in seat_ids:
            if s_id not in theater_seats: return False, f"Invalid seat {s_id}"
            if s_id in st.showtime_seats: return False, f"Seat {s_id} already booked"
            total_raw_price += (base_price + theater_seats[s_id].price)
            seat_names.append(theater_seats[s_id].number)

        final_price = total_raw_price * (1 - user.discount)

        if coupon_id:
            coupon = next((c for c in user.coupons if c.id == coupon_id and not c.is_used), None)
            if not coupon: return False, "Invalid or used coupon"
            final_price = coupon.calculate_discount(final_price)
            coupon.is_used = True

        for s_id in seat_ids:
            seat = theater_seats[s_id]
            st.showtime_seats[s_id] = ShowtimeSeat(seat.id, seat.number, seat.type)
        
        b_id = self.__gen_bkg_id()
        bkg = Booking(b_id, user_id, showtime_id, seat_ids, final_price, coupon_id)
        user.add_booking(bkg)
        
        # แสดงผลว่าใครจอง
        return True, f"Booking ID: {b_id} | User: {user.name} (ID: {user.id}) | Location: {cpx.name}, {st.theater.name} | Movie: {st.movie.name} ({st.start_time.strftime('%H:%M')}) | Seats: {', '.join(seat_names)}"

    def confirm_booking(self, booking_id: str, account_number: str):
        bkg, user = self.__find_booking(booking_id)
        if not bkg or bkg.status != BookingStatus.PENDING: return False, "Invalid booking"
        
        if self.__bank.pay(account_number, bkg.total):
            bkg.status = BookingStatus.CONFIRMED
            bkg.account_number = account_number
            user.add_points(int(bkg.total // 10))
            
            st, _ = self.__find_showtime(bkg.showtime_id)
            tickets_generated = []
            
            for s_id in bkg.seat_ids:
                if s_id in st.showtime_seats:
                    st.showtime_seats[s_id].status = SeatStatus.OCCUPIED
                    seat_num = st.showtime_seats[s_id].number
                    t_id = self.__gen_tkt_id()
                    new_ticket = Ticket(t_id, booking_id, st.id, seat_num)
                    user.add_ticket(new_ticket)
                    tickets_generated.append(f"Ticket: {t_id} (Seat: {seat_num})")
                    
            return True, f"Payment successful. Tickets generated: {', '.join(tickets_generated)}"
        return False, "Payment failed. Check account number."

    def cancel_booking(self, booking_id: str):
        bkg, user = self.__find_booking(booking_id)
        if not bkg or bkg.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]: return False, "Cannot cancel"
        
        if bkg.status == BookingStatus.CONFIRMED:
            self.__bank.refund(bkg.account_number, bkg.total)
            for t in user.tickets:
                if t.booking_id == booking_id:
                    t.status = TicketStatus.CANCELLED
        
        bkg.status = BookingStatus.CANCELLED
        
        if bkg.coupon_id:
            coupon = next((c for c in user.coupons if c.id == bkg.coupon_id), None)
            if coupon: coupon.is_used = False

        st, _ = self.__find_showtime(bkg.showtime_id)
        for s_id in bkg.seat_ids:
            if s_id in st.showtime_seats:
                del st.showtime_seats[s_id]
                
        return True, f"Booking {booking_id} has been cancelled and refunded successfully."

    def get_goods_by_cineplex(self, cineplex_name: str):
        cpx = self.search_cineplex_by_name(cineplex_name)
        if not cpx: return False, "Cineplex not found"
        return True, [{"id": g.id, "name": g.name, "type": g.type.value, "price": g.price, "stock": g.stock} for g in cpx.goods]

    def order_goods(self, user_id: str, cineplex_name: str, items_dict: dict, account_number: str, coupon_id: str = None):
        if user_id not in self.__users: return False, "User not found"
        
        cpx = self.search_cineplex_by_name(cineplex_name)
        if not cpx: return False, "Cineplex not found"
        
        user = self.__users[user_id]
        cpx_goods = {g.id: g for g in cpx.goods}
        
        total = 0
        items_bought = []
        for g_id, qty in items_dict.items():
            if g_id not in cpx_goods or cpx_goods[g_id].stock < qty: return False, f"Stock issue for {g_id}"
            total += cpx_goods[g_id].price * qty
            items_bought.append(f"{cpx_goods[g_id].name} (x{qty})")

        if coupon_id:
            coupon = next((c for c in user.coupons if c.id == coupon_id and not c.is_used), None)
            if not coupon: return False, "Invalid or used coupon"
            total = coupon.calculate_discount(total)
            coupon.is_used = True

        if self.__bank.pay(account_number, total):
            for g_id, qty in items_dict.items(): cpx_goods[g_id].decrease_stock(qty)
            o_id = self.__gen_ord_id()
            user.add_order(Order(o_id, user_id, items_dict, total, account_number, coupon_id))
            
            # แสดงผลว่าใครเป็นคนสั่งซื้อ
            return True, f"Order {o_id} successful | User: {user.name} (ID: {user.id}) | Bought: {', '.join(items_bought)}. Total Paid: {total} THB."
            
        return False, "Payment failed. Check account number."

    def cancel_order(self, order_id: str, cineplex_name: str):
        order, user = self.__find_order(order_id)
        if not order or order.status == OrderStatus.CANCELLED: return False, "Invalid order"
        
        cpx = self.search_cineplex_by_name(cineplex_name)
        if not cpx: return False, "Cineplex not found"
        cpx_goods = {g.id: g for g in cpx.goods}

        self.__bank.refund(order.account_number, order.total)
        for g_id, qty in order.items.items():
            if g_id in cpx_goods: cpx_goods[g_id].increase_stock(qty)
                
        if order.coupon_id:
            coupon = next((c for c in user.coupons if c.id == order.coupon_id), None)
            if coupon: coupon.is_used = False

        order.status = OrderStatus.CANCELLED
        return True, f"Order {order_id} cancelled and refunded successfully."

    def upgrade_member(self, user_id: str, account_number: str):
        if user_id not in self.__users: return False, "User not found"
        user = self.__users[user_id]
        
        if self.__bank.pay(account_number, 150.0):
            user.upgrade_tier()
            return True, f"Upgrade successful. You are now a {user.tier.value} member."
        return False, "Payment failed. Check account number."

    def view_history(self, user_id: str):
        if user_id not in self.__users: return False, "User not found"
        user = self.__users[user_id]
        history = []
        for b in user.bookings:
            if user.tier == MemberTier.GUEST and b.status in [BookingStatus.COMPLETED, BookingStatus.CANCELLED]: continue
            history.append({
                "id": b.id, 
                "status": b.status.value, 
                "total": b.total,
                "date": b.created_at.strftime("%Y-%m-%d %H:%M")
            })
        if not history and user.tier == MemberTier.GUEST:
            return True, "No active bookings. Guests cannot view past history."
        return True, history

    def show_points_and_rewards(self, user_id: str):
        if user_id not in self.__users: return False, "User not found"
        user = self.__users[user_id]
        if user.tier == MemberTier.GUEST: return False, "Members only"
        
        rwds = []
        for cpx in self.__cineplexes.values():
            for r in cpx.rewards: rwds.append(f"[{r.id}] {r.name} - Required: {r.points} points")
        return True, {"points": user.points, "rewards": rwds}

    def redeem_reward(self, user_id: str, reward_id: str):
        if user_id not in self.__users: return False, "User not found"
        user = self.__users[user_id]
        if user.tier == MemberTier.GUEST: return False, "Members only"
        
        target_rwd = None
        for cpx in self.__cineplexes.values():
            for r in cpx.rewards:
                if r.id == reward_id: target_rwd = r; break
        
        if not target_rwd: return False, "Reward not found"
        if user.points >= target_rwd.points:
            user.decrease_points(target_rwd.points)
            return True, "Redeem successful."
        return False, "Not enough points"

    def collect_monthly_coupon(self, user_id: str, coupon_id: str):
        if user_id not in self.__users: return False, "User not found"
        user = self.__users[user_id]
        if user.tier == MemberTier.GUEST: return False, "Members only"
        
        discount_val = 50.0 
        if user.tier == MemberTier.GOLD: discount_val = 100.0
        elif user.tier == MemberTier.PLATINUM: discount_val = 150.0

        user.add_coupon(FixedDiscountCoupon(coupon_id, f"Monthly {discount_val} THB", discount_val))
        return True, f"Coupon collected for {user.tier.value} tier."

    def change_seats(self, user_id: str, booking_id: str, new_seat_ids: list):
        bkg, user = self.__find_booking(booking_id)
        if not bkg or user.id != user_id: return False, "Booking not found"
        if user.tier == MemberTier.GUEST: return False, "Members only"
        
        if bkg.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]: 
            return False, "Cannot change seats for this booking"
        
        if len(new_seat_ids) != len(bkg.seat_ids): return False, "Seat count mismatch"

        st, _ = self.__find_showtime(bkg.showtime_id)
        theater_seats = {s.id: s for s in st.theater.seats}
        
        new_total_raw = 0
        base_price = st.movie.base_price + st.theater.additional_price
        
        for s_id in new_seat_ids:
            if s_id not in theater_seats: return False, "Invalid seat"
            if s_id in st.showtime_seats and s_id not in bkg.seat_ids: return False, "Seat already booked"
            new_total_raw += (base_price + theater_seats[s_id].price)

        new_final = new_total_raw * (1 - user.discount)
        
        if bkg.coupon_id:
            coupon = next((c for c in user.coupons if c.id == bkg.coupon_id), None)
            if coupon: new_final = coupon.calculate_discount(new_final)

        if new_final > bkg.total: return False, "Cannot change to higher price"
        
        diff = bkg.total - new_final

        if bkg.status == BookingStatus.CONFIRMED:
            if diff > 0: self.__bank.refund(bkg.account_number, diff)
            
            booking_tickets = [t for t in user.tickets if t.booking_id == booking_id and t.status != TicketStatus.CANCELLED]
            
            for s_id in bkg.seat_ids: 
                if s_id in st.showtime_seats: del st.showtime_seats[s_id]
                
            for i, s_id in enumerate(new_seat_ids): 
                seat = theater_seats[s_id]
                new_st_seat = ShowtimeSeat(seat.id, seat.number, seat.type)
                new_st_seat.status = SeatStatus.OCCUPIED
                st.showtime_seats[s_id] = new_st_seat
                if i < len(booking_tickets):
                    booking_tickets[i].seat_number = seat.number

        elif bkg.status == BookingStatus.PENDING:
            for s_id in bkg.seat_ids: 
                if s_id in st.showtime_seats: del st.showtime_seats[s_id]
            for s_id in new_seat_ids: 
                seat = theater_seats[s_id]
                new_st_seat = ShowtimeSeat(seat.id, seat.number, seat.type)
                new_st_seat.status = SeatStatus.BOOKED 
                st.showtime_seats[s_id] = new_st_seat

        bkg.seat_ids = new_seat_ids 
        bkg.total = new_final
        return True, f"Changed seats successfully. Refund: {diff if bkg.status == BookingStatus.CONFIRMED else 0.0}"

    def write_review(self, user_id: str, booking_id: str, star: int, comment: str):
        bkg, user = self.__find_booking(booking_id)
        if not bkg or user.id != user_id: return False, "Booking not found"
        if user.tier == MemberTier.GUEST: return False, "Members only"
        if bkg.status != BookingStatus.COMPLETED: return False, "You haven't watched this movie yet."
        
        st, _ = self.__find_showtime(bkg.showtime_id)
        st.movie.add_review(Review(star, comment, user.name))
        return True, "Review added successfully."

    def read_reviews(self, movie_id: str):
        m = self.__find_movie(movie_id)
        if not m: return False, "Movie not found"
        return True, [{"star": r.star, "comment": r.comment, "reviewer": r.user_name} for r in m.reviews]

    def view_tickets(self, user_id: str, booking_id: str):
        bkg, user = self.__find_booking(booking_id)
        if not bkg or user.id != user_id: return False, "Booking not found"
        if bkg.status not in [BookingStatus.CONFIRMED, BookingStatus.COMPLETED]:
            return False, "Tickets have not been issued or booking was cancelled."
        
        st, cpx = self.__find_showtime(bkg.showtime_id)
        
        tickets_info = []
        for t in user.tickets:
            if t.booking_id == booking_id:
                tickets_info.append({
                    "ticket_id": t.id,
                    "movie": st.movie.name,
                    "cineplex": cpx.name,
                    "theater": st.theater.name,
                    "showtime": st.start_time.strftime("%Y-%m-%d %H:%M"),
                    "seat": t.seat_number,
                    "status": t.status.value
                })
        return True, tickets_info