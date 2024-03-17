import random
import signal
import sys
import math
successes = 0 

def handler(a, b):
    print("questions solved: {}".format(successes))
    sys.exit(0)

if __name__ == "__main__":
    multi_stock_flag = False
    if len(sys.argv) > 1:
        multi_stock_flag = True
    signal.signal(signal.SIGALRM, handler) 
    signal.alarm(120)

    stock_width = random.randint(1, 10)
    uneven = random.randint(0, 1)
    stock_price = random.randint(3000, 10000)
    stock_market = [(stock_price - stock_width) / 100, (stock_price + stock_width + uneven) / 100]
    rc = random.randint(1, 10) / 100

    while True:
        if multi_stock_flag:
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
        
        correct = False
        while not correct:
            print("cust {} {:.2f} in the {} combos, what is this like in stock?".format(bid_or_offer, theo + amt_through, strike))
            dir_guess, price_guess = input().split()

            po = strike > (stock_price / 100)
            if po:
                price_correct = -theo - amt_through
            else:
                price_correct = theo + amt_through
            price_correct = price_correct + strike - rc

            if (po and bid_or_offer == "bid") or (not po and bid_or_offer == "offer"):
                dir_correct = "offer"
            else:
                dir_correct = "bid"

            if math.isclose(float(price_guess), price_correct) and dir_guess == dir_correct:
                correct = True

        print()
        successes += 1