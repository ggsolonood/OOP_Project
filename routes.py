from fastapi import APIRouter, HTTPException
from mock_data import system
from schemas import *

api_router = APIRouter()

@api_router.get("/movies")
def get_all_movies(): return system.get_all_movies()

@api_router.get("/movies/{movie_id}/showtimes")
def get_showtimes(movie_id: str):
    success, res = system.get_showtimes_by_movie(movie_id)
    if not success: raise HTTPException(404, res)
    return res

@api_router.get("/showtimes/{showtime_id}/seats")
def get_seats(showtime_id: str):
    success, res = system.get_available_seats(showtime_id)
    if not success: raise HTTPException(404, res)
    return res

@api_router.post("/bookings")
def book_ticket(req: BookTicketReq):
    success, res = system.book_ticket(req.user_id, req.showtime_id, req.seat_ids, req.coupon_id)
    if not success: raise HTTPException(400, res)
    return {"message": res}

@api_router.post("/bookings/{booking_id}/confirm")
def confirm_booking(booking_id: str, req: ConfirmBookingReq):
    success, res = system.confirm_booking(booking_id, req.account_id)
    if not success: raise HTTPException(400, res)
    return {"message": res}

@api_router.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: str):
    success, res = system.cancel_booking(booking_id)
    if not success: raise HTTPException(400, res)
    return {"message": res}

@api_router.get("/cineplexes/{cineplex_id}/goods")
def get_goods(cineplex_id: str):
    success, res = system.get_goods_by_cineplex(cineplex_id)
    if not success: raise HTTPException(404, res)
    return res

@api_router.post("/store/order")
def order_goods(req: OrderGoodsReq):
    success, res = system.order_goods(req.user_id, req.cineplex_id, req.items, req.account_id, req.coupon_id)
    if not success: raise HTTPException(400, res)
    return {"message": res}

@api_router.delete("/store/order/{order_id}")
def cancel_order(order_id: str, cineplex_id: str):
    success, res = system.cancel_order(order_id, cineplex_id)
    if not success: raise HTTPException(400, res)
    return {"message": res}

@api_router.post("/users/{user_id}/upgrade")
def upgrade_member(user_id: str, req: UpgradeMemberReq):
    success, res = system.upgrade_member(user_id, req.account_id)
    if not success: raise HTTPException(400, res)
    return {"message": res}

@api_router.get("/users/{user_id}/history")
def view_history(user_id: str):
    success, res = system.view_history(user_id)
    if not success: raise HTTPException(404, res)
    return res

@api_router.get("/users/{user_id}/rewards")
def get_rewards(user_id: str):
    success, res = system.show_points_and_rewards(user_id)
    if not success: raise HTTPException(400, res)
    return res

@api_router.post("/users/{user_id}/rewards/{reward_id}/redeem")
def redeem_reward(user_id: str, reward_id: str):
    success, res = system.redeem_reward(user_id, reward_id)
    if not success: raise HTTPException(400, res)
    return {"message": res}

@api_router.post("/users/{user_id}/coupons/{coupon_id}/collect")
def collect_coupon(user_id: str, coupon_id: str):
    success, res = system.collect_monthly_coupon(user_id, coupon_id)
    if not success: raise HTTPException(400, res)
    return {"message": res}

@api_router.put("/bookings/{booking_id}/seats")
def change_seats(booking_id: str, req: ChangeSeatsReq):
    success, res = system.change_seats(req.user_id, booking_id, req.new_seat_ids)
    if not success: raise HTTPException(400, res)
    return {"message": res}

@api_router.post("/bookings/{booking_id}/review")
def write_review(booking_id: str, req: ReviewReq):
    success, res = system.write_review(req.user_id, booking_id, req.star, req.comment)
    if not success: raise HTTPException(400, res)
    return {"message": res}

@api_router.get("/movies/{movie_id}/reviews")
def read_reviews(movie_id: str):
    success, res = system.read_reviews(movie_id)
    if not success: raise HTTPException(404, res)
    return res