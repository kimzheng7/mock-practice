# import plotly.express as px

# def first_harvest_pdf(x):
#     if 0 <= x and x <= 120:
#         return 1 / 121
#     else:
#         return 0

# def first_harvest_cdf(x): # probability less than OR EQUAL TO x
#     if x < 0:
#         return 0
#     if x >= 120:
#         return 1
    
#     return (x + 1) * (1 / 121)

# def second_harvest_pdf(x):
#     if 0 <= x and x <= 80:
#         return 1 / 81
#     else:
#         return 0

# def second_harvest_cdf(x): # probability less than OR EQUAL TO x
#     if x < 0:
#         return 0
#     if x >= 80:
#         return 1
    
#     return (x + 1) * (1 / 81)

# def both_harvest_pdf(x):
#     if x < 0 or x > 200:
#         return 0
#     sums = 0
#     for i in range(x + 1):
#         sums += first_harvest_pdf(i) * second_harvest_pdf(x - i)
#     return sums

# def total_harvest_cdf(x):
#     if x < 0:
#         return 0
#     if x >= 200:
#         return 1

#     sums = 0
#     for i in range(x + 1):
#         sums += both_harvest_pdf(i)

#     return sums

# def beginning_fair(num_players):
#     pass





# Eventually take the below and use the actual uniform distributions





import numpy as np
from scipy.stats import norm

# estimating fairs using a normal distribution
def uniform_dist_to_norm_dist(lower, upper):
    values = range(lower, upper + 1)
    return np.mean(values), np.var(values)

# getting distributions of first harvest
def first_harvest_dist():
    return uniform_dist_to_norm_dist(0, 121)

# getting distributions of second harvest
def second_harvest_dist():
    return uniform_dist_to_norm_dist(0, 81)

# get list of distributions, and then combine to get a total distribution
def combine_distributions(list_of_dists):
    total_mean = 0
    total_var = 0
    for mean, var in list_of_dists:
        total_mean += mean
        total_var += var

    return total_mean, total_var

# getting fair given distributions
def get_fair(first_harvest_distributions, second_harvest_distributions, num_players):
    list_of_dists = first_harvest_distributions + second_harvest_distributions
    full_dist_mean, full_dist_var = combine_distributions(list_of_dists)

    overs_limit = num_players * 100
    if full_dist_var == 0:
        if full_dist_mean >= overs_limit:
            return 0.01
        else:
            return 0.99
    else:
        z_score_overs_limit = (overs_limit - full_dist_mean) / (full_dist_var) ** (1/2)

    return 0.99 * norm.cdf(z_score_overs_limit) + 0.01 * (1 - norm.cdf(z_score_overs_limit))

def fair_pre_spring(num_players):
    list_of_dists = []
    for j in range(2):
        curr = []
        for i in range(num_players):
            if j == 0:
                curr.append(first_harvest_dist())
            if j == 1:
                curr.append(second_harvest_dist())
        list_of_dists.append(curr)

    return get_fair(list_of_dists[0], list_of_dists[1], num_players)

def fair_post_spring(num_players, spring_harvest):
    list_of_dists = []
    for j in range(2):
        curr = []
        for i in range(num_players):
            if j == 0:
                if i == 0:
                    curr.append((spring_harvest, 0))
                else:
                    curr.append(first_harvest_dist())
            if j == 1:
                curr.append(second_harvest_dist())
        list_of_dists.append(curr)

    return get_fair(list_of_dists[0], list_of_dists[1], num_players)

def fair_pre_summer(num_players, spring_harvest, spring_total_harvest):
    list_of_dists = []
    for j in range(2):
        curr = []
        for i in range(num_players):
            if j == 0:
                if i == 0:
                    curr.append((spring_harvest, 0))
                else:
                    curr.append(((spring_total_harvest - spring_harvest) / (num_players - 1), 0))
            if j == 1:
                curr.append(second_harvest_dist())
        list_of_dists.append(curr)

    return get_fair(list_of_dists[0], list_of_dists[1], num_players)

def fair_post_summer(num_players, spring_harvest, spring_total_harvest, summer_harvest):
    list_of_dists = []
    for j in range(2):
        curr = []
        for i in range(num_players):
            if j == 0:
                if i == 0:
                    curr.append((spring_harvest, 0))
                else:
                    curr.append(((spring_total_harvest - spring_harvest) / (num_players - 1), 0))
            if j == 1:
                if i == 0:
                    curr.append((summer_harvest, 0))
                else:
                    curr.append(second_harvest_dist())
        list_of_dists.append(curr)

    return get_fair(list_of_dists[0], list_of_dists[1], num_players)

def fair_autumn(num_players, spring_harvest, spring_total_harvest, summer_harvest, summer_total_harvest):
    list_of_dists = []
    for j in range(2):
        curr = []
        for i in range(num_players):
            if j == 0:
                if i == 0:
                    curr.append((spring_harvest, 0))
                else:
                    curr.append(((spring_total_harvest - spring_harvest) / (num_players - 1), 0))
            if j == 1:
                if i == 0:
                    curr.append((summer_harvest, 0))
                else:
                    curr.append(((summer_total_harvest - summer_harvest) / (num_players - 1), 0))
        list_of_dists.append(curr)

    return get_fair(list_of_dists[0], list_of_dists[1], num_players)


num_players = 8
print(fair_pre_spring(num_players))
spring_harvest = 30
print(fair_post_spring(num_players, spring_harvest))
spring_total_harvest = 450
print(fair_pre_summer(num_players, spring_harvest, spring_total_harvest))
summer_harvest = 40
print(fair_post_summer(num_players, spring_harvest, spring_total_harvest, summer_harvest))
summer_total_harvest = 330
print(fair_autumn(num_players, spring_harvest, spring_total_harvest, summer_harvest, summer_total_harvest))

