from pydantic import BaseModel
from typing import List, Dict, Optional

class BookTicketReq(BaseModel):
    user_id: str
    showtime_id: str
    seat_ids: List[str]
    coupon_id: Optional[str] = None

class ConfirmBookingReq(BaseModel):
    account_number: str

class OrderGoodsReq(BaseModel):
    user_id: str
    cineplex_name: str
    items: Dict[str, int]
    account_number: str
    coupon_id: Optional[str] = None

class UpgradeMemberReq(BaseModel):
    account_number: str

class ChangeSeatsReq(BaseModel):
    user_id: str
    new_seat_ids: List[str]

class ReviewReq(BaseModel):
    user_id: str
    star: int
    comment: str