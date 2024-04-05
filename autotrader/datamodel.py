from typing import *
from enum import Enum

class OrderType(Enum):
    MARKET = 0
    LIMIT = 1

class Side(Enum):
    BUY = 0
    SELL = 1

class OrderbookItem:
    def __init__(self, quantity: float, price: float):
        self.quantity = quantity
        self.price = price

    def __str__(self):
        return f"Price: {self.price}, Quantity: {self.quantity}"

    def __repr__(self):
        return self.__str__()

class Orderbook:
    def __init__(self, product_id: str, bids: List[OrderbookItem], asks: List[OrderbookItem]):
        # each bid should have a quanitty and price
        self.product_id = product_id
        self.bids = bids
        self.asks = asks

    def __str__(self):
        return f"Orderbook for Product ID: {self.product_id}\nBids: {self.bids}\nAsks: {self.asks}"

    def __repr__(self):
        return self.__str__()

    
class Order:
    def __init__(self, product_id: str, volume: float, price: float, side: Side, order_type: OrderType, trader: str):
        self.product_id = product_id
        self.price = price
        self.volume = volume
        self.side = side
        self.order_type = order_type   
        self.trader = trader

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "volume": self.volume,
            "price": self.price,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "trader": self.trader
        }    

    def __str__(self):
        return f"Product ID: {self.product_id}, Volume: {self.volume}, Price: {self.price}, Side: {self.side}, Order Type: {self.order_type}, Trader: {self.trader}"
    
    def __repr__(self):
        return self.__str__()

class Update:
    def __init__(self, product_id: str, update):
        self.product_id = product_id
        self.update = update
    
    def __str__(self):
        return f"Product ID: {self.product_id}, Update: {self.update}"

    def __repr__(self):
        return self.__str__()
    

class Settlement:
    def __init__(self, product_id: str, price: float):
        self.product_id = product_id
        self.price = price
    
    def __str__(self):
        return f"Product ID: {self.product_id}, Price: {self.price}"
    
    def __repr__(self):
        return self.__str__()
    
class ProductDetails:
    def __init__(self, product_id: str, product_type: str, strike_price: float, updates: float, asset_class: str, asset_information: str):
        self.product_id = product_id
        self.product_type = product_type
        self.strike_price = strike_price
        self.updates = updates
        self.asset_class = asset_class
        self.asset_information = asset_information
    
    def __str__(self):
        return f"Product ID: {self.product_id}, Product Type: {self.product_type}, Strike Price: {self.strike_price}, Updates: {self.updates}, Asset Class: {self.asset_class}, Asset Information: {self.asset_information}"
    
    def __repr__(self):
        return self.__str__()