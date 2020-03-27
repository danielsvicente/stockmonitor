import logging
import os
import json


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def format_value(value, space):
	return ("{:.2f}".format(value)).rjust(space)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

class Transactions:

    __list_transactions = []

    def __init__(self):
        self.total_balance = 0.00
        self.total_fees = 0.00
        self.balance_per_year = {}


    def load(self, transactions):
        self.__list_transactions = transactions
        logging.debug(self.__list_transactions)

        for t in transactions:
            if t['date']:
                year = t['date'][-4:]
                if year in self.balance_per_year:
                    self.balance_per_year[year] += -t['total_trade']
                else:
                    self.balance_per_year[year] = -t['total_trade']
            self.total_balance += -t['total_trade']
            self.total_fees += t['total_trade'] - t['total_after_fees']

    def summary(self):
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('    Transactions summary    ')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('')
        print('   Balance:')
        print('')
        for year, value in self.balance_per_year.items():
            print('      ' + year + ':' + format_value(value, 12))
        print('')
        print('     Total:' + format_value(self.total_balance, 12))
        print('')
        print('Total fees:' + format_value(self.total_fees, 12))
        print('')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

class Earnings:

    __list_earnings = []

    def load(self, earnings):
        self.__list_earnings = earnings
        logging.debug(self.__list_earnings)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.transactions = []
        self.earnings = []
        self.quantity = 0
        self.total_invested = 0
        self.average_price = 0
        logging.debug("New stock " + self.ticker)

    def get_ticker(self):
        return self.ticker

    def add_transaction_json(self, transaction):
        logging.debug(self.ticker + ": Adding new transaction")
        if not 'date' in transaction:
            raise InputError('date', 'is missing')
        self.transactions.append(transaction)

    def add_transaction(self, date, operation, quantity, price):
        t = {}
        t['date'] = date
        t['type'] = operation
        t['quantity'] = quantity
        t['price'] = price
        self.add_transaction_json(t)

    def add_earning_json(self, earning):
        logging.debug(self.ticker + ": Adding new earning")
        #if not ... in earning:
        #    raise InputError(...)
        self.earnings.append(earning)

    def add_earning(self, date, operation, value, shares):
        e = {}
        e['date'] = date
        e['operation'] = operation
        e['valeu'] = value
        e['shares'] = shares
        self.add_earning_json(e)

    def print_as_json(self):
        print("transactions:" + json.dumps(self.transactions, indent=2))
        print("earning:" + json.dumps(self.earnings, indent=2))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

class Portfolio:

    # Assets
    stocks = {}

    # Figures
    total_invested = 0.00
    current_total = 0.00
    current_yield = 0.00

    def add_stock(self, stock):
        logging.debug("Portfolio.add_stock( " + stock.get_ticker() + " )")
        self.stocks[stock.get_ticker()] = stock

    def get_stock(self, ticker):
        return self.stocks[ticker]

    def summary(self):
        print("Portfolio summary:")
        for ticker, stock in self.stocks.items():
            print(ticker + ": ")
            stock.print_as_json()

    def contains(self, ticker):
        return ticker in self.stocks


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

class PersistentData:

    # File content holder - JSON 
    __data = {}

    def __init__(self):
        parent_path = os.path.dirname(__file__)
        datafile_path = os.path.join(parent_path, 'data.json')
        with open(datafile_path, 'r') as data_file:
            self.__data = json.load(data_file)

    def get_all_transactions(self):
        return self.__data['transactions']

    def get_all_earnings(self):
        return self.__data['earnings']


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

if __name__ == "__main__":
    #logging.basicConfig(level=logging.DEBUG)

    portfolio = Portfolio()
    
    # Load persisten_data
    persistent_data = PersistentData()
    transactions = Transactions()
    earnings = Earnings()

    transactions.load(persistent_data.get_all_transactions())
    earnings.load(persistent_data.get_all_earnings())

    transactions.summary()
"""
    for transaction in transactions:
        for trade in transaction['trades']:
            trade['date'] = transaction['date']
            if portfolio.contains(trade['ticker']):
                portfolio.get_stock(trade['ticker']).add_transaction_json(trade)
            else:
                stock = Stock(trade['ticker'])
                stock.add_transaction_json(trade)
                portfolio.add_stock(stock)

    earnings = persistent_data.get_all_earnings()
    for earning in earnings:
        portfolio.get_stock(earning['ticker']).add_earning_json(earning)


    portfolio.summary()
"""

