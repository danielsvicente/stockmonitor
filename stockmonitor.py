from datetime import date, timedelta
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web
import time
import numpy as np
import json


# Some initial configurations for the gui
plt.style.use('dark_background')
plt.figure().subplots_adjust(hspace=0.5)
plt.ion()
mng = plt.get_current_fig_manager()
#mng.full_screen_toggle()


# Access data from json file
with open("data.json", "r") as data_file:
    data = json.load(data_file)

# Process data
total_deposited = data["total_deposited"]
available_to_invest = data["available_to_invest"]
transactions = data["transactions"]
earings = data["earnings"]
stocks = []
# Fill list of stocks
for transaction in transactions:
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
                if stock['quantity'] > 0:
                    stock['average_price'] = stock['total_invested'] / stock['quantity']
                new_stock = False
        if new_stock is True:
            ti = trade['quantity'] * trade['price']
            stocks.append(dict(ticker=trade['ticker'], yahoo_id=trade["yahoo_id"], quantity=trade['quantity'], average_price=trade['price'], total_invested=ti))

print(json.dumps(stocks, indent=4))

days = 30
start = date.today() - timedelta(days=days)
end = date.today()

intraday = []

def calc_change(previous_close, current_rate):
	change = current_rate - previous_close
	change_percentage = change * 100 / previous_close
	return change, change_percentage

def format_value(value):
	return "{:.2f}".format(value)

while True:

	try:

		current_shares_value = 0
		last_shares_value = 0
		historical = pd.Series()

		plot_column = 0

		plt.clf()

		for stock in stocks:
			if stock["quantity"] > 0:
				print("Pulling", stock["yahoo_id"])

				online_data = web.get_data_yahoo(str(stock["yahoo_id"]), start, end)

				online_data['Diff'] = online_data['Close'].diff()
				online_data['Total'] = online_data['Close'] * stock["quantity"]

				# Cleaning datasets from possible NaN values
				online_data.fillna(method='ffill', inplace=True)

				online_data_current_rate = online_data.iloc[-1]['Close']
				online_data_previous_close = online_data.iloc[-2]['Close']
				online_data_change, online_data_change_percentage = calc_change(online_data_previous_close, online_data_current_rate)
				
				current_shares_value = current_shares_value + (online_data_current_rate * stock["quantity"])
				last_shares_value = last_shares_value + (online_data_previous_close * stock["quantity"])

				print(stock["ticker"] + format_value(online_data_current_rate) + ' ' + format_value(online_data_change) + ' (' + format_value(online_data_change_percentage) + ')' )

				if historical.empty:
					historical = online_data["Total"]
				else:
					historical = historical + online_data["Total"]

				# Row 1 - Close prices
				plt.subplot2grid((3, 5), (0, plot_column), rowspan=1, colspan=1)
				plt.title(stock["ticker"] + ': ' + format_value(online_data_current_rate) + ' ' + format_value(online_data_change) + ' (' + format_value(online_data_change_percentage) + '%)' )
				online_data['Close'].plot(color='cyan')

				# Row 2 - Diff
				plt.subplot2grid((3, 5), (1, plot_column), rowspan=1, colspan=1)
				plt.tick_params(
				    axis='x',          # changes apply to the x-axis
				    which='both',      # both major and minor ticks are affected
				    bottom='off',      # ticks along the bottom edge are off
				    top='off',         # ticks along the top edge are off
				    labelbottom='off') # labels along the bottom edge are off
				online_data['Diff'].plot(kind='bar', color='cyan')

				plot_column = plot_column + 1

		plt.pause(0.05)

		current_account_value = current_shares_value + available_to_invest
		current_yield_value = current_account_value - total_deposited
		current_yield_percentage = (current_account_value * 100 / total_deposited) - 100
		
		current_day_yield_value = current_shares_value - last_shares_value
		current_day_yield_percentage = (current_shares_value * 100 / last_shares_value) - 100
		
		print('SHARES TOTAL : ' + format_value(current_shares_value))
		print('ACCOUNT TOTAL : ' + 	format_value(current_account_value) + ' ' + format_value(current_yield_value) + ' (' + format_value(current_yield_percentage) + '%)')

		# Row 3 - Historical and Intraday
		plt.subplot2grid((3, 5), (2, 0), rowspan=1, colspan=2)
		plt.title('Total : ' + format_value(current_account_value) + ' ' + format_value(current_yield_value) + ' (' + format_value(current_yield_percentage) + '%)' )
		historical.plot(color='cyan')		

		intraday.append(current_account_value)
		intraday_series = pd.Series(intraday)
		plt.subplot2grid((3, 5), (2, 2), rowspan=1, colspan=3)
		plt.title('No dia : ' + format_value(current_day_yield_value) + ' (' + format_value(current_day_yield_percentage) + '%)' )
		intraday_series.plot(color='cyan')
		
		plt.pause(0.05)
		#time.sleep(0.1)

	except Exception as e:
		print(e)


