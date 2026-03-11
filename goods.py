from typing import Optional
from enums import GoodsType


class Goods:
    def __init__(self, name: str, values: int, price: float,
                 goods_type: GoodsType, flavor: str = None):
        self.__name       = name
        self.__values     = values
        self.__price      = price
        self.__goods_type = (goods_type if isinstance(goods_type, GoodsType)
                             else GoodsType.from_str(str(goods_type)))
        self.__flavor     = flavor

    @classmethod
    def create(cls, name: str, values: int, price: float,
               type_str: str, flavor: str = None) -> "Goods":
        return cls(name, values, price, GoodsType.from_str(type_str), flavor)

    @property
    def goods_type(self) -> GoodsType:
        return self.__goods_type

    @property
    def flavor(self) -> Optional[str]:
        return self.__flavor

    def get_name(self) -> str:
        return self.__name

    def get_price(self) -> float:
        return self.__price

    def check_values(self, amount_needed: int) -> bool:
        return self.__values >= amount_needed

    def clearstock(self, amount: int):
        self.__values -= amount
        return "success"

    def restore_stock(self, amount: int):
        self.__values += amount
        return "success"
