## AutoTrader README

## Basic Usage

There are four files for running the autotrader, but for players, they only need to update the code in Trader.py. At a high level, TradingState.py and datamodel.py provide the data structures that the Trader will be dealing with, and the ExchangeGateway abstracts the details of connecting to the exchange, including the websocket for updates and calling endpoints for taking actions.

## Running the AutoTrader

To run and test out the sample AutoTrader, take the following steps:

1. Run the exchange locally using `cargo run`
2. Add a new trader that matches the username and password set in the Trader class. By default, the username is `autotrader` and the password is `123`
3. Run the AutoTrader by running ExchangeGateway.py
4. Create a new product, and try placing an order. The AutoTrader should place orders on both sides whenever there are no orders available, and place orders when the prices are above / below fair value

## Trader Class Overview

The Trader class is the only class that needs to be edited by the player, and the only function they are required to implement is the run function. The run function is required to return a dictionary with keys "orders" and "remove_orders" for orders they would like to place, and remove respectively.

Players will also need to include their trader username / password under the Trader init function.

```python
class Trader:
    def __init__(self):
        self.username = "lucas"
        self.password = "123"

    def run(self, tradingState: TradingState):
        
        result = {
            # dict of order to place {product_id: [Order]}
            "orders": {},
            # dict of orders to remove {product_id: []}
            "remove_orders": {}
        }

        for product in tradingState.orderbook_data:
            orders: List[Order] = []

            # place a trade on the first ask available
            if len(tradingState.orderbook_data[product].asks) > 0:
                orders.append(Order(product, 1, tradingState.orderbook_data[product].asks[0]['price'], 0, 1, self.username))
            
            result["orders"][product] = orders
        
        return result
```

This example Trader implementation simply looks through all available products in the orderbook, and places a sell if there is an available ask.

## Trading State Class Overview

The TradingState class contains all of the information necessary for the algorithmic trader to place trades. 

```python
class TradingState(object):    
    def __init__(self):
        self.orderbook_data: Dict[str, Orderbook]= {}
        self.product_updates: Dict[str, List[Update]] = {}
        self.product_settlements: Dict[str, List[Settlement]] = {}
        self.positions  = {}
        self.products: List[str] = []
        self.product_details: Dict[str, ProductDetails] = {}
```

Each dictionary has product as the key and its related data as its value. For example, orderbook_data['future_0'] would provide lists of asks and bids. Similarly, product updates contains a list of all updates sent by the exchange, settlements contains settlements sent out by the exchange, and positions represents your own positions on any products. 

The classes of each data model are contained in the datamodel.py file as follows below.

## Data Model Classes Overview

This file contains the models for various classes such as Orderbooks, Orders, Updates, and Settlements. The goal of this is to simplify the development experience for players such that the ExchangeGateway and TradingState will handle all of the conversion to / from json objects for them.

```python
class OrderbookItem:
    def __init__(self, quantity: float, price: float):
        self.quantity = quantity
        self.price = price

class Orderbook:
    def __init__(self, product_id: str, bids: List[OrderbookItem], asks: List[OrderbookItem]):
        # each bid should have a quanitty and price
        self.product_id = product_id
        self.bids = bids
        self.asks = asks

class Order:
    def __init__(self, product_id: str, volume: float, price: float, side: Side, order_type: OrderType, trader: str):
        self.product_id = product_id
        self.price = price
        self.volume = volume
        self.side = side
        self.order_type = order_type   
        self.trader = trader

class Update:
    def __init__(self, product_id: str, update):
        self.product_id = product_id
        self.update = update
    
class Settlement:
    def __init__(self, product_id: str, price: float):
        self.product_id = product_id
        self.price = price
    
class ProductDetails:
    def __init__(self, product_id: str, product_type: str, strike_price: float, updates: float, asset_class: str, asset_information: str):
        self.product_id = product_id
        self.product_type = product_type
        self.strike_price = strike_price
        self.updates = updates
        self.asset_class = asset_class
        self.asset_information = asset_information
```

These datamodels are used in the TradingState class, and when you are trying to access data in Trader, refer back to these models.

## Exchange Gateway Class Overview

The ExchangeGateway is the interface with the exchange and it doesn't need to be edited. Nevertheless, if you'd really like to edit it, please do so at your own risk. 

At a high level overview, the ExchangeGateway establishes a websocket connection with the exchange in order to receive messages. These occur whenever an event such as a trade, settlement, or a new product being added, and can be identified by their msg_type. Each case has already been handled, so if you'd like you can plce your code in there (or don't). 

The current implementation runs your Trader implementation whenever there is a new message. Every 5 seconds, there is also a tick message that is sent out, which allows your trader to run even if other traders are inactive. 

All of the functions needed for calling the exchange endpoints are defined below the establish_connection function, and should include all of the necessary endpoints for getting and sending information to the exchange. These functions tend to return the result in a JSON object, which is then handled by functions within the TradingState class.

## Strategy

The AutoTrader is left intentionally vague so you can express your own creativity and skill. However, for some guidance you may want to look at the example provided in the Trader class which places orders around the fair price, and also takes orders that are a certain amount above or below the fair price. 

To start off with, you can keep this same strategy, but adjust what the fair value will be. By looking at the product_details, you can determine what asset_class it is (dice, cards, etc.), and using that information evaluate what the fair price might be. 

This is just a starting point, and remember that you have full control over your bot so be as creative as you want!