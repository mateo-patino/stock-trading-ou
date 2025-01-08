"""
This script checks for mean-reverting behavior in a list of publicly-traded companies and evaluates the
deviation from the mean of the current price to signal trading opportunities.

This is the quantitative tool our team [name] used at the Wharton Youth Investment Competition to filter
stocks and manage our portfolio allocations.

"""

import yfinance as yf
import numpy as np
from scipy.stats import linregress
from sys import argv
from statsmodels.tsa.stattools import adfuller


class Company:
    def __init__(self, name, symbol, prices, current_price):
        self.name = name
        self.symbol = symbol
        self.prices = prices
        self.current_price = current_price
        self.mu = None
        self.z_score = None


# reads company list from filename; returns Company list
def read_company_list(filename, start, end):
    companies = []
    with open(filename, "r") as file:
        lines = file.readlines()
        visited = {}
        for line in lines:
            elements = line.split()
            symbol = elements[0].rstrip()
            if visited.get(symbol, False):
                continue
            else:
                visited[symbol] = True
            name = " ".join(elements[1:])
            try:
                prices = np.array(yf.download(symbol, start=start, end=end)["Close"]).flatten()
                new_company = Company(name.strip(), symbol, prices, prices[-1])
                companies.append(new_company)
            except:
                pass
        print(f"\n{len(companies)} companies read out of {len(lines)}")
    return companies


# checks if a set of prices exhibits mean-reverting behavior with an Augmented Dickey-Fuller test
def mean_reverting_behavior(prices, threshold):
    p_value = adfuller(prices)[1]
    if p_value < threshold:
        return True
    return False


# calculate mean price from Ornstein-Uhlenbeck equation
def fit_OU_model(companies):
    short_companies, long_companies = [[] for i in range(2)]
    for company in companies:
        # estimate mean price from OU equation with linear regression
        log_prices = np.log(company.prices)
        dX = np.diff(log_prices)
        X_t = log_prices[:-1] 
        slope, intercept, r_value, p_value, std_err = linregress(X_t, dX)
        mu = np.exp(-intercept / slope)
        company.mu = mu

        # find z-score of current price for given company
        z_score = (company.prices[-1] - mu) / np.std(company.prices)
        company.z_score = z_score
        if z_score < 0:
            long_companies.append(company) # if z_score is negative, buy the stock
        else:
            short_companies.append(company)
    return long_companies, short_companies


# takes in a list of companies; returns dictionary with each company's weight within a portfolio
def portfolio_allocation(companies):
    sum_z = 0
    for company in companies: 
        sum_z += abs(company.z_score)

    # keys: company name; value: weight
    allocation = {}
    for company in companies:
        allocation[f"{company.symbol} {company.name}"] = abs(company.z_score) / sum_z
    return allocation

# argv = ["filename", "lookback start (yyyy-mm-dd)", "lookback end (yyyy-mm-dd)", threshold for ADF test]
if __name__ == "__main__":
    if len(argv) != 5:
        exit("Usage: python3 mean_reversion.py filename start end adf-threshold")
    companies = read_company_list(*argv[1:4])

    # Filter companies with mean-reverting behavior
    mean_reverting_companies = []
    non_reverting = []
    for company in companies:
        if mean_reverting_behavior(company.prices, float(argv[4])):
            mean_reverting_companies.append(company)
        else:
            non_reverting.append(company)
    
    # PRINT RESULTS
    print(f"\nNON-MEAN-REVERTING COMPANIES ({len(non_reverting)} TOTAL)")
    for company in non_reverting:
        print(f"{company.symbol} {company.name}")
    print(f"\nMEAN-REVERTING COMPANIES ({len(mean_reverting_companies)} TOTAL)")
    for company in mean_reverting_companies:
        print(f"{company.symbol} {company.name}")

    # Find companies to short and long
    long_companies, short_companies = fit_OU_model(mean_reverting_companies)

    # Print results
    print(f"\nLONG COMPANIES & Z-SCORES ({len(long_companies)} TOTAL)")
    for company in long_companies:
        print(f"{company.symbol} {company.name} {company.z_score}")
    print(f"\nSHORT COMPANIES & Z-SCORES ({len(short_companies)} TOTAL)")
    for company in short_companies:
        print(f"{company.symbol} {company.name} {company.z_score}")

    # Portfolio allocation
    allocation = portfolio_allocation(long_companies + short_companies)
    print("\nPORTFOLIO WEIGHTS")
    for name, weight in allocation.items():
        print(name, weight)

