import TradingState
from datamodel import *
from typing import List

class Trader:
    def __init__(self):
        self.username = "autotrader"
        self.password = "123"

    def run(self, tradingState: TradingState):
        # dict of order to place {product_id: [Order]}
        result = {
            "orders": {},
            "remove_orders": {}
        }
        
        print("\n--- RUNNING TRADER --- ")
        print("\n--- TRADING STATE INFO --- ")
        print('orderbook data', tradingState.orderbook_data)
        print('product updates', tradingState.product_updates)
        print('product settlements', tradingState.product_settlements)
        print('open positions', tradingState.positions)
        print('product details', tradingState.product_details)
        print("---------")

        # simple market making strat
        FAIR_PRICE = 100

        for product in tradingState.products:
            orders: List[Order] = []

            if tradingState.product_details[product].asset_class == 'dice' and tradingState.product_details[product].product_type == 'FUTURE':
                EV = tradingState.product_details[product].updates*3.5
            else:
                EV = 100

            if product in tradingState.orderbook_data:
                print("orderbook data for product", tradingState.orderbook_data[product])
                print("fair price for product", FAIR_PRICE)
                if len(tradingState.orderbook_data[product].asks) == 0:
                    orders.append(Order(product_id=product, volume=1, price=FAIR_PRICE + 5, side=Side.SELL, order_type=OrderType.LIMIT, trader=self.username))
                else:
                    for order in tradingState.orderbook_data[product].asks:
                        if order.price < FAIR_PRICE-5:
                            print("order found to buy", order.price)
                            orders.append(Order(product_id=product, volume=order.quantity, price=order.price, side=Side.BUY, order_type=OrderType.LIMIT, trader=self.username))

                if len(tradingState.orderbook_data[product].bids) == 0:
                    orders.append(Order(product_id=product, volume=1, price=FAIR_PRICE - 5, side=Side.BUY, order_type=OrderType.LIMIT, trader=self.username))
                else:
                    for order in tradingState.orderbook_data[product].bids:
                        if order.price > FAIR_PRICE+5:
                            print("order found to sell", order.price)
                            orders.append(Order(product_id=product, volume=order.quantity, price=order.price, side=Side.SELL, order_type=OrderType.LIMIT, trader=self.username))

                result["orders"][product] = orders
            else:
                print("no orderbook data for product", product)
        print("--- TRADER FINISHED RUNNING ---\n")
        return result