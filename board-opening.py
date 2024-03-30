import math
from scipy.stats import norm 
import random
import tkinter as tk

def black_scholes(S, K, T, r, sigma, option='call'):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = (math.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    
    if option == 'call':
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    if option == 'put':
        return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

if __name__ == "__main__":
    # precalcs and parameter deciding
    stock_price = random.randint(3000, 10000) / 100
    stock_width = random.randint(2, 15) / 100
    uneven = random.randint(0, 1) / 100
    stock_market = [round(stock_price - stock_width, 2), round(stock_price + stock_width + uneven, 2)]
    rc = random.randint(3, 10) / 100

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
    rc_text = tk.Label(text="r/c = {}".format(rc))
    stock_text.pack()
    rc_text.pack()
    call_theo_texts = []
    put_theo_texts = []

    theos_showing = False
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
        if struc == "p&s" or struc == "straddle" or struc == "cs":
            given_info_l = tk.Label(master=strike_frame, text="{}: {}".format(struc, price), width=12)
            given_info_r = tk.Label(master=strike_frame, text="", width=12)
        if struc == "b/w" or struc == "ps":
            given_info_l = tk.Label(master=strike_frame, text="", width=12)
            given_info_r = tk.Label(master=strike_frame, text="{}: {}".format(struc, price), width=12)

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

    theos_button.pack()

    def new_order():
        higher = random.choice([False, True])
        impact = random.randint(1, 20) / 100
        volume = int(impact * 100 * 30)

    resting_orders = []
    resting_orders_showing = False
    resting_orders_button = tk.Button(text="Show resting orders")

    new_order_button = tk.Button(text="New Order")
    new_order_button.pack()
    pass_order_button = tk.Button(text="Pass")
    pass_order_button.pack()
    execute_order_button = tk.Button(text="Execute")
    execute_order_button.pack()


    window.mainloop()