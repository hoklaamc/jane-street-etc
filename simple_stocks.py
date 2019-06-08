from helpers import *
import globals

def get_highest_price(arr):
    prices = []
    for i in range(len(arr)):
        prices.append(arr[i][0])
    highest = max(prices)
    return highest

def get_lowest_price(arr):
    prices = []
    for i in range(len(arr)):
        prices.append(arr[i][0])
    lowest = min(prices)
    return lowest

def simple_stocks_trade(exchange):
    prices_paid = []
    ms_reply = {}

    while True:
        # Get prices of MS
        while True:
            reply = read_from_exchange(exchange)
            if (reply["type"] == "book" and reply["symbol"] == "GS"):
                ms_reply = reply
                break
        hbp = get_highest_price(reply["buy"]) + 1
        # Create buy order
        buy_order = create_buy_order(globals.next_order_id, "GS", hbp, 1)
        write_to_exchange(exchange, buy_order)
        # Wait for ack
        while True:
            ack_reply = read_from_exchange(exchange)
            if (ack_reply["type"] == "ack" and ack_reply["order_id"] == buy_order["order_id"]):
                print_reply(ack_reply)
                break
        # Wait for fill
        globals.next_order_id = globals.next_order_id + 1
        while True:
            fill_reply = read_from_exchange(exchange)
            if (fill_reply["type"] == "fill" and fill_reply["order_id"] == buy_order["order_id"]):
                print_reply(fill_reply)
                break
        prices_paid.append(hbp)
        
        average_buy_price = reduce(lambda a, b: a + b, prices_paid) / len(prices_paid)
        lsp = get_lowest_price(reply["sell"]) - 1
        sell_order = create_sell_order(globals.next_order_id, "GS", lsp, 1)
        write_to_exchange(exchange, sell_order)
        while True:
            ack_reply = read_from_exchange(exchange)
            if (ack_reply["type"] == "ack" and ack_reply["order_id"] == sell_order["order_id"]):
                print_reply(ack_reply)
                break
        globals.next_order_id = globals.next_order_id + 1
        # Wait for fill
        while True:
            fill_reply = read_from_exchange(exchange)
            if (fill_reply["type"] == "fill" and fill_reply["order_id"] == sell_order["order_id"]):
                print_reply(fill_reply)
                break

    # while True:
    #     if (exchange.closed):
    #         print("Exchange closed")
    #         return
        
    #     # 
    #     # Create buy order
    #     buy_order = simple_bond_buy(globals.next_order_id, 1)
    #     globals.next_order_id = globals.next_order_id + 1
    #     write_to_exchange(exchange, buy_order)

    #     # Wait for ack
    #     while True:
    #         ack_reply = read_from_exchange(exchange)
    #         if (ack_reply["type"] == "ack" and ack_reply["order_id"] == buy_order["order_id"]):
    #             print_reply(ack_reply)
    #             break
    #     # Wait for fill
    #     while True:
    #         fill_reply = read_from_exchange(exchange)
    #         if (fill_reply["type"] == "fill" and fill_reply["order_id"] == buy_order["order_id"]):
    #             print_reply(fill_reply)
    #             break

    #     # Create sell order
    #     sell_order = simple_bond_sell(globals.next_order_id, 1)
    #     globals.next_order_id = globals.next_order_id + 1
        
    #     write_to_exchange(exchange, sell_order)

    #     # Wait for ack
    #     while True:
    #         ack_reply = read_from_exchange(exchange)
    #         if (ack_reply["type"] == "ack" and ack_reply["order_id"] == sell_order["order_id"]):
    #             print_reply(ack_reply)
    #             break
    #     # Wait for fill
    #     while True:
    #         fill_reply = read_from_exchange(exchange)
    #         if (fill_reply["type"] == "fill" and fill_reply["order_id"] == sell_order["order_id"]):
    #             print_reply(fill_reply)
    #             break