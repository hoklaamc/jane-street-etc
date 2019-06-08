#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import globals

from helpers import *
from simple_bond import *
from simple_stocks import *

# ~~~~~============== CONFIGURATION  ==============~~~~~

globals.init()

def main():
    exchange = connect()
    
    # Handshake
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    print_reply(hello_from_exchange)
    
    simple_stocks_trade(exchange)


if __name__ == "__main__":
    main()
