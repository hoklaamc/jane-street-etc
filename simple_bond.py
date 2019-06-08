from helpers import *
from uuid import uuid4
from val_arbitrage import *
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
    if (vale_sell != -1 and valbz_buy != -1 and (valbz_sell*10 < vale_buy*10 - 26)):
        #print("I am in the first of init looking to ", "buy balbz", '\n')
        buy_val_arb = val_arbitrage_buy(id, 5, "VALBZ", valbz_sell)
        write_to_exchange(exchange, buy_val_arb)
        while True:
            ack_reply = read_from_exchange(exchange)
            if (ack_reply["type"] == "ack" and ack_reply["order_id"] == buy_val_arb["order_id"]):
                print_reply(ack_reply)
                break
            elif (ack_reply["type"] == "reject"):
                return 0
        #print("I am in the first of init looking to ", "covert my stock", '\n')
        convert_val_arb = val_arbitrage_convert(id+1, "VALE", 5)
        write_to_exchange(exchange, convert_val_arb)
        #print("I am in the first of init looking to ", "sell vale", '\n')
        sell_val_arb = val_arbitrage_sell(id+2, 5, "VALE", vale_buy)
        write_to_exchange(exchange, sell_val_arb)
        while True:
            ack_reply = read_from_exchange(exchange)
            #print_reply(ack_reply)
            if (ack_reply["type"] == "ack" and ack_reply["order_id"] == sell_val_arb["order_id"]):
                #print_reply(ack_reply)
                break
        order_used = 3;

    if (valbz_sell != -1 and vale_buy != -1 and (vale_sell*10 < valbz_buy*10 - 26)):
        #print("I am in the first of init looking to ", "buy vale", '\n')
        buy_val_arb = val_arbitrage_buy(id, 5, "VALE", vale_sell)
        write_to_exchange(exchange, buy_val_arb)
        while True:
            ack_reply = read_from_exchange(exchange)
            #print_reply(ack_reply)
            if (ack_reply["type"] == "ack" and ack_reply["order_id"] == buy_val_arb["order_id"]):
                #print_reply(ack_reply)
                break
            elif (ack_reply["type"] == "reject"):
                return 0
        #print("I am in the first of init looking to ", "covert my stock", '\n')
        convert_val_arb = val_arbitrage_convert(id+1, "VALBZ", 5)
        write_to_exchange(exchange, convert_val_arb)
        #print("I am in the first of init looking to ", "sell valbz", '\n')
        sell_val_arb = val_arbitrage_sell(id+2, 5, "VALBZ", vale_buy)
        write_to_exchange(exchange, sell_val_arb)
        while True:
            ack_reply = read_from_exchange(exchange)
            #print_reply(ack_reply)
            if (ack_reply["type"] == "ack" and ack_reply["order_id"] == sell_val_arb["order_id"]):
                #print_reply(ack_reply)
                break
        order_used = 3;
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
        reponse = read_from_exchange(exchange)
        if (reponse["type"] == "book" and (reponse["symbol"] == "VALBZ" or reponse["symbol"] == "VALE")):
            #print(fill_reply, '\n')
            globals.next_order_id += val_update(globals.next_order_id, exchange, reponse)
