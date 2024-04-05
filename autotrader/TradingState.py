from datamodel import *
import json
from typing import *

class TradingState(object):    
    def __init__(self):
        self.orderbook_data: Dict[str, Orderbook]= {}

        self.product_updates: Dict[str, List[Update]] = {}
        self.product_settlements: Dict[str, List[Settlement]] = {}

        self.positions  = {}

        self.products: List[str] = []
        self.product_details: Dict[str, ProductDetails] = {}

    # takes in a json
    def update_orderbook(self, update):
        # book = update['book']
        book = json.loads(update['book'])
        bids = [OrderbookItem(bid['quantity'], bid['price']) for bid in book['bids']]
        asks = [OrderbookItem(ask['quantity'], ask['price']) for ask in book['asks']]

        orderbook = Orderbook(update['product_id'], bids, asks)
        self.orderbook_data[update['product_id']] = orderbook
    
    def add_product_update(self, update):
        update = Update(update['product_id'], update['update'])
        
        if update.product_id not in self.product_updates:
            self.product_updates[update.product_id] = []
        
        self.product_updates[update.product_id].append(update)
    
    def add_product_settlement(self, settlement):
        settlement = Settlement(settlement['product_id'], settlement['price'])
        
        if settlement.product_id not in self.product_settlements:
            self.product_settlements[settlement.product_id] = []
        
        self.product_settlements[settlement.product_id].append(settlement)
    
    def update_product_position(self, product_id, positions):
        if product_id not in self.positions:
            self.positions[product_id] = []
            
        self.positions[product_id] = positions['open_positions']
    
    def update_product_list(self, product_list):
        if product_list:
            self.products = product_list.split(',')
        else:
            self.products = []

    def update_product_details(self, product_details):
        for product_id in product_details:
            product = product_details[product_id]
            self.product_details[product_id] = ProductDetails(product_id, product['product_type'], product['strike_price'], product['updates'], product['asset_class'], product['asset_information'])

            # add empty orderbook for any that don't exist
            if product_id not in self.orderbook_data:
                self.orderbook_data[product_id] = Orderbook(product_id, [], [])