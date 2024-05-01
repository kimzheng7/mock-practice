import plotly.express as px

def first_harvest_pdf(x):
    if 0 <= x and x <= 120:
        return 1 / 121
    else:
        return 0

def first_harvest_cdf(x): # probability less than OR EQUAL TO x
    if x < 0:
        return 0
    if x >= 120:
        return 1
    
    return (x + 1) * (1 / 121)

def second_harvest_pdf(x):
    if 0 <= x and x <= 80:
        return 1 / 81
    else:
        return 0

def second_harvest_cdf(x): # probability less than OR EQUAL TO x
    if x < 0:
        return 0
    if x >= 80:
        return 1
    
    return (x + 1) * (1 / 81)

def total_harvest_pdf(x):
    if x < 0 or x > 200:
        return 0
    sums = 0
    for i in range(x + 1):
        sums += first_harvest_pdf(i) * second_harvest_pdf(x - i)
    return sums

def total_harvest_cdf(x): # probability less than OR EQUAL TO x
    if x < 0:
        return 0
    if x >= 200:
        return 1

    sums = 0
    for i in range(x + 1):
        sums += total_harvest_pdf(i)

    return sums

def price_given_inventory_middle(curr_amount):
    # if you get (99 - curr amount beans), or less, then the bean is worth 1
    return second_harvest_cdf(99 - curr_amount)

def price_given_inventory_beginning(curr_amount):
    # if you get (99 - current amount beans), or less, then bean is worth 1
    # if you get more, then bean is worth 0
    return total_harvest_cdf(99 - curr_amount)

bean_price_beginning = []
bean_price_middle = []
for i in range(110):
    bean_price_beginning.append(price_given_inventory_beginning(i))
    bean_price_middle.append(price_given_inventory_middle(i))

fig = px.scatter(x=list(range(110)), y=bean_price_beginning)
fig_ = px.scatter(x=list(range(110)), y=bean_price_middle)
fig.show()
fig_.show()
