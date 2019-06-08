def print_reply(exchange_reply):
    print("The exchange replied:", exchange_reply)

def create_buy_order(id, sym, price, size):
    return {"type": "add", "order_id": id, "symbol": sym, "dir": "BUY", "price": price, "size": size}

def create_sell_order(id, sym, price, size):
    return {"type": "add", "order_id": id, "symbol": sym, "dir": "SELL", "price": price, "size": size}
