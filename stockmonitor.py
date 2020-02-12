import sys
import os
from datetime import date, timedelta
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web
import time
import numpy as np
import json
import logging
import inspect
import argparse

parser = argparse.ArgumentParser(description='Monitor for stock shares.')
parser.add_argument('-v', '--verbose', action='store_true', help='print out all call outputs and debug logs')
parser.add_argument('-p', '--period', default=30, help='number of days for stock history')
args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('verbose=' + str(args.verbose))
    logging.debug('period=' + str(args.period))


plt.style.use('dark_background')
plt.figure().subplots_adjust(hspace=0.5)
plt.ion()
mng = plt.get_current_fig_manager()
#mng.full_screen_toggle()


# Access data from json file
parent_path = os.path.dirname(__file__)
datafile_path = os.path.join(parent_path, "data.json")
with open(datafile_path, "r") as data_file:
    data = json.load(data_file)

# Process data
total_deposited = data["total_deposited"]
available_to_invest = data["available_to_invest"]
inflation = data["inflation"]
transactions = data["transactions"]
earnings = data["earnings"]
stocks = []
dividends = {}
total_fees = 0.00
total_earning = 0.00

total_money = 0.00

# Fill list of stocks
for transaction in transactions:
    total_fees = total_fees + abs(transaction['total_trade'] - transaction['total_after_fees'])
    for trade in transaction['trades']:
        new_stock = True
        for stock in stocks:
            if stock['ticker'] == trade['ticker']:
                if trade['type'] == 'BUY':
                    stock['quantity'] = stock['quantity'] + trade['quantity']
                    stock['total_invested'] = stock['total_invested'] + (trade['quantity'] * trade['price'])
                elif trade['type'] == 'SELL':
                    stock['quantity'] = stock['quantity'] - trade['quantity']
                    stock['total_invested'] = stock['total_invested'] - (trade['quantity'] * trade['price'])
                elif trade['type'] == 'ADJUST':
                	stock['quantity'] = stock['quantity'] + trade['quantity']
                elif trade['type'] == 'SPLIT':
                        stock['quantity'] = stock['quantity'] * trade['factor']
                if stock['quantity'] > 0:
                    stock['average_price'] = stock['total_invested'] / stock['quantity']
                new_stock = False
        if new_stock is True:
            ti = trade['quantity'] * trade['price']
            stocks.append(dict(ticker=trade['ticker'], yahoo_id=trade["yahoo_id"], quantity=trade['quantity'], average_price=trade['price'], total_invested=ti, dividend=0.0, day_price_list=[]))
            dividends[trade['ticker']] = dict(ticker=trade['ticker'], yahoo_id=trade["yahoo_id"], quantity=trade['quantity'], average_price=trade['price'], total_invested=ti, dividend_total=0.0, dividend_per_share=0.0, dividend_average=0.0, dividend_count=0, day_price_list=[])


# Calculate total received from the companies to date
for item in earnings:
    dividends[item['ticker']]['dividend_count'] = dividends[item['ticker']]['dividend_count'] + 1
    dividends[item['ticker']]['dividend_total'] = dividends[item['ticker']]['dividend_total'] + item['value']
    dividends[item['ticker']]['dividend_per_share'] = dividends[item['ticker']]['dividend_per_share'] + (item['value'] / item['shares'])
    dividends[item['ticker']]['dividend_average'] = dividends[item['ticker']]['dividend_per_share'] / dividends[item['ticker']]['dividend_count']
    total_earning = total_earning + item['value']

period = int(args.period)
start = date.today() - timedelta(days=period)
end = date.today()

intraday = []
ibvsp_intraday = []

def calc_change(previous_close, current_rate):
	change = current_rate - previous_close
	change_percentage = change * 100 / previous_close
	return change, change_percentage

def format_value(value):
	return "{:.2f}".format(value)

def get_color(value):
    if value > 0.0:
        return 'limegreen'
    elif value < 0.0:
        return 'red'
    else:
        return 'grey'


logging.debug(json.dumps(stocks, indent=4))
logging.debug(json.dumps(dividends, indent=4))

