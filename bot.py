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
from bond_pennying import *
from val_arbitrage import *

# ~~~~~============== CONFIGURATION  ==============~~~~~
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

# ~~~~~============== CURRENT PRICE ==============~~~~~~

vale_sell = -1
valbz_sell = -1
vale_buy = -1
valbz_buy = -1
vale_total = 0
valbz_total = 0


# ~~~~~============== VAL Initiator ==============~~~~~~

def val_initiator(id, exchange):
    global vale_total
    global valbz_total
    order_used = 0
#    print("Vale sell: ", vale_sell, " and Valbz buy: ", valbz_buy);
#    print("Valbz sell: ", valbz_sell, " and Vale buy: ", vale_buy);
    if (vale_sell != -1 and valbz_buy != -1 and (vale_sell*5 > valbz_buy*5 + 10)):
        buy_val_arb = val_arbitrage_buy(id, 5, "VALBZ", valbz_buy)
        write_to_exchange(exchange, buy_val_arb)
        convert_val_arb = val_arbitrage_convert(id, "VALBZ", 5)
        write_to_exchange(exchange, convert_val_arb)
        sell_val_arb = val_arbitrage_sell(id+1, 5, "VALBZ", vale_sell)
        write_to_exchange(exchange, sell_val_arb)
        order_used = 2;
        print("Initiator: 1", '\n')

    if (valbz_sell != -1 and vale_buy != -1 and (valbz_sell*5 > vale_buy*5 + 10)):
        buy_val_arb = val_arbitrage_buy(id, 5, "VALE", vale_buy)
        write_to_exchange(exchange, buy_val_arb)
        convert_val_arb = val_arbitrage_convert(id, "VALE", 5)
        write_to_exchange(exchange, convert_val_arb)
        sell_val_arb = val_arbitrage_sell(id+1, 5, "VALE", vale_sell)
        write_to_exchange(exchange, sell_val_arb)
        order_used = 2;
        print("Initiator: 2", '\n')
    return order_used

def val_update(id, exchange, object):
    global vale_buy
    global vale_sell
    global valbz_buy
    global valbz_sell
    if (object["symbol"] == "VALBZ"):
        if object["buy"]:
            valbz_buy = object["buy"][0][0]
        if object["sell"]:
            valbz_sell = object["sell"][0][0]
        if not (object["sell"] and object["buy"]):
            return 0;
        #print("VALBZ BUY: ", object["buy"][0][0], " AND VALBZ SELL: ", object["sell"][0][0], '\n')
        return val_initiator(id, exchange)

    if (object["symbol"] == "VALE"):
        if object["buy"]:
            vale_buy = object["buy"][0][0]
        if object["sell"]:
            vale_sell = object["sell"][0][0]
        if not (object["sell"] and object["buy"]):
            return 0;
        #print("VALE BUY: ", object["buy"][0][0], " AND VALE SELL: ", object["sell"][0][0], '\n')
        return val_initiator(id, exchange)
    return 0

# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()
    next_order_id = 1

    # Handshake
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    print_reply(hello_from_exchange)

    while True:
        # Create buy order
        buy_order = bond_pennying_buy(next_order_id, 1)
        next_order_id = next_order_id + 1
        write_to_exchange(exchange, buy_order)

        # Wait for ack
        while True:
            ack_reply = read_from_exchange(exchange)
            if (ack_reply["type"] == "book" and (ack_reply["symbol"] == "VALBZ" or ack_reply["symbol"] == "VALE")):
                #print(ack_reply, '\n')
                next_order_id += val_update(next_order_id, exchange, ack_reply)
            if (ack_reply["type"] == "ack" and ack_reply["order_id"] == buy_order["order_id"]):
                print_reply(ack_reply)
                break
        # Wait for fill
        while True:
            fill_reply = read_from_exchange(exchange)
            if (fill_reply["type"] == "book" and (fill_reply["symbol"] == "VALBZ" or fill_reply["symbol"] == "VALE")):
                #print(fill_reply, '\n')
                next_order_id += val_update(next_order_id, exchange, fill_reply)
            if (fill_reply["type"] == "fill" and fill_reply["order_id"] == buy_order["order_id"]):
                print_reply(fill_reply)
                break

        # Create sell order
        sell_order = bond_pennying_sell(next_order_id, 1)
        next_order_id = next_order_id + 1
        write_to_exchange(exchange, sell_order)

        # Wait for ack
        while True:
            ack_reply = read_from_exchange(exchange)
            if (ack_reply["type"] == "book" and (ack_reply["symbol"] == "VALBZ" or ack_reply["symbol"] == "VALE")):
                # print(ack_reply, '\n')
                next_order_id += val_update(next_order_id, exchange, ack_reply)
            if (ack_reply["type"] == "ack" and ack_reply["order_id"] == sell_order["order_id"]):
                print_reply(ack_reply)
                break
        # Wait for fill
        while True:
            fill_reply = read_from_exchange(exchange)
            if (fill_reply["type"] == "book" and (fill_reply["symbol"] == "VALBZ" or fill_reply["symbol"] == "VALE")):
                #print(fill_reply, '\n')
                next_order_id += val_update(next_order_id, exchange, fill_reply)
            if (fill_reply["type"] == "fill" and fill_reply["order_id"] == sell_order["order_id"]):
                print_reply(fill_reply)
                break


if __name__ == "__main__":
    main()
