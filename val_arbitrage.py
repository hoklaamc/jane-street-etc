from helpers import *

def val_arbitrage_buy(order_id, size, type, price):
    return create_buy_order(order_id, type, price, size)

def val_arbitrage_convert(order_id, sym, size):
    return create_convert_order(order_id, sym, size)

def val_arbitrage_sell(order_id, size, type, price):
    return create_sell_order(order_id, type, price, size)
