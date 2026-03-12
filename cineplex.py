from datetime import datetime
from payment import Bank
from goods import Order
from theater import Cineplex, ShowtimeSeat, Review
from user import User, Booking, DiscountCoupon, ExchangeCoupon
from enums import MemberTier, BookingStatus, OrderStatus, SeatStatus

class JamorCineplex:
    def __init__(self, bank: Bank):
        self.__bank = bank
        self.__cineplexes = {} 
        self.__users = {}
        
        self.__order_counter = 1
        self.__booking_counter = 1

    def __gen_bkg_id(self):
        uid = f"B{self.__booking_counter:03d}"
        self.__booking_counter += 1
        return uid

    def __gen_ord_id(self):
        uid = f"O{self.__order_counter:03d}"
        self.__order_counter += 1
        return uid

    def add_cineplex(self, cpx: Cineplex): self.__cineplexes[cpx.id] = cpx
    def add_user(self, user: User): self.__users[user.id] = user

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

    # ================= 16 USE CASES =================

    # 1. แสดงหนัง
    def get_all_movies(self):
        unique = {m.id: m.name for cpx in self.__cineplexes.values() for m in cpx.movies}
        return [{"id": k, "name": v} for k, v in unique.items()]

    # 2. แสดงรอบฉายของหนัง
    def get_showtimes_by_movie(self, movie_id: str):
        m = self.__find_movie(movie_id)
        if not m: return False, "Movie not found"
        return True, [{"id": st.id, "time": st.start_time.strftime("%Y-%m-%d %H:%M")} for st in m.showtimes]

    # 3. แสดงที่นั่งว่าง และราคา (Movie Base + Theater Markup + Seat Markup)
    def get_available_seats(self, showtime_id: str):
        st, _ = self.__find_showtime(showtime_id)
        if not st: return False, "Showtime not found"
        
        avail = []
        base_price = st.movie.base_price + st.theater.additional_price

        for seat in st.theater.seats:
            if seat.id not in st.showtime_seats:
                total_seat_price = base_price + seat.price
                avail.append({"id": seat.id, "number": seat.number, "price": total_seat_price})
        return True, avail

    # 4. จองตั๋ว 
    def book_ticket(self, user_id: str, showtime_id: str, seat_ids: list, coupon_id: str = None):
        if user_id not in self.__users: return False, "User not found"
        user = self.__users[user_id]
        st, _ = self.__find_showtime(showtime_id)
        if not st: return False, "Showtime not found"

        now = datetime.now()
        if user.penalty_end and now < user.penalty_end: return False, "You are penalized"
        if (st.start_time - now).total_seconds() < 900: return False, "Too late to book"

        theater_seats = {s.id: s for s in st.theater.seats}
        total_raw_price = 0
        base_price = st.movie.base_price + st.theater.additional_price
        
        for s_id in seat_ids:
            if s_id not in theater_seats: return False, "Invalid seat"
            if s_id in st.showtime_seats: return False, "Seat already booked"
            total_raw_price += (base_price + theater_seats[s_id].price)

        final_price = total_raw_price * (1 - user.discount)

        if coupon_id:
            coupon = next((c for c in user.coupons if c.id == coupon_id and not c.is_used), None)
            if not coupon: return False, "Invalid or used coupon"
            if isinstance(coupon, DiscountCoupon):
                final_price = max(final_price - coupon.discount_amount, 0)
                coupon.is_used = True
            else:
                return False, "This coupon cannot be used for booking"

        # สร้าง ShowtimeSeat
        for s_id in seat_ids:
            seat = theater_seats[s_id]
            st.showtime_seats[s_id] = ShowtimeSeat(seat.id, seat.number, seat.type)
        
        b_id = self.__gen_bkg_id()
        bkg = Booking(b_id, showtime_id, seat_ids, final_price, coupon_id)
        user.add_booking(bkg)
        return True, b_id

    # 5. จ่ายเงินยืนยันการจอง
    def confirm_booking(self, booking_id: str, account_id: str):
        bkg, user = self.__find_booking(booking_id)
        if not bkg or bkg.status != BookingStatus.PENDING: return False, "Invalid booking"
        
        if self.__bank.pay(account_id, bkg.total):
            bkg.status = BookingStatus.CONFIRMED
            bkg.account_id = account_id
            user.add_points(int(bkg.total // 10))
            
            st, _ = self.__find_showtime(bkg.showtime_id)
            for s_id in bkg.seat_ids:
                if s_id in st.showtime_seats:
                    st.showtime_seats[s_id].status = SeatStatus.OCCUPIED
                    
            return True, "Confirmed"
        return False, "Payment failed"

    # 6. ยกเลิกจอง
    def cancel_booking(self, booking_id: str):
        bkg, user = self.__find_booking(booking_id)
        if not bkg or bkg.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]: return False, "Cannot cancel"
        
        if bkg.status == BookingStatus.CONFIRMED:
            self.__bank.refund(bkg.account_id, bkg.total)
        
        bkg.status = BookingStatus.CANCELLED
        
        if bkg.coupon_id:
            coupon = next((c for c in user.coupons if c.id == bkg.coupon_id), None)
            if coupon: coupon.is_used = False

        st, _ = self.__find_showtime(bkg.showtime_id)
        for s_id in bkg.seat_ids:
            if s_id in st.showtime_seats:
                del st.showtime_seats[s_id]
                
        return True, "Cancelled"

    # 7. สั่งซื้อสินค้า
    def order_goods(self, user_id: str, cineplex_id: str, items_dict: dict, account_id: str, coupon_id: str = None):
        if user_id not in self.__users: return False, "User not found"
        if cineplex_id not in self.__cineplexes: return False, "Cineplex not found"
        
        user = self.__users[user_id]
        cpx = self.__cineplexes[cineplex_id]
        cpx_goods = {g.id: g for g in cpx.goods}
        
        total = 0
        for g_id, qty in items_dict.items():
            if g_id not in cpx_goods or cpx_goods[g_id].stock < qty: return False, f"Stock issue for {g_id}"
            total += cpx_goods[g_id].price * qty

        if coupon_id:
            coupon = next((c for c in user.coupons if c.id == coupon_id and not c.is_used), None)
            if not coupon: return False, "Invalid or used coupon"
                
            if isinstance(coupon, DiscountCoupon):
                total = max(total - coupon.discount_amount, 0)
                coupon.is_used = True
            elif isinstance(coupon, ExchangeCoupon):
                for free_item in coupon.goods_list:
                    if free_item in items_dict:
                        total = max(total - cpx_goods[free_item].price, 0)
                coupon.is_used = True

        if self.__bank.pay(account_id, total):
            for g_id, qty in items_dict.items(): cpx_goods[g_id].decrease_stock(qty)
            o_id = self.__gen_ord_id()
            user.add_order(Order(o_id, items_dict, total, account_id, coupon_id))
            return True, o_id
            
        return False, "Payment failed"

    # 8. ยกเลิกคำสั่งซื้อ
    def cancel_order(self, order_id: str, cineplex_id: str):
        order, user = self.__find_order(order_id)
        if not order or order.status == OrderStatus.CANCELLED: return False, "Invalid order"
        
        cpx = self.__cineplexes.get(cineplex_id)
        if not cpx: return False, "Cineplex not found"
        cpx_goods = {g.id: g for g in cpx.goods}

        self.__bank.refund(order.account_id, order.total)
        for g_id, qty in order.items.items():
            if g_id in cpx_goods: cpx_goods[g_id].increase_stock(qty)
                
        if order.coupon_id:
            coupon = next((c for c in user.coupons if c.id == order.coupon_id), None)
            if coupon: coupon.is_used = False

        order.status = OrderStatus.CANCELLED
        return True, "Order cancelled"

    # 9. สมัครสมาชิก
    def upgrade_member(self, user_id: str, account_id: str):
        if user_id not in self.__users: return False, "User not found"
        user = self.__users[user_id]
        if user.tier != MemberTier.GUEST: return False, "Already a member"

        if self.__bank.pay(account_id, 500.0):
            user.tier = MemberTier.SILVER
            return True, "Upgraded"
        return False, "Payment failed"

    # 10. ดูประวัติ
    def view_history(self, user_id: str):
        if user_id not in self.__users: return False, "User not found"
        user = self.__users[user_id]
        history = []
        for b in user.bookings:
            if user.tier == MemberTier.GUEST and b.status in [BookingStatus.COMPLETED, BookingStatus.CANCELLED]: continue
            history.append({"id": b.id, "status": b.status.value, "total": b.total})
        return True, history

    # 11. โชว์พ้อย & รางวัล
    def show_points_and_rewards(self, user_id: str):
        if user_id not in self.__users: return False, "User not found"
        user = self.__users[user_id]
        if user.tier == MemberTier.GUEST: return False, "Members only"
        
        rwds = []
        for cpx in self.__cineplexes.values():
            for r in cpx.rewards: rwds.append({"id": r.id, "name": r.name, "cost": r.points})
        return True, {"points": user.points, "rewards": rwds}

    # 12. แลกของ
    def redeem_reward(self, user_id: str, reward_id: str):
        if user_id not in self.__users: return False, "User not found"
        user = self.__users[user_id]
        if user.tier == MemberTier.GUEST: return False, "Members only"
        
        target_rwd = None
        for cpx in self.__cineplexes.values():
            for r in cpx.rewards:
                if r.id == reward_id:
                    target_rwd = r
                    break
        
        if not target_rwd: return False, "Reward not found"
        if user.points >= target_rwd.points:
            user.decrease_points(target_rwd.points)
            return True, "Redeemed"
        return False, "Not enough points"

    # 13. เก็บคูปอง
    def collect_monthly_coupon(self, user_id: str, coupon_id: str):
        if user_id not in self.__users: return False, "User not found"
        user = self.__users[user_id]
        if user.tier == MemberTier.GUEST: return False, "Members only"
        
        user.add_coupon(DiscountCoupon(coupon_id, "Monthly 50 THB", 50.0))
        return True, "Coupon collected"

    # 14. เปลี่ยนที่นั่ง
    def change_seats(self, user_id: str, booking_id: str, new_seat_ids: list):
        bkg, user = self.__find_booking(booking_id)
        if not bkg or user.id != user_id: return False, "Booking not found"
        if user.tier == MemberTier.GUEST: return False, "Members only"
        if bkg.status != BookingStatus.CONFIRMED: return False, "Must be confirmed"
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
            if isinstance(coupon, DiscountCoupon):
                new_final = max(new_final - coupon.discount_amount, 0)

        if new_final > bkg.total: return False, "Cannot change to higher price"
        
        diff = bkg.total - new_final
        if diff > 0: self.__bank.refund(bkg.account_id, diff)
        
        for s_id in bkg.seat_ids: 
            if s_id in st.showtime_seats:
                del st.showtime_seats[s_id]
            
        for s_id in new_seat_ids: 
            seat = theater_seats[s_id]
            new_st_seat = ShowtimeSeat(seat.id, seat.number, seat.type)
            new_st_seat.status = SeatStatus.OCCUPIED # ยืนยันแล้ว
            st.showtime_seats[s_id] = new_st_seat

        bkg.seat_ids = new_seat_ids 
        bkg.total = new_final
        return True, f"Seats changed. Refund: {diff}"

    # 15. เขียนรีวิว
    def write_review(self, user_id: str, booking_id: str, star: int, comment: str):
        bkg, user = self.__find_booking(booking_id)
        if not bkg or user.id != user_id: return False, "Booking not found"
        if user.tier == MemberTier.GUEST: return False, "Members only"
        if bkg.status != BookingStatus.COMPLETED: return False, "Movie not watched yet"
        
        st, _ = self.__find_showtime(bkg.showtime_id)
        st.movie.add_review(Review(star, comment, user.name))
        return True, "Review added"

    # 16. อ่านรีวิว
    def read_reviews(self, movie_id: str):
        m = self.__find_movie(movie_id)
        if not m: return False, "Movie not found"
        return True, [{"star": r.star, "comment": r.comment, "user": r.user_name} for r in m.reviews]