#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
from helpers import *
from simple_bond import *

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="HAT"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = False

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

def main():
    exchange = connect()
    next_order_id = 1
    
    # Handshake
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    print_reply(hello_from_exchange)
    
    while True:
        if (exchange.closed):
            print("Exchange closed")
            break
        # Create buy order
        buy_order = simple_bond_buy(next_order_id, 1)
        next_order_id = next_order_id + 1
        write_to_exchange(exchange, buy_order)

        # Wait for ack
        while True:
            ack_reply = read_from_exchange(exchange)
            if (ack_reply["type"] == "ack" and ack_reply["order_id"] == buy_order["order_id"]):
                print_reply(ack_reply)
                break
        # Wait for fill
        while True:
            fill_reply = read_from_exchange(exchange)
            if (fill_reply["type"] == "fill" and fill_reply["order_id"] == buy_order["order_id"]):
                print_reply(fill_reply)
                break

        # Create sell order
        sell_order = simple_bond_sell(next_order_id, 1)
        next_order_id = next_order_id + 1
        write_to_exchange(exchange, sell_order)

        # Wait for ack
        while True:
            ack_reply = read_from_exchange(exchange)
            if (ack_reply["type"] == "ack" and ack_reply["order_id"] == sell_order["order_id"]):
                print_reply(ack_reply)
                break
        # Wait for fill
        while True:
            fill_reply = read_from_exchange(exchange)
            if (fill_reply["type"] == "fill" and fill_reply["order_id"] == sell_order["order_id"]):
                print_reply(fill_reply)
                break


if __name__ == "__main__":
    main()
