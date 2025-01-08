"""
This script takes a list of companies and their weights in a portfolio and compares the portfolio's performance against the S&P500.

"""

from sys import argv
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf


# takes a set of lists and returns all of them spliced until the minimum length
def adjust_series(*lists):
    min_length = min([len(l) for l in lists])
    result = []
    for l in lists:
        result.append(l[:min_length])
    return result


# generates value of a portfolio only composed of the reference securities
def generate_reference_performance(prices, capital):
    shares_owned = capital / prices[0] # 0th prices is purchase price
    value = []
    for current_price in prices:
        value.append(current_price * shares_owned)
    return value


# generates value of portfolio composed of companies with weights; N data points
def generate_portfolio_performance(allocations, company_prices, capital, N):
    # calculate quantities of each stock
    quantity = {}
    for name, weight in allocations.items():
        quantity[name] = (capital * weight) / company_prices[name][0]

    # calculate the N values of the portfolio
    value = []
    for i in range(N):
        current_value = 0
        for name, prices in company_prices.items():
            current_value += prices[i] * quantity[name]
        value.append(current_value)
    return value


# takes start, end date in yyyy-mm-dd and number of price points (N) and outputs time axis and tickers
def generate_time_axis(start, end, N):
    start_year = int(start.split("-")[0])
    end_year = int(end.split("-")[0])
    if start_year == end_year:
        exit(f"End and start years cannot be the same ({start_year}). Ensure lookback period is longer than one year.")

    # Create time axis
    Time = np.linspace(start_year, end_year, N)

    # Create time tickers
    time_tickers = []
    for i in range(end_year - start_year + 1):
        time_tickers.append(start_year + i) # years in between start and end
    return Time, time_tickers


# reads companies from filename in [name] [weight] format for portfolio, returns dictionary w/ name = (p weights
def read_portfolio(filename, start, end):
    visited, allocations, prices = [{} for i in range(3)]
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            elements = line.split()
            company_symbol = elements[0]
            company_name = " ".join(elements[1:len(elements) - 1])
            # avoid for repeated companies
            if not visited.get(company_name, False):
                visited[company_name] = True
            else:
                continue
            allocations[company_name] = float(elements[-1]) # last item is weight
            prices[company_name] = np.array(yf.download(company_symbol, start=start, end=end)["Close"]).flatten()
    return allocations, prices

if __name__ == "__main__":
    if len(argv) != 5:
        exit("Usage: market_performance.py [filename] [start] [end] [capital]")
    filename, start, end, capital = argv[1:]
    allocations, company_prices = read_portfolio(filename, start, end)

    # retrieve close prices from the S&P 500 and NASDAQ composites
    try:
        sp500_close = np.array(yf.Ticker("^GSPC").history(start=start, end=end)["Close"]).flatten()
        nasdaq_close = np.array(yf.Ticker("^IXIC").history(start=start, end=end)["Close"]).flatten()
    except Exception as e:
        exit(f"S&P 500 and NASDAQ data could not be retrieved at this time:\n{e}")

    # adjust size of sp500 and nasdaq to account for missing dates
    adjusted_series = adjust_series(sp500_close, nasdaq_close, *company_prices.values())
    sp500_close, nasdaq_close = adjusted_series[:2]

    # match the price lists to their corresponding company in the company_prices dict
    adjusted_company_prices = adjusted_series[2:]
    for i, key in enumerate(company_prices.keys()):
        company_prices[key] = adjusted_company_prices[i]

    # generate lists of data points
    Time, time_tickers = generate_time_axis(start, end, len(sp500_close))
    sp500 = generate_reference_performance(sp500_close, float(capital))
    nasdaq = generate_reference_performance(nasdaq_close, float(capital))
    portfolio = generate_portfolio_performance(allocations, company_prices, float(capital), len(sp500_close))

    # plot
    plt.plot(Time, portfolio, color="black", lw=2, label=f"Our portfolio ({len(company_prices)} companies)", zorder=5)
    plt.plot(Time, sp500, color="tab:blue", lw=2, label="S&P 500")
    plt.plot(Time, nasdaq, color="tab:orange", lw=2, label="NASDAQ")
    plt.xlabel("Year")
    plt.ylabel(f"Value of ${capital}")
    plt.title("Our portfolio vs. the S&P 500 and NASDAQ")
    plt.xticks(time_tickers)
    plt.grid("both")
    plt.legend()
    plt.show()