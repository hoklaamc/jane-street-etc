from helpers import *
from uuid import uuid4

bond_fair = 1000

def simple_bond_buy(order_id, size):
    return create_buy_order(order_id, "BOND", bond_fair - 1, size)
    
def simple_bond_sell(order_id, size):
    return create_sell_order(order_id, "BOND", bond_fair + 1, size)