print('------------------------------------------------------------------------------------')
print('                               SHARES AVERAGE PRICES                                ')
print('------------------------------------------------------------------------------------')
for stock in stocks:
    if stock['quantity'] > 0:
        online_data = web.get_data_yahoo(str(stock["yahoo_id"]), start, end)
        logging.debug(online_data.iloc[-1])
        close_price = online_data.iloc[-1]['Close']
        total_money = total_money + (close_price * stock['quantity'])
        # calculating yield
        total_with_average_price = stock['quantity'] * stock['average_price']
        total_with_close_price = stock['quantity'] * close_price
        current_difference = total_with_close_price - total_with_average_price
        current_yield = (100 * total_with_close_price / total_with_average_price) - 100
        print(stock['ticker'], \
                str(stock['quantity']).rjust(10), \
                format_value(stock['total_invested']).rjust(10), \
                format_value(stock['average_price']).rjust(10), \
                format_value(close_price).rjust(10), \
                format_value(current_yield).rjust(10), "%", \
                format_value(current_difference).rjust(10), \
                format_value(total_with_close_price).rjust(10))

print('')
print('---------------------------')
print('         DIVIDENDS         ')
print('---------------------------')
for stock in stocks:
    if dividends[stock['ticker']]:
        print(dividends[stock['ticker']]['ticker'], \
		format_value(dividends[stock['ticker']]['dividend_total']).rjust(10), \
		format_value(dividends[stock['ticker']]['dividend_average']).rjust(10))

print('')
print('TOTAL INVESTED: ', format_value(total_deposited).rjust(10))
print('TOTAL TODAY   : ', format_value(total_money + available_to_invest).rjust(10))
print('BALANCE       : ', format_value(total_money + available_to_invest - total_deposited).rjust(10))

print('')
print('TOTAL PAID FEES TO DATE: ', format_value(total_fees).rjust(10))
print('TOTAL RECEIVED TO DATE : ', format_value(total_earning).rjust(10))
print('')

