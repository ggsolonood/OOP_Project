from enums import GoodsType, OrderStatus

class Goods:
    def __init__(self, goods_id: str, name: str, price: float, stock: int, g_type: GoodsType):
        self.__id = goods_id
        self.__name = name
        self.__price = price
        self.__stock = stock
        self.__type = g_type

    @property
    def id(self): return self.__id
    @property
    def name(self): return self.__name
    @property
    def price(self): return self.__price
    @property
    def stock(self): return self.__stock
    @property
    def type(self): return self.__type

    def decrease_stock(self, amount: int): self.__stock -= amount
    def increase_stock(self, amount: int): self.__stock += amount

class Order:
    def __init__(self, order_id: str, items: dict, total: float, account_id: str, coupon_id: str = None):
        self.__id = order_id
        self.__items = items
        self.__total = total
        self.__account_id = account_id
        self.__coupon_id = coupon_id
        self.__status = OrderStatus.COMPLETED

    @property
    def id(self): return self.__id
    @property
    def items(self): return self.__items
    @property
    def total(self): return self.__total
    @property
    def account_id(self): return self.__account_id
    @property
    def coupon_id(self): return self.__coupon_id
    @property
    def status(self): return self.__status
    @status.setter
    def status(self, val: OrderStatus): self.__status = val

class Reward:
    def __init__(self, reward_id: str, name: str, points: int):
        self.__id = reward_id
        self.__name = name
        self.__points = points

    @property
    def id(self): return self.__id
    @property
    def name(self): return self.__name
    @property
    def points(self): return self.__points