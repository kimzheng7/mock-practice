import random
print("gl with mock")

while True:
    stock_width = random.randint(1, 10)
    uneven = random.randint(0, 1)
    stock_price = random.randint(3000, 10000)
    stock_market = [(stock_price - stock_width) / 100, (stock_price + stock_width + uneven) / 100]
    rc = random.randint(1, 10) / 100

    mid_strike_index = int(stock_price // 500)
    strikes = [5 * i for i in range(mid_strike_index - 2, mid_strike_index + 3)]

    print("stock market:", stock_market[0], "@", stock_market[1])
    print("r/c: {}".format(rc))

    bid_or_offer = random.choice(["bid", "offer"])
    strike = random.choice(strikes)
    theo = abs(stock_price / 100 - strike + rc)
    amt_through = random.randint(-15, 15) / 100

    print("cust {} {:.2f} in the {} combos, what is this like in stock?".format(bid_or_offer, theo + amt_through, strike))
    input()