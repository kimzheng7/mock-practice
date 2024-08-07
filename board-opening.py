from scipy.stats import norm 
from functools import partial
import math
import random
import tkinter as tk
import numpy as np
import pyttsx3
import threading

def black_scholes(S, K, T, r, sigma, option='call'):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = (math.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    
    if option == 'call':
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    if option == 'put':
        return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

def black_scholes_delta(S, K, T, r, sigma, option="call"):
    d1 = (math.log(S/K) + (r + sigma**2/2)*T) / (sigma*math.sqrt(T))
    if option == "call":
        delta_calc = norm.cdf(d1, 0, 1)
    elif option == "put":
        delta_calc = -norm.cdf(-d1, 0, 1)
    return delta_calc

def black_scholes_vega(S, K, T, r, sigma, option="call"):
    d1 = (math.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)

    vega_calc = S * norm.pdf(d1, 0, 1) * np.sqrt(T)
    return vega_calc * 0.01

def get_middle_strike_with_indices(strikes):
    strike_indices = list(sorted(np.random.choice([1, 2, 3], 2, replace = False)))
    return (strikes[strike_indices[0]], strikes[strike_indices[1]]), strike_indices

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

def get_normal_order_size():
    return random.randint(4, 10) * 50

def get_impact(curr_state):
    if curr_state == "eq":
        impact = random.randint(0, 2)
    if curr_state == "lu" or curr_state == "ld":
        impact = random.randint(2, 5)
    if curr_state == "hu" or curr_state == "hd":
        impact = random.randint(8, 15)
    
    return impact

def get_straddle_impact(curr_state):
    if curr_state == "eq":
        impact = random.randint(0, 5)
    if curr_state == "lu" or curr_state == "ld":
        impact = random.randint(5, 12)
    if curr_state == "hu" or curr_state == "hd":
        impact = random.randint(12, 20)
    
    return impact


def get_liquidity(curr_stock_liquidity):
    if curr_stock_liquidity == "l":
        volume = random.randint(5, 10) * 20
    if curr_stock_liquidity == "m":
        volume = random.randint(3, 8) * 20
    if curr_stock_liquidity == "h":
        volume = random.randint(1, 4) * 20
    return volume

def get_width(curr_stock_liquidity):
    if curr_stock_liquidity == "l":
        width = random.randint(1, 3)
    if curr_stock_liquidity == "m":
        width = random.randint(2, 5)
    if curr_stock_liquidity == "h":
        width = random.randint(4, 10)
    return width

def amount_on_higher_levels(curr_stock_liquidity, diff_1, diff_2):
    # essentially - you are trying to sus out the amount of impact there has been so you test stock
    # if stock fills are thin, then the impact may be way larger since you havent any disconfirming evidence that you've moved stock enough
    # whereas if stock fills are full, then the impact is around what you observe, since you've run into that disconfirming evidence that you're paying too much
    liquidity_top_to_bottom = [get_liquidity(curr_stock_liquidity) * 5]
    for i in range(int(diff_2) - 1):
        liquidity_top_to_bottom.append(liquidity_top_to_bottom[-1] ** (1/2))

    if diff_1 > diff_2:
        return np.inf
    else:
        return sum(liquidity_top_to_bottom[-int(diff_1):])

if __name__ == "__main__":
    speech = pyttsx3.init()
    with_text = True

    # Section 1: Parameter deciding
    stock_price = random.randint(5000, 8000) / 100
    ref_initial_stock = stock_price
    impacted_stock_price = stock_price
    rc = random.randint(3, 10) / 100

    # state 1: equilibrium point, have found 2 way flow
    # state 2: low impact up
    # state 3: low impact down
    # state 4: high impact up
    # state 5: high impact down
    states = ["eq", "lu", "ld", "hu", "hd"]
    initial_prob_vector = [0.3, 0.25, 0.25, 0.1, 0.1]
    transition_matrix = [
        [0.7, 0.3 / 4, 0.3 / 4, 0.3 / 4, 0.3 / 4], 
        [0.1 / 3, 0.6, 0.3, 0.1 / 3, 0.1 / 3], 
        [0.1 / 3, 0.3, 0.6, 0.1 / 3, 0.1 / 3], 
        [0.1 / 3, 0.1 / 3, 0.1 / 3, 0.7, 0.2], 
        [0.1 / 3, 0.1 / 3, 0.1 / 3, 0.2, 0.7]]
    curr_state = "eq"
    # curr_state = np.random.choice(states, p = initial_prob_vector)
    curr_stock_liquidity = "l"
    
    impact_per_normal = get_impact(curr_state)
    normal_order_size = get_normal_order_size()
    stock_width = get_width(curr_stock_liquidity) / 100
    liquidity = [get_liquidity(curr_stock_liquidity), get_liquidity(curr_stock_liquidity)]
    uneven = random.randint(0, 1) / 100
    stock_market = [round(stock_price - stock_width, 2), round(stock_price + stock_width + uneven, 2)]

    # Section 2: calculating option theoreticals
    mid_strike_index = int(round(stock_price / 5, 0))
    strikes = [5 * i for i in range(mid_strike_index - 2, mid_strike_index + 3)]
    dte = 30 / 365
    r = math.log(1 - rc/strikes[2]) / -dte
    sigma = random.randint(35,65) / 100

    theo_calls = []
    theo_puts = []
    theo_calls_delta = []
    theo_puts_delta = []
    theo_vegas = []
    for strike in strikes:
        theo_calls.append(round(black_scholes(stock_price, strike, dte, r, sigma, option = "call"), 2))
        theo_puts.append(round(black_scholes(stock_price, strike, dte, r, sigma, option = "put"), 2))
        theo_calls_delta.append(round(black_scholes_delta(stock_price, strike, dte, r, sigma, option = "call"), 2))
        theo_puts_delta.append(round(black_scholes_delta(stock_price, strike, dte, r, sigma, option = "put"), 2))
        theo_vegas.append(round(black_scholes_vega(stock_price, strike, dte, r, sigma), 2))

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
            # Section 3: determining vol parameters
            initial_straddle = round(theo_calls[i] + theo_puts[i], 2)
            impacted_straddle = initial_straddle
            curr_vol_state = np.random.choice(states, p = initial_prob_vector)
            straddle_impact_per_normal = get_straddle_impact(curr_vol_state)

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

    for strike, info, vega in zip(strikes, opening_info, theo_vegas):
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
        vegas = tk.Label(master=strike_frame, text="", width=5)

        given_info_l.pack(side=tk.LEFT)
        vegas.pack(side=tk.LEFT)
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

        given_info_l.bind("<Button-1>", partial(click_handler_l, struc, price))
        given_info_r.bind("<Button-1>", partial(click_handler_r, struc, price))

        vegas["text"] = vega
        if (struc == "b/w" or struc == "ps"):
            given_info_r["text"] = "{}: {}".format(struc, price)
        elif (struc == "p&s" or struc == "straddle" or struc == "cs"):
            given_info_l["text"] = "{}: {}".format(struc, price)

    theos_button.pack()

    # order handling and generation
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
        
        if not cust_order["market_order"]:
            market = [float(bid_entry.get()), float(offer_entry.get())]
            print(market)
        bid_entry.delete(0, tk.END)
        offer_entry.delete(0, tk.END)

        bid_entry.pack_forget()
        offer_entry.pack_forget()
        submit_market_button.pack_forget()
        willingness = max(impact_per_normal, 2) / 100

        if cust_order["structure"] == "combos" and not cust_order["puts_over"]:
            cust_order["level"] = round(impacted_stock_price - cust_order["strike"] + rc, 2)
        elif cust_order["structure"] == "combos" and not cust_order["bets_vol"]:
            cust_order["level"] = - round(impacted_stock_price - cust_order["strike"] + rc, 2)
        elif cust_order["structure"] == "calls" and not cust_order["bets_vol"]:
            bw = theo_puts[0] + theo_puts_delta[0] * (impacted_stock_price - ref_initial_stock) + rc
            cust_order["level"] = round(impacted_stock_price - cust_order["strike"] + bw, 2)
        elif cust_order["structure"] == "puts" and not cust_order["bets_vol"]:
            ps = theo_calls[-1] + theo_calls_delta[-1] * (impacted_stock_price - ref_initial_stock) - rc
            cust_order["level"] = round(- impacted_stock_price + cust_order["strike"] + ps, 2)
        elif cust_order["structure"] == "risk reversal" and not cust_order["puts_over"]:
            combo_temp = round(impacted_stock_price - cust_order["strike"][0] + rc, 2)
            i = strikes.index(cust_order["strike"][0])
            j = strikes.index(cust_order["strike"][1])
            cs_temp = theo_calls[i] - theo_calls[j]
            cs_temp += (impacted_stock_price - ref_initial_stock) * (theo_calls_delta[i] - theo_calls_delta[j])
            cust_order["level"] = round(combo_temp - cs_temp, 2)
        elif cust_order["structure"] == "risk reversal" and cust_order["puts_over"]:
            combo_temp = round(impacted_stock_price - cust_order["strike"][0] + rc, 2)
            i = strikes.index(cust_order["strike"][0])
            j = strikes.index(cust_order["strike"][1])
            cs_temp = theo_calls[i] - theo_calls[j]
            cs_temp += (impacted_stock_price - ref_initial_stock) * (theo_calls_delta[i] - theo_calls_delta[j])
            cust_order["level"] = round(cs_temp - combo_temp, 2)
        elif cust_order["structure"] == "call spread":
            i = strikes.index(cust_order["strike"][0])
            j = strikes.index(cust_order["strike"][1])
            cs_temp = theo_calls[i] - theo_calls[j]
            cs_temp += (impacted_stock_price - ref_initial_stock) * (theo_calls_delta[i] - theo_calls_delta[j])
            cust_order["level"] = round(cs_temp, 2)
        elif cust_order["structure"] == "put spread":
            i = strikes.index(cust_order["strike"][0])
            j = strikes.index(cust_order["strike"][1])
            ps_temp = theo_puts[j] - theo_puts[i]
            ps_temp += (impacted_stock_price - ref_initial_stock) * (theo_calls_delta[j] - theo_calls_delta[i])
            cust_order["level"] = round(ps_temp, 2)
        elif cust_order["structure"] == "puts":
            combo = impacted_stock_price - strikes[2] + rc
            atf_puts = (impacted_straddle - combo) / 2
            i = strikes.index(cust_order["strike"])
            if i == 1:
                put_spread = theo_puts[2] - theo_puts[1]
                cust_order["level"] = atf_puts - put_spread
            if i == 2:
                cust_order["level"] = atf_puts
            if i == 3:
                put_spread = theo_puts[3] - theo_puts[2]
                cust_order["level"] = atf_puts + put_spread

        elif cust_order["structure"] == "calls":
            combo = impacted_stock_price - strikes[2] + rc
            atf_calls = (impacted_straddle + combo) / 2
            i = strikes.index(cust_order["strike"])
            if i == 1:
                call_spread = theo_calls[1] - theo_calls[2]
                cust_order["level"] = atf_calls + call_spread
            if i == 2:
                cust_order["level"] = atf_calls
            if i == 3:
                call_spread = theo_calls[2] - theo_calls[3]
                cust_order["level"] = atf_calls - call_spread
        elif cust_order["structure"] == "straddle":
            i = strikes.index(cust_order["strike"])
            if i == 1:
                straddle_swap = theo_calls[1] + theo_puts[1] - theo_calls[2] - theo_puts[2]
                cust_order["level"] = impacted_straddle + straddle_swap
            if i == 2:
                cust_order["level"] = impacted_straddle
            if i == 3:
                straddle_swap = theo_calls[3] + theo_puts[3] - theo_calls[2] - theo_puts[2]
                cust_order["level"] = impacted_straddle + straddle_swap
        elif cust_order["structure"] == "strangle":
            i = strikes.index(cust_order["strike"][0])
            j = strikes.index(cust_order["strike"][1])
            if i > j:
                temp = j
                j = i
                i = temp
            straddle_change = impacted_straddle - initial_straddle
            prev_strangle = theo_puts[i] + theo_calls[j]
            cust_order["level"] = straddle_change + prev_strangle

        print(cust_order)

        if cust_order["direction"] == "bid":
            cust_order["level"] += willingness
            cust_order["level"] = round(cust_order["level"], 2)
            if cust_order["market_order"]:
                check_label["text"] = "Cust is bid {} for {} of the {} {}".format(cust_order["level"], cust_order["volume"], cust_order["strike"], cust_order["structure"])
                pass_order_button.pack(side=tk.LEFT)
                execute_order_button.pack(side=tk.LEFT)
            elif cust_order["level"] >= market[1]:
                if with_text:
                    check_label["text"] = "Customer lifts your offer"
                else:
                    speech.say("Customer lifts your offer")
                execute_order_button.pack(side=tk.LEFT)
            else:
                if with_text:
                    check_label["text"] = "Customer is bid {}".format(cust_order["level"])
                else:
                    speech.say("Customer is bid {}".format(cust_order["level"]))
                pass_order_button.pack(side=tk.LEFT)
                execute_order_button.pack(side=tk.LEFT)
        if cust_order["direction"] == "offer":
            cust_order["level"] -= willingness
            cust_order["level"] = round(cust_order["level"], 2)
            if cust_order["market_order"]:
                check_label["text"] = "Cust is offered {} for {} of the {} {}".format(cust_order["level"], cust_order["volume"], cust_order["strike"], cust_order["structure"])
                pass_order_button.pack(side=tk.LEFT)
                execute_order_button.pack(side=tk.LEFT)
            elif cust_order["level"] <= market[0]:
                if with_text:
                    check_label["text"] = "Customer hits your bid"
                else:
                    speech.say("Customer hits your bid")
                execute_order_button.pack(side=tk.LEFT)
            else:
                if with_text:
                    check_label["text"] = "Customer is offered {}".format(cust_order["level"])
                else:
                    speech.say("Customer is offered {}".format(cust_order["level"]))
                pass_order_button.pack(side=tk.LEFT)
                execute_order_button.pack(side=tk.LEFT)
        
        threading.Thread(target=speech.runAndWait).start()

    submit_market_button = tk.Button(text="Submit Market", master=incoming_order_frame, command=submit_market)

    def new_order():
        global curr_state
        global curr_vol_state
        global cust_order
        global impact_per_normal
        global straddle_impact_per_normal
        global impacted_stock_price
        global impacted_straddle
        print(impacted_stock_price)
        print(impacted_straddle)
        
        vol_order = random.choice([True, False])
        market_order = random.choice([True, False])
        cust_order["bets_vol"] = vol_order
        cust_order["market_order"] = market_order

        if vol_order:
            structures = ["calls", "puts", "straddle", "strangle"]
            structure = np.random.choice(structures, p = [1/3, 1/3, 1/12, 3/12])
        else:
            structures = ["combos", "calls", "puts", "risk reversal", "call spread", "put spread"]
            structure = np.random.choice(structures, p = [1/5, 1/5, 1/5, 1/5, 1/10, 1/10])

        if structure == "calls" and not vol_order:
            cust_order["structure"] = "calls"
            cust_order["strike"] = strikes[0]
            cust_order["puts_over"] = False
        elif structure == "puts" and not vol_order:
            cust_order["structure"] = "puts"
            cust_order["strike"] = strikes[-1]
            cust_order["puts_over"] = True
        elif structure == "combos":
            cust_order["structure"] = "combos"
            cust_order["strike"] = random.choice(strikes)
            cust_order["puts_over"] = cust_order["strike"] > impacted_stock_price
        elif structure == "risk reversal":
            cust_order["structure"] = "risk reversal"
            # determine the strike of the risky
            mid_strikes, mid_strike_indices = get_middle_strike_with_indices(strikes)
            cust_order["strike"] = mid_strikes
            cust_order["puts_over"] = theo_puts[mid_strike_indices[1]] > theo_calls[mid_strike_indices[0]]
        elif structure == "call spread":
            cust_order["structure"] = "call spread"
            mid_strikes, mid_strike_indices = get_middle_strike_with_indices(strikes)
            cust_order["strike"] = mid_strikes
            cust_order["puts_over"] = False
        elif structure == "put spread":
            cust_order["structure"] = "put spread"
            mid_strikes, mid_strike_indices = get_middle_strike_with_indices(strikes)
            cust_order["strike"] = mid_strikes
            cust_order["puts_over"] = True
        elif structure == "calls" and vol_order:
            cust_order["structure"] = "calls"
            cust_order["strike"] = random.choice(strikes[1:4])
            cust_order["puts_over"] = False
        elif structure == "puts" and vol_order:
            cust_order["structure"] = "puts"
            cust_order["strike"] = random.choice(strikes[1:4])
            cust_order["puts_over"] = True
        elif structure == "straddle":
            cust_order["structure"] = "straddle"
            cust_order["strike"] = random.choice(strikes[1:4])
            cust_order["puts_over"] = False
        elif structure == "strangle":
            cust_order["structure"] = "strangle"
            mid_strikes, mid_strike_indices = get_middle_strike_with_indices(strikes)
            cust_order["strike"] = mid_strikes
            cust_order["puts_over"] = False

        cust_order["volume"] = normal_order_size * random.choice([0.5, 1, 1.5]) 
        cust_order["volume"] = round(cust_order["volume"] / 50) * 50
        upwards = curr_state == "lu" or curr_state == "hu" or (curr_state == "eq" and random.choice([True, False]))

        # takes volume and converts to equivalent deltas of volume
        if cust_order["structure"] == "combos":
            deltas_volume = cust_order["volume"]
        elif cust_order["structure"] == "calls" and not vol_order:
            deltas_volume = cust_order["volume"] * (1 - abs(theo_puts_delta[0]))
        elif cust_order["structure"] == "puts" and not vol_order:
            deltas_volume = cust_order["volume"] * (1 - abs(theo_calls_delta[-1]))
        elif cust_order["structure"] == "risk reversal":
            i = strikes.index(cust_order["strike"][0])
            j = strikes.index(cust_order["strike"][1])
            deltas_volume = cust_order["volume"] * (abs(theo_puts_delta[i]) + abs(theo_calls_delta[j]))
        elif cust_order["structure"] == "call spread":
            i = strikes.index(cust_order["strike"][0])
            j = strikes.index(cust_order["strike"][1])
            deltas_volume = cust_order["volume"] * (abs(theo_calls_delta[i] - theo_calls_delta[j]))
        elif cust_order["structure"] == "put spread":
            i = strikes.index(cust_order["strike"][0])
            j = strikes.index(cust_order["strike"][1])
            deltas_volume = cust_order["volume"] * (abs(theo_puts_delta[i] - theo_puts_delta[j]))
        elif vol_order and (cust_order["structure"] == "calls" or cust_order["structure"] == "puts"):
            vega_volume = cust_order["volume"]
        elif vol_order and (cust_order["structure"] == "strangle" or cust_order["structure"] == "straddle"):
            vega_volume = cust_order["volume"] * 2

        if not vol_order:
            if upwards:
                impacted_stock_price += (impact_per_normal / 100) * (deltas_volume / normal_order_size)
                if cust_order["puts_over"]:
                    cust_order["direction"] = "offer"
                else:
                    cust_order["direction"] = "bid"
            else:
                impacted_stock_price -= (impact_per_normal / 100) * (deltas_volume / normal_order_size) 
                if cust_order["puts_over"]:
                    cust_order["direction"] = "bid"
                else:
                    cust_order["direction"] = "offer"
        if vol_order:
            if upwards:
                impacted_straddle += (straddle_impact_per_normal / 100) * (vega_volume / normal_order_size)
                cust_order["direction"] = "bid"
            else:
                impacted_straddle -= (straddle_impact_per_normal / 100) * (vega_volume / normal_order_size) 
                cust_order["direction"] = "offer"

        if market_order:
            bid_entry.pack(side=tk.LEFT)
            offer_entry.pack(side=tk.LEFT)
            submit_market_button.pack(side=tk.LEFT)
            new_order_button.pack_forget()
            submit_market()
            return
            
        if with_text:
            check_label["text"] = "Can I get a market for {} of the {} {}".format(cust_order["volume"], cust_order["strike"], cust_order["structure"])
        else:
            speech.say("Can I get a market for {} of the {} {}".format(cust_order["volume"], cust_order["strike"], cust_order["structure"]))

        bid_entry.pack(side=tk.LEFT)
        offer_entry.pack(side=tk.LEFT)
        submit_market_button.pack(side=tk.LEFT)
        new_order_button.pack_forget()

        threading.Thread(target=speech.runAndWait).start()

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
                diff_1 = (stock_test_price - (stock_price + stock_width)) * 100
                diff_2 = (impacted_stock_price - (stock_price + stock_width)) * 100
                filled_amt = amount_on_higher_levels(curr_stock_liquidity, diff_1, diff_2) + liquidity[1]
            else:
                diff_1 = ((stock_price - stock_width) - stock_test_price) * 100
                diff_2 = ((stock_price - stock_width) - impacted_stock_price) * 100
                filled_amt = amount_on_higher_levels(curr_stock_liquidity, diff_1, diff_2) + liquidity[0]
            filled_amt = min(filled_amt, stock_test_volume)
            stock_test_feedback["text"] = "Filled on {:,}.".format(filled_amt * 100)
            
            stock_price = impacted_stock_price
            stock_width = get_width(curr_stock_liquidity) / 100
            liquidity = [get_liquidity(curr_stock_liquidity), get_liquidity(curr_stock_liquidity)]
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