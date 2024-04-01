from scipy.stats import norm 
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
        impact = random.randint(50, 100) / 100
    if curr_state == "lu" or curr_state == "ld":
        impact = random.randint(100, 250) / 100
    if curr_state == "hu" or curr_state == "hd":
        impact = random.randint(250, 500) / 100
    
    return impact

def get_liquidity(curr_state):
    if curr_state == "eq":
        volume = random.randint(5, 10) * 20
    if curr_state == "lu" or curr_state == "ld":
        volume = random.randint(3, 8) * 20
    if curr_state == "hu" or curr_state == "hd":
        volume = random.randint(1, 5) * 20
    return volume

def get_width(curr_state):
    if curr_state == "eq":
        width = random.randint(1, 3)
    if curr_state == "lu" or curr_state == "ld":
        width = random.randint(2, 5)
    if curr_state == "hu" or curr_state == "hd":
        width = random.randint(4, 10)
    return width

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
    def show_starting():
        global starting_info_showing
        for given_info_l, given_info_r, info in zip(starting_info_texts_l, starting_info_texts_r, opening_info):
            struc, price = info
            if starting_info_showing:
                given_info_l["text"] = ""
                given_info_r["text"] = ""
            else:
                if struc == "p&s" or struc == "straddle" or struc == "cs":
                    given_info_l["text"] = "{}: {}".format(struc, price)
                    given_info_r["text"] = ""
                if struc == "b/w" or struc == "ps":
                    given_info_l["text"] = ""
                    given_info_r["text"] = "{}: {}".format(struc, price)
        starting_info_showing = not starting_info_showing

    theos_button = tk.Button(text="Show theos", command=show_theos)
    starting_info_button = tk.Button(text="Hide starting", command=show_starting)

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

    show_starting()
    starting_info_button.pack()
    theos_button.pack()

    # order handling and generation
    first_order = False
    resting_orders = []
    resting_orders_buttons = []
    cust_level = None
    cust_direction = None
    volume = None
    strike = None
    puts_over = None
    incoming_order_frame = tk.Frame()
    incoming_order_frame.pack()
    check_label = tk.Label(text="", master=incoming_order_frame)
    combo_bid_entry = tk.Entry(master=incoming_order_frame, width=5)
    combo_offer_entry = tk.Entry(master=incoming_order_frame, width=5)

    def execute_order():
        check_label["text"] = ""
        pass_order_button.pack_forget()
        execute_order_button.pack_forget()
        new_order_button.pack()

    def pass_order():
        resting_order_label = tk.Label()
        if (cust_direction == "bid" and not puts_over) or (cust_direction == "offer" and puts_over):
            resting_order_label["text"] = "Cust is bid {} for {} of the {} combos".format(cust_level, volume, strike)
        else:
            resting_order_label["text"] = "Cust offers {} of the {} combos at {}".format(volume, strike, cust_level)

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
        global cust_level
        global cust_direction
        global puts_over
        
        combo_market = [float(combo_bid_entry.get()), float(combo_offer_entry.get())]
        combo_bid_entry.delete(0, tk.END)
        combo_offer_entry.delete(0, tk.END)

        combo_bid_entry.pack_forget()
        combo_offer_entry.pack_forget()
        submit_market_button.pack_forget()
        willingness = random.randint(1, 5) / 100
        if cust_direction == "bid":
            cust_level = round(impacted_stock_price + willingness - strike + rc, 2)
        if cust_direction == "offer":
            cust_level = round(impacted_stock_price - willingness - strike + rc, 2)
        
        puts_over = cust_level < 0
        if puts_over:
            cust_level = - cust_level

        if (cust_direction == "bid" and not puts_over) or (cust_direction == "offer" and puts_over):
            if cust_level >= combo_market[1]:
                check_label["text"] = "Customer lifts your offer"
                execute_order_button.pack(side=tk.LEFT)
            else:
                check_label["text"] = "Customer is bid {}".format(cust_level)
                pass_order_button.pack(side=tk.LEFT)
                execute_order_button.pack(side=tk.LEFT)
        if (cust_direction == "offer" and not puts_over) or (cust_direction == "bid" and puts_over):
            if cust_level <= combo_market[0]:
                check_label["text"] = "Customer hits your bid"
                execute_order_button.pack(side=tk.LEFT)
            else:
                check_label["text"] = "Customer is offered {}".format(cust_level)
                pass_order_button.pack(side=tk.LEFT)
                execute_order_button.pack(side=tk.LEFT)

    submit_market_button = tk.Button(text="Submit Market", master=incoming_order_frame, command=submit_market)

    def new_order():
        global first_order
        global curr_state
        global cust_direction
        global impact_per_hundred
        global impacted_stock_price
        global volume
        global strike

        if not first_order:
            prev_state = curr_state
            curr_state = next_state(curr_state, states, transition_matrix)
            if curr_state != prev_state:
                impact_per_hundred = get_impact(curr_state)
        else:
            first_order = not first_order

        strike = random.choice(strikes)
        volume = random.randint(1, 10) * 50
        check_label["text"] = "Can I get a market for {} of the {} combos".format(volume, strike)

        if curr_state == "lu" or curr_state == "hu" or (curr_state == "eq" and random.choice([True, False])):
            impacted_stock_price += (impact_per_hundred / 100) * (volume / 100)
            cust_direction = "bid"       
        if curr_state == "ld" or curr_state == "hd" or curr_state == "eq":
            impacted_stock_price -= (impact_per_hundred / 100) * (volume / 100) 
            cust_direction = "offer"

        print(impacted_stock_price)

        combo_bid_entry.pack(side=tk.LEFT)
        combo_offer_entry.pack(side=tk.LEFT)
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
                stock_test_feedback["text"] = "Filled on {}.".format(stock_test_volume * 100)
                if (buy and stock_test_volume < liquidity[1]):
                    liquidity[1] -= stock_test_volume
                if (not buy and stock_test_volume < liquidity[0]):
                    liquidity[0] -= stock_test_volume
                liquidity_text["text"] = "{}x by {}x".format(liquidity[0], liquidity[1])
                return
            
            stock_price = impacted_stock_price
            stock_width = get_width(curr_state) / 100
            liquidity = [get_liquidity(curr_state), get_liquidity(curr_state)]
            uneven = random.randint(0, 1) / 100
            filled_amt = 

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