while True:

	try:

		current_shares_value = 0
		last_shares_value = 0
		df_hist = pd.DataFrame()
		historical = pd.Series()
		ibvsp_today = pd.Series()

		plot_column = 0
		qtt_elements = 0
		qtt_rows = 4

		plt.clf()

		for stock in stocks:
			if stock["quantity"] > 0:
				qtt_elements = qtt_elements + 1

		for stock in stocks:
			if stock["quantity"] > 0:
				logging.debug("Pulling", stock["yahoo_id"])

				online_data = web.get_data_yahoo(str(stock["yahoo_id"]), start, end)
				logging.debug(online_data)

				online_data['Diff'] = online_data['Close'].diff()
				online_data['DiffTotal'] = online_data['Diff'] * stock["quantity"]
				online_data['Total'] = online_data['Close'] * stock["quantity"]
				# Cleaning datasets from possible NaN values
				online_data.fillna(method='ffill', inplace=True)

				online_data_current_rate = online_data.iloc[-1]['Close']
				online_data_previous_close = online_data.iloc[-2]['Close']
				online_data_change, online_data_change_percentage = calc_change(online_data_previous_close, online_data_current_rate)

				current_shares_value = current_shares_value + (online_data_current_rate * stock["quantity"])
				last_shares_value = last_shares_value + (online_data_previous_close * stock["quantity"])
				stock["day_price_list"].append(current_shares_value)
				day_price_list_series = pd.Series(stock["day_price_list"])

				# Console log
				logging.debug(stock["ticker"] + format_value(online_data_current_rate) + ' ' + format_value(online_data_change) + ' (' + format_value(online_data_change_percentage) + ')' )

				if historical.empty:
					historical = online_data["Total"]
				else:
					historical = historical + online_data["Total"]

				# Row 1 - Close prices
				plt.subplot2grid((qtt_rows, qtt_elements), (0, plot_column), rowspan=1, colspan=1)
				plt.title(stock["ticker"] + ': ' + format_value(online_data_current_rate) + ' ' + format_value(online_data_change) + ' (' + format_value(online_data_change_percentage) + '%)' )
				online_data['Close'].plot(color=get_color(online_data_change))

				# Row 2 - Diff
				plt.subplot2grid((qtt_rows, qtt_elements), (1, plot_column), rowspan=1, colspan=1)
				plt.tick_params(
				    axis='x',          # changes apply to the x-axis
				    which='both',      # both major and minor ticks are affected
				    bottom='off',      # ticks along the bottom edge are off
				    top='off',         # ticks along the top edge are off
				    labelbottom='off') # labels along the bottom edge are off
				#online_data['Diff'].plot(kind='bar', color=get_color(online_data_change))
				day_price_list_series.plot(color=get_color(online_data_change))

				plot_column = plot_column + 1

		current_account_value = current_shares_value + available_to_invest
		current_yield_value = current_account_value - total_deposited
		current_yield_percentage = current_account_value * 100 / total_deposited
		yield_after_inflation = current_yield_value - (total_deposited * inflation / 100)
		yield_after_inflation_percentage = yield_after_inflation * 100 / total_deposited

		current_day_yield_value = current_shares_value - last_shares_value
		current_day_yield_percentage = (current_shares_value * 100 / last_shares_value) - 100

		df_hist["Total"] = historical
		df_hist["Diff"] = df_hist["Total"].diff()

		logging.debug('SHARES TOTAL : ' + format_value(current_shares_value))
		logging.debug('ACCOUNT TOTAL : ' + 	format_value(current_account_value) + ' ' + format_value(current_yield_value) + ' (' + format_value(current_yield_percentage) + '%)')
		logging.debug("HISTORICAL")
		logging.debug(df_hist)

		# Row 3 - Historical and Intraday

		plt.subplot2grid((qtt_rows, qtt_elements), (2, 0), rowspan=1, colspan=3)
		plt.title('Total : ' + format_value(current_account_value) + ' ' + format_value(yield_after_inflation) + ' (' + format_value(yield_after_inflation_percentage) + '%)' )
		historical.plot(color=get_color(yield_after_inflation))

		intraday.append(current_account_value)
		intraday_series = pd.Series(intraday)
		plt.subplot2grid((qtt_rows, qtt_elements), (2, 3), rowspan=1, colspan=4)
		plt.title('Today : ' + format_value(current_day_yield_value) + ' (' + format_value(current_day_yield_percentage) + '%)' )
		intraday_series.plot(color=get_color(current_day_yield_value))

		#### IBOVESPA index ####
		online_ibvsp = web.get_data_yahoo("^BVSP", start, end)
		online_ibvsp['Diff'] = online_ibvsp['Close'].diff()
		if ibvsp_today.empty:
			ibvsp_today = online_ibvsp['Close']
		else:
			ibvsp_today = ibvsp_today + online_ibvsp['Close']
		ibvsp_intraday.append(online_ibvsp.iloc[-1]['Close'])
		ibvsp_intraday_series = pd.Series(ibvsp_intraday)
		online_ibvsp['Diff'] = online_ibvsp['Close'].diff()
		online_ibvsp.fillna(method='ffill', inplace=True)

		online_ibvsp_current_rate = online_ibvsp.iloc[-1]['Close']
		online_ibvsp_previous_close = online_ibvsp.iloc[-2]['Close']
		online_ibvsp_change, online_ibvsp_change_percentage = calc_change(online_ibvsp_previous_close, online_ibvsp_current_rate)

		plt.subplot2grid((qtt_rows, qtt_elements), (3, 0), rowspan=1, colspan=3)
		plt.title('IBOVESPA ' + str(period) + ' days')
		ibvsp_today.plot(color=get_color(online_ibvsp_change))

		intraday.append(current_account_value)
		intraday_series = pd.Series(intraday)
		plt.subplot2grid((qtt_rows, qtt_elements), (3, 3), rowspan=1, colspan=4)
		plt.title('IBOVESPA today: ' + format_value(online_ibvsp_change) + ' (' + format_value(online_ibvsp_change_percentage) + '%)' )
		ibvsp_intraday_series.plot(color=get_color(online_ibvsp_change))

		plt.pause(0.05)
		#time.sleep(0.1)

	except Exception as e:
                logging.error(e)
