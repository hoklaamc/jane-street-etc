from helpers import *
from uuid import uuid4

bond_fair = 1000

def bond_pennying_buy(order_id, size):
    return create_buy_order(order_id, "BOND", bond_fair - 1, size)
    
def bond_pennying_sell(order_id, size):
    return create_sell_order(order_id, "BOND", bond_fair + 1, size)