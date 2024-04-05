import websocket
import json
from Trader import Trader
from TradingState import TradingState
import requests
from dotenv import load_dotenv
from datamodel import *
import os
import logging

load_dotenv()
ENDPOINT_URL = os.environ.get('EXCHANGE_ENDPOINT_URL')
WEBSOCKET_URL = os.environ.get('EXCHANGE_WEBSOCKET_URL')

logging.basicConfig(filename='log.log', level=logging.DEBUG, format='%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s')

class ExchangeGateway:
    def __init__(self, trader: Trader):
        self.ws = websocket.WebSocket()
        self.trader = trader

        self.trading_state = TradingState()

    def receieve_json_response(self) -> dict:
        response = self.ws.recv()
        if response:
            print(json.loads(response))
            return json.loads(response)
        return None

    def establish_connection(self):
        print("--- ESTABLISHING CONNECTION WITH EXCHANGE ", WEBSOCKET_URL, "---")

        self.ws = websocket.WebSocket()
        self.ws.connect(WEBSOCKET_URL)

        print("--- CONNECTION ESTABLISHED ---")

        logging.log(logging.INFO, "Connection established")

        # initialize our trading state
        self.initialize_tradingstate()

        actions = {}

        while True:
            response = self.receieve_json_response()

            msg = response['message']
            msg_type = response['message_type']

            logging.debug(f"Message received: {msg_type}")

            if msg_type == 'trade':
                print("trade message received")
                print(msg)

            elif msg_type == 'productCreation':
                print("product creation message received")
                print(msg)

            elif msg_type == 'order':
                print("order message received")
                print(msg)

            elif msg_type == 'orderbook':
                print("orderbook message received")

                # update our TradingState orderbook
                orderbook_json = msg['Orderbook']
                self.trading_state.update_orderbook(orderbook_json)
                print('orderbook updated')

            elif msg_type == 'update':
                print("update message received")

                # update our TradingState updates
                update_json = msg['Update']
                self.trading_state.add_product_update(update_json)
                print('product update added')

            elif msg_type == 'settlement':
                print("settlement message received")

                # update our TradingState settlements
                settlement_json = msg['Settlement']
                self.trading_state.add_product_settlement(settlement_json)
                print('product settlement added')
            
            elif msg_type == 'tick':
                print("tick message received")
            
            else:
                print("received unknown message type")
                print(msg_type)

            # update products
            product_list = self.get_products()
            print('product_list', product_list)

            if product_list is not None:
                self.trading_state.update_product_list(product_list)

            detailed_products = self.get_products_details()
            print("detailed products")

            if detailed_products is not None:
                print('detailed products', detailed_products)
                self.trading_state.update_product_details(detailed_products)

            # run autotrader
            actions = self.trader.run(self.trading_state)

            print('actions', actions)

            # place / remove orders
            if 'orders' in actions:
                for product in actions['orders']:
                    for order in actions['orders'][product]:
                        self.place_trade(order)
                    
            if 'remove_orders' in actions:
                for product in actions['remove_orders']:
                    for delete_order in actions['remove_orders'][product]:
                        self.delete_order(delete_order, product)
                    
            # may be inefficient to get own positions every time. but code is here anyways
            for product in self.trading_state.products:
                open_positions = self.get_open_positions(product)
                print(open_positions)
                if open_positions is not None:
                    self.trading_state.update_product_position(product, open_positions)
            
    def place_trade(self, order: Order):
        try:
            trade_message = {
                "username": self.trader.username,
                "password": self.trader.password,
                "data": json.dumps(order.to_dict())
            }

            trade_message_json = json.dumps(trade_message)

            response = requests.post(ENDPOINT_URL + "/trade", data=trade_message_json, headers={"Content-Type": "application/json"})
            response.raise_for_status()

            print("response recevied")

            # Check the response from the server
            print(response.text)
        except Exception as e:
            print("Exception in place_trade", e)
            logging.log(logging.ERROR, e)

    def get_open_positions(self, product_id: str):
        try:
            open_positions_message = {
            "username": self.trader.username,
            "password": self.trader.password,
            "data": product_id
            }

            open_positions_message_json = json.dumps(open_positions_message)

            print("sending open positions reqeust")
            response = requests.post(ENDPOINT_URL + "/trader_position", data=open_positions_message_json, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            print("response recevied")
            
            return json.loads(response.text)
        except Exception as e:
            print("Exception in get_open_positions", e)
            logging.log(logging.ERROR, e)
            return None
    
    def delete_order(self, order_id: str, product_id: str):
        try:
            delete_order_data = {
                "order_id": order_id,
                "product_id": product_id,
                "trader_id": self.trader.username
            }

            delete_order_data_json = json.dumps(delete_order_data)

            delete_order_message = {
                "username": self.trader.username,
                "password": self.trader.password,
                "data": delete_order_data_json
            }
            
            delete_order_message_json = json.dumps(delete_order_message)
            print('delete order message json')
            print(delete_order_message_json)

            print("sending delete positions reqeust")

            response = requests.post(ENDPOINT_URL + "/delete", data=delete_order_message_json, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            print("response recevied")

        except Exception as e:
            print("Exception in delete_order", e)
            logging.log(logging.ERROR, e)

    def get_products(self):
        try:
            response = requests.get(ENDPOINT_URL + "/products")
            response.raise_for_status()

            print("getting products")
            print(response.text)

            return response.text
        except Exception as e:
            print("Exception in get_products", e)
            logging.log(logging.ERROR, e)
            return None

    def get_products_details(self):
        try:
            response = requests.get(ENDPOINT_URL + "/product_details")
            response.raise_for_status()

            print("getting products details")
            print(response.text)

            return json.loads(response.text)
        except Exception as e:
            print("Exception in get_products_details", e)
            logging.log(logging.ERROR, e)
            return None

    def initialize_tradingstate(self):
        # get products
        product_list = self.get_products()
        print('product_list', product_list)

        if product_list is not None:
            self.trading_state.update_product_list(product_list)

        detailed_products = self.get_products_details()
        print("detailed products")

        if detailed_products is not None:
            print('detailed products', detailed_products)
            self.trading_state.update_product_details(detailed_products)

        # get open positions for all products
        for product in self.trading_state.products:
            open_positions = self.get_open_positions(product)
            self.trading_state.update_product_position(product, open_positions)

def __main__():
    trader = Trader()
    eg = ExchangeGateway(trader)

    eg.establish_connection()

if __name__ == "__main__":
    __main__()