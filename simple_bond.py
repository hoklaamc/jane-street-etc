from helpers import *
import globals

bond_fair = 1000

def simple_bond_trade(exchange):
  while True:
        if (exchange.closed):
            print("Exchange closed")
            return
        # Create bulk buy order
        buy_order = simple_bond_buy(globals.next_order_id, 20)
        globals.next_order_id = globals.next_order_id + 1
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
        sell_order = simple_bond_sell(globals.next_order_id, 20)
        globals.next_order_id = globals.next_order_id + 1
        
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

def simple_bond_buy(order_id, size):
    return create_buy_order(order_id, "BOND", bond_fair - 1, size)
    
def simple_bond_sell(order_id, size):
    return create_sell_order(order_id, "BOND", bond_fair + 1, size)