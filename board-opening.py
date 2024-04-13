from scipy.stats import norm 
from functools import partial
import math
import random
import tkinter as tk
import numpy as np

def black_scholes(S, K, T, r, sigma, option='call'):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = (math.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    
    if option == 'call':
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    if option == 'put':
        return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

def next_state(curr_state, states, transition_matrix):
    if curr_state == "eq":
        i = 0
    if curr_state == "lu":
        i = 1
    if curr_state == "ld":
        i = 2
    if curr_state == "hu":
        i = 3
    if curr_state == "hd":
        i = 4

    return np.random.choice(states, p = transition_matrix[i])

def get_impact(curr_state):
    if curr_state == "eq":
        impact = random.randint(1, 3)
    if curr_state == "lu" or curr_state == "ld":
        impact = random.randint(3, 6)
    if curr_state == "hu" or curr_state == "hd":
        impact = random.randint(5, 15)
    
    return impact

def get_liquidity(curr_state):
    if curr_state == "eq":
        volume = random.randint(5, 10) * 20
    if curr_state == "lu" or curr_state == "ld":
        volume = random.randint(3, 8) * 20
    if curr_state == "hu" or curr_state == "hd":
        volume = random.randint(1, 4) * 20
    return volume

def get_width(curr_state):
    if curr_state == "eq":
        width = random.randint(1, 3)
    if curr_state == "lu" or curr_state == "ld":
        width = random.randint(2, 5)
    if curr_state == "hu" or curr_state == "hd":
        width = random.randint(4, 10)
    return width

def amount_on_higher_levels(curr_state):
    if curr_state == "eq":
        ratio = random.randint(4, 8) / 10
    if curr_state == "lu" or curr_state == "ld":
        ratio = random.randint(3, 7) / 10
    if curr_state == "hu" or curr_state == "hd":
        ratio = random.randint(1, 4) / 10
    return ratio

if __name__ == "__main__":
    # precalcs and parameter deciding
    stock_price = random.randint(3000, 10000) / 100
    impacted_stock_price = stock_price
    rc = random.randint(3, 10) / 100

    # state 1: equilibrium point, have found 2 way flow
    # state 2: low impact up
    # state 3: low impact down
    # state 4: high impact up
    # state 5: high impact down
    states = ["eq", "lu", "ld", "hu", "hd"]
    initial_prob_vector = [0.1, 0.9 / 4, 0.9 / 4, 0.9 / 4, 0.9 / 4]
    transition_matrix = [
        [0.7, 0.3 / 4, 0.3 / 4, 0.3 / 4, 0.3 / 4], 
        [0.1 / 3, 0.6, 0.3, 0.1 / 3, 0.1 / 3], 
        [0.1 / 3, 0.3, 0.6, 0.1 / 3, 0.1 / 3], 
        [0.1 / 3, 0.1 / 3, 0.1 / 3, 0.7, 0.2], 
        [0.1 / 3, 0.1 / 3, 0.1 / 3, 0.2, 0.7]]
    curr_state = np.random.choice(states, p = initial_prob_vector)
    
    impact_per_hundred = get_impact(curr_state)
    stock_width = get_width(curr_state) / 100
    liquidity = [get_liquidity(curr_state), get_liquidity(curr_state)]
    uneven = random.randint(0, 1) / 100
    stock_market = [round(stock_price - stock_width, 2), round(stock_price + stock_width + uneven, 2)]

    mid_strike_index = int(round(stock_price / 5, 0))
    strikes = [5 * i for i in range(mid_strike_index - 2, mid_strike_index + 3)]
    dte = 30 / 365
    r = math.log(1 - rc/strikes[2]) / -dte
    sigma = random.randint(50, 70) / 100

    theo_calls = []
    theo_puts = []
    for strike in strikes:
        theo_calls.append(round(black_scholes(stock_price, strike, dte, r, sigma, option = "call"), 2))
        theo_puts.append(round(black_scholes(stock_price, strike, dte, r, sigma, option = "put"), 2))

    opening_info = []
    structures = ["b/w", "ps", "straddle", "cs", "p&s"]
    for i, struc in enumerate(structures):
        if struc == "b/w":
            opening_info.append((struc, round(theo_puts[i] + rc, 2)))
        elif struc == "p&s":
            opening_info.append((struc, round(theo_calls[i] - rc, 2)))
        elif struc == "cs":
            opening_info.append((struc, round(theo_calls[i - 1] - theo_calls[i], 2)))
        elif struc == "ps":
            opening_info.append((struc, round(theo_puts[i + 1] - theo_puts[i], 2)))
        elif struc == "straddle":
            opening_info.append((struc, round(theo_calls[i] + theo_puts[i], 2)))

    # opening the actual board (displaying)
    window = tk.Tk()
    stock_text = tk.Label(text="{} @ {}".format(stock_market[0], stock_market[1]))
    liquidity_text = tk.Label(text="{}x by {}x".format(liquidity[0], liquidity[1]))
    rc_text = tk.Label(text="r/c = {}".format(rc))
    stock_text.pack()
    liquidity_text.pack()
    rc_text.pack()
    call_theo_texts = []
    put_theo_texts = []
    starting_info_texts_l = []
    starting_info_texts_r = []

    theos_showing = False
    starting_info_showing = False

    def click_handler_l(struc, price, e):
        empty = e.widget["text"] == ""
        if empty and (struc == "p&s" or struc == "straddle" or struc == "cs"):
            e.widget["text"] = "{}: {}".format(struc, price)
        elif not empty:
            e.widget["text"] = ""

    def click_handler_r(struc, price, e):
        empty = e.widget["text"] == ""
        if empty and (struc == "b/w" or struc == "ps"):
            e.widget["text"] = "{}: {}".format(struc, price)
        elif not empty:
            e.widget["text"] = ""

    def show_theos():
        global theos_showing
        for put_theo_text, call_theo_text, put_theo, call_theo in zip(put_theo_texts, call_theo_texts, theo_puts, theo_calls):
            if not theos_showing:
                put_theo_text["text"] = str(put_theo)
                call_theo_text["text"] = str(call_theo)
            else:
                put_theo_text["text"] = ""
                call_theo_text["text"] = ""
        theos_showing = not theos_showing

    theos_button = tk.Button(text="Show theos", command=show_theos)

    for strike, info in zip(strikes, opening_info):
        struc, price = info
        strike_frame = tk.Frame()
        strike_frame.pack(pady=5)

        call_bid_entry = tk.Entry(master=strike_frame, width=5)
        call_theo_text = tk.Label(text="", master=strike_frame, width=5)
        call_offer_entry = tk.Entry(master=strike_frame, width=5)
        strike_text = tk.Label(master=strike_frame, text="{}".format(strike), width=5)
        put_bid_entry = tk.Entry(master=strike_frame, width=5)
        put_theo_text = tk.Label(text="", master=strike_frame, width=5)
        put_offer_entry = tk.Entry(master=strike_frame, width=5)
        given_info_l = tk.Label(master=strike_frame, text="", width=12)
        given_info_r = tk.Label(master=strike_frame, text="", width=12)

        given_info_l.pack(side=tk.LEFT)
        call_bid_entry.pack(side=tk.LEFT)
        call_theo_text.pack(side=tk.LEFT)
        call_offer_entry.pack(side=tk.LEFT)
        strike_text.pack(side=tk.LEFT)
        put_bid_entry.pack(side=tk.LEFT)
        put_theo_text.pack(side=tk.LEFT)
        put_offer_entry.pack(side=tk.LEFT)
        given_info_r.pack(side=tk.LEFT)

        call_theo_texts.append(call_theo_text)
        put_theo_texts.append(put_theo_text)
        starting_info_texts_l.append(given_info_l)
        starting_info_texts_r.append(given_info_r)

        if (struc == "p&s" or struc == "straddle" or struc == "cs"):
            given_info_l["text"] = "{}: {}".format(struc, price)
        else:
            given_info_r["text"] = "{}: {}".format(struc, price)

        given_info_l.bind("<Button-1>", partial(click_handler_l, struc, price))
        given_info_r.bind("<Button-1>", partial(click_handler_r, struc, price))


    theos_button.pack()

    # order handling and generation
    first_order = True
    resting_orders = []
    resting_orders_buttons = []
    cust_order = {"structure" : None, "strike" : None, "volume" : None, "direction" : None, "level" : None, "puts_over" : None }
    incoming_order_frame = tk.Frame()
    incoming_order_frame.pack()
    check_label = tk.Label(text="", master=incoming_order_frame)
    bid_entry = tk.Entry(master=incoming_order_frame, width=5)
    offer_entry = tk.Entry(master=incoming_order_frame, width=5)

    def execute_order():
        check_label["text"] = ""
        pass_order_button.pack_forget()
        execute_order_button.pack_forget()
        new_order_button.pack()

    def pass_order():
        resting_order_label = tk.Label()
        resting_order_label["text"] = "Cust is {} {} for {} of the {} {}".format(cust_order["direction"], cust_order["level"], cust_order["volume"], cust_order["strike"], cust_order["structure"])
        resting_orders.append(resting_order_label)

        def execute_resting():
            resting_order_label.pack_forget()
            resting_orders.remove(resting_order_label)
            execute_resting_button.pack_forget()
            resting_orders_buttons.remove(execute_resting_button)

        execute_resting_button = tk.Button(text="Execute", command=execute_resting)
        resting_orders_buttons.append(execute_resting_button)
        execute_order()

    pass_order_button = tk.Button(text="Pass", master=incoming_order_frame, command=pass_order)
    execute_order_button = tk.Button(text="Execute", master=incoming_order_frame, command=execute_order)

    def submit_market():
        global cust_order
        
        market = [float(bid_entry.get()), float(offer_entry.get())]
        bid_entry.delete(0, tk.END)
        offer_entry.delete(0, tk.END)

        bid_entry.pack_forget()
        offer_entry.pack_forget()
        submit_market_button.pack_forget()
        willingness = get_width(curr_state) / 100
        if cust_order["direction"] == "offer":
            willingness = -willingness

        if cust_order["structure"] == "combos" and not cust_order["puts_over"]:
            cust_order["level"] = round(impacted_stock_price + willingness - cust_order["strike"] + rc, 2)
        elif cust_order["structure"] == "combos":
            cust_order["level"] = round(- impacted_stock_price + willingness + cust_order["strike"] + rc, 2)
        elif cust_order["structure"] == "calls":
            bw = theo_puts[0] + rc
            cust_order["level"] = round(impacted_stock_price + willingness - cust_order["strike"] + bw, 2)
        elif cust_order["structure"] == "puts":
            ps = theo_calls[-1] - rc
            cust_order["level"] = round(- impacted_stock_price + willingness + cust_order["strike"] + ps, 2)

        print(market)
        print(cust_order)

        if cust_order["direction"] == "bid":
            if cust_order["level"] >= market[1]:
                check_label["text"] = "Customer lifts your offer"
                execute_order_button.pack(side=tk.LEFT)
            else:
                check_label["text"] = "Customer is bid {}".format(cust_order["level"])
                pass_order_button.pack(side=tk.LEFT)
                execute_order_button.pack(side=tk.LEFT)
        if cust_order["direction"] == "offer":
            if cust_order["level"] <= market[0]:
                check_label["text"] = "Customer hits your bid"
                execute_order_button.pack(side=tk.LEFT)
            else:
                check_label["text"] = "Customer is offered {}".format(cust_order["level"])
                pass_order_button.pack(side=tk.LEFT)
                execute_order_button.pack(side=tk.LEFT)

    submit_market_button = tk.Button(text="Submit Market", master=incoming_order_frame, command=submit_market)

    def new_order():
        global first_order
        global curr_state
        global cust_order
        global impact_per_hundred
        global impacted_stock_price

        print(impacted_stock_price)

        if not first_order:
            curr_state = next_state(curr_state, states, transition_matrix)
            impact_per_hundred = get_impact(curr_state)
        else:
            first_order = not first_order

        single_option = np.random.choice([True, False], p = [0.3, 0.7])
        if single_option and np.random.choice([True, False]):
            cust_order["structure"] = "calls"
            cust_order["strike"] = strikes[0]
            cust_order["puts_over"] = False
        elif single_option:
            cust_order["structure"] = "puts"
            cust_order["strike"] = strikes[-1]
            cust_order["puts_over"] = True
        else:
            cust_order["structure"] = "combos"
            cust_order["strike"] = random.choice(strikes)
            cust_order["puts_over"] = cust_order["strike"] > impacted_stock_price

        cust_order["volume"] = random.randint(1, 10) * 50
        check_label["text"] = "Can I get a market for {} of the {} {}".format(cust_order["volume"], cust_order["strike"], cust_order["structure"])
        upwards = curr_state == "lu" or curr_state == "hu" or (curr_state == "eq" and random.choice([True, False]))
        
        if upwards:
            impacted_stock_price += (impact_per_hundred / 100) * (cust_order["volume"] / 100)
            if cust_order["puts_over"]:
                cust_order["direction"] = "offer"
            else:
                cust_order["direction"] = "bid"
        else:
            impacted_stock_price -= (impact_per_hundred / 100) * (cust_order["volume"] / 100) 
            if cust_order["puts_over"]:
                cust_order["direction"] = "bid"
            else:
                cust_order["direction"] = "offer"

        bid_entry.pack(side=tk.LEFT)
        offer_entry.pack(side=tk.LEFT)
        submit_market_button.pack(side=tk.LEFT)
        new_order_button.pack_forget()

    new_order_button = tk.Button(text="New Order", master=incoming_order_frame, command=new_order)    

    new_order_button.pack(side=tk.LEFT)
    check_label.pack(side=tk.LEFT)

    def stock_test_buy_sell(buy):
        def stock_test():
            global stock_price
            global stock_width
            global liquidity
            global uneven
            global stock_market

            # if volume is sufficient, then refresh according to state
            stock_test_price = float(stock_test_price_entry.get())
            stock_test_volume = float(stock_test_volume_entry.get()) // 100
            stock_test_price_entry.delete(0, tk.END)
            stock_test_volume_entry.delete(0, tk.END)

            if (buy and (stock_test_price < stock_market[1])) or (not buy and (stock_test_price > stock_market[0])):
                stock_test_feedback["text"] = "Filled on 0."
                return
            if (buy and stock_test_volume < liquidity[1]) or (not buy and stock_test_volume < liquidity[0]):
                stock_test_feedback["text"] = "Filled on {:,}.".format(stock_test_volume * 100)
                if (buy and stock_test_volume < liquidity[1]):
                    liquidity[1] -= stock_test_volume
                if (not buy and stock_test_volume < liquidity[0]):
                    liquidity[0] -= stock_test_volume
                liquidity_text["text"] = "{}x by {}x".format(liquidity[0], liquidity[1])
                return
            
            if buy:
                diff = (stock_test_price - (stock_price + stock_width)) * 100
                filled_amt = round(amount_on_higher_levels(curr_state) * liquidity[1] * diff, - 1) + liquidity[1]
            else:
                diff = ((stock_price - stock_width) - stock_test_price) * 100
                filled_amt = round(amount_on_higher_levels(curr_state) * liquidity[0] * diff, - 1) + liquidity[0]
            filled_amt = min(filled_amt, stock_test_volume)
            stock_test_feedback["text"] = "Filled on {:,}.".format(filled_amt * 100)
            
            stock_price = impacted_stock_price
            stock_width = get_width(curr_state) / 100
            liquidity = [get_liquidity(curr_state), get_liquidity(curr_state)]
            uneven = random.randint(0, 1) / 100
            stock_market = [round(stock_price - stock_width, 2), round(stock_price + stock_width + uneven, 2)]
            stock_text["text"] = "{} @ {}".format(stock_market[0], stock_market[1])
            liquidity_text["text"] = "{}x by {}x".format(liquidity[0], liquidity[1])

        return stock_test

    stock_test_frame = tk.Frame()
    stock_test_frame.pack()
    stock_test_price_label = tk.Label(text="Price:", master=stock_test_frame)
    stock_test_price_entry = tk.Entry(master=stock_test_frame)
    stock_test_volume_label = tk.Label(text="Volume:", master=stock_test_frame)
    stock_test_volume_entry = tk.Entry(master=stock_test_frame)
    stock_test_bid_button = tk.Button(text="Buy Stock", master=stock_test_frame, command=stock_test_buy_sell(True))
    stock_test_offer_button = tk.Button(text="Sell Stock", master=stock_test_frame, command=stock_test_buy_sell(False))
    stock_test_price_label.pack(side=tk.LEFT)
    stock_test_price_entry.pack(side=tk.LEFT)
    stock_test_volume_label.pack(side=tk.LEFT)
    stock_test_volume_entry.pack(side=tk.LEFT)
    stock_test_bid_button.pack(side=tk.LEFT)
    stock_test_offer_button.pack(side=tk.LEFT)
    stock_test_feedback = tk.Label(text="")
    stock_test_feedback.pack()

    resting_orders_showing = False
    def show_resting():
        global resting_orders_showing

        for label, button in zip(resting_orders, resting_orders_buttons):
            if not resting_orders_showing:
                label.pack()
                button.pack()
            else:
                label.pack_forget()
                button.pack_forget()
        resting_orders_showing = not resting_orders_showing

    resting_orders_button = tk.Button(text="Show resting orders", command=show_resting)
    resting_orders_button.pack()


    window.mainloop()