from abc import ABC, abstractmethod


class Goods(ABC):
    def __init__(self, name, values: int, price):
        self._name = name
        self._values = values
        self._price = price

    def get_name(self):
        return self._name

    def get_price(self):
        return self._price

    def check_values(self, amount_needed):
        return self._values >= amount_needed

    def clearstock(self, amount):
        self._values -= amount
        return "success"

    def restore_stock(self, amount):
        self._values += amount
        return "success"


class Popcorn(Goods):
    def __init__(self, name, values: int, price, flavor):
        super().__init__(name, values, price)
        self._flavor = flavor


class Drinks(Goods):
    def __init__(self, name, values: int, price, flavor):
        super().__init__(name, values, price)
        self._flavor = flavor


class Snack(Goods):
    def __init__(self, name, values: int, price):
        super().__init__(name, values, price)


class Coupon:
    def __init__(self, id, name):
        self.__coupon_id = id
        self.__name = name
        self._is_used = False

    @property
    def id(self):
        return self.__coupon_id

    def get_coupon_id(self):
        return self.__coupon_id

    def get_discount(self):
        return 0

    def update_status(self, status):
        self._is_used = (status != "Available")
        return "success"


class DiscountCoupon(Coupon):
    def __init__(self, id, name, discount):
        super().__init__(id, name)
        self.__discount = discount

    def get_discount(self):
        return self.__discount


class ExchangeCoupon(Coupon):
    def __init__(self, id, name, goods):
        super().__init__(id, name)
        self.__list_goods = goods

    def get_goods_list(self):
        return self.__list_goods
