# Stock trading with the Ornstein-Uhlenbeck process
This repository contains code for a mean-reversion trading algorithm based on the Ornstein-Uhlenbeck (OU) process. The scripts in this repository are meant to illustrate the implementation of such an algorithm and should not be used to inform real investment decisions.

## Installation
This code requires [Python3](https://www.python.org/downloads/) and certain external libraries ("dependencies") to run. First, make sure you have Python3 installed in your system. Then, install the dependencies by running 
```
pip install -r requirements.txt
```

## Usage
There are two executale scripts in this repository, `mean_reversion.py` and `market_performance.py`. 

`mean_reversion.py` reads a list of companies, checks them for mean-reverting behavior, fits an OU process to their price series, and prints a list of companies whose stock can be potentially bought or shorted. This script outputs recommended portfolio allocations for each company too. This program takes four command-line arguments: the file name containing the company list, a start date and end date for the look back period in the format `yyyy-mm-dd`, and a threshold for the Augmented Dickey-Fuller test, which filters out non-mean reverting companies from the original list. For example, consider the command

```
python3 mean_reversion.py companies.in 2023-01-01 2024-12-31 0.05
```
which reads a list of companies from `companies.in`, selects the daily close prices of these companies from January 1, 2023 to December 31, 2024, and uses p < 0.05 to identify companies whose prices don't exhibit mean-reverting behavior.

`market_performance.py` reads a list of companies and their portfolio allocations and plots the performance of the portfolio against the S&P 500 and NASDAQ over a number of years. 

To run 
