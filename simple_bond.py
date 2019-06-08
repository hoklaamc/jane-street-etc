from helpers import *
from uuid import uuid4
from bot import write_to_exchange, read_from_exchange
import globals



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

# ~~~~~~~~========== BOND VALUE =========~~~~~~~
bond_fair = 1000

def simple_bond_trade(exchange):
  while True:
        if (exchange.closed):
            print("Exchange closed")
            return
        # Create bulk buy order
        buy_order = simple_bond_buy(globals.next_order_id, 1)
        globals.next_order_id = globals.next_order_id + 1
        write_to_exchange(exchange, buy_order)

        # Wait for ack
        while True:
            ack_reply = read_from_exchange(exchange)
            if (ack_reply["type"] == "book" and (ack_reply["symbol"] == "VALBZ" or ack_reply["symbol"] == "VALE")):
                #print(fill_reply, '\n')
                globals.next_order_id += val_update(globals.next_order_id, exchange, ack_reply)
            if (ack_reply["type"] == "ack" and ack_reply["order_id"] == buy_order["order_id"]):
                print_reply(ack_reply)
                break
        # Wait for fill
        while True:
            fill_reply = read_from_exchange(exchange)
            if (fill_reply["type"] == "book" and (fill_reply["symbol"] == "VALBZ" or fill_reply["symbol"] == "VALE")):
                #print(fill_reply, '\n')
                globals.next_order_id += val_update(globals.next_order_id, exchange, fill_reply)
            if (fill_reply["type"] == "fill" and fill_reply["order_id"] == buy_order["order_id"]):
                print_reply(fill_reply)
                break

        # Create sell order
        sell_order = simple_bond_sell(globals.next_order_id, 1)
        globals.next_order_id = globals.next_order_id + 1
        write_to_exchange(exchange, sell_order)

        # Wait for ack
        while True:
            ack_reply = read_from_exchange(exchange)
            if (ack_reply["type"] == "book" and (ack_reply["symbol"] == "VALBZ" or ack_reply["symbol"] == "VALE")):
                #print(fill_reply, '\n')
                globals.next_order_id += val_update(globals.next_order_id, exchange, ack_reply)
            if (ack_reply["type"] == "ack" and ack_reply["order_id"] == sell_order["order_id"]):
                print_reply(ack_reply)
                break
        # Wait for fill
        while True:
            fill_reply = read_from_exchange(exchange)
            if (fill_reply["type"] == "book" and (fill_reply["symbol"] == "VALBZ" or fill_reply["symbol"] == "VALE")):
                #print(fill_reply, '\n')
                globals.next_order_id += val_update(globals.next_order_id, exchange, fill_reply)
            if (fill_reply["type"] == "fill" and fill_reply["order_id"] == sell_order["order_id"]):
                print_reply(fill_reply)
                break

def simple_bond_buy(order_id, size):
    return create_buy_order(order_id, "BOND", bond_fair - 1, size)

def simple_bond_sell(order_id, size):
    return create_sell_order(order_id, "BOND", bond_fair + 1, size)
