import socket
import json

# replace REPLACEME with your team name!
team_name="HAT"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

# ~~~~~============== MAIN LOOP ==============~~~~~

def print_reply(exchange_reply):
    print("The exchange replied:", exchange_reply)

def create_buy_order(id, sym, price, size):
    return {"type": "add", "order_id": id, "symbol": sym, "dir": "BUY", "price": price, "size": size}

def create_sell_order(id, sym, price, size):
    return {"type": "add", "order_id": id, "symbol": sym, "dir": "SELL", "price": price, "size": size}

def wait_for_ack(exchange, order_id):
    while True:
        ack_reply = read_from_exchange(exchange)
        if (ack_reply["type"] == "ack" and ack_reply["order_id"] == order_id):
            print_reply(ack_reply)
            return True