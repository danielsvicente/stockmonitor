from datetime import date, timedelta
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web
import time
import numpy as np
import json
import os 

# Some initial configurations for the gui

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
transactions = data["transactions"]
earnings = data["earnings"]
earings = data["earnings"]
stocks = []
total_fees = 0.00
total_earning = 0.00

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
                if stock['quantity'] > 0:
                    stock['average_price'] = stock['total_invested'] / stock['quantity']
                new_stock = False
        if new_stock is True:
            ti = trade['quantity'] * trade['price']
            stocks.append(dict(ticker=trade['ticker'], yahoo_id=trade["yahoo_id"], quantity=trade['quantity'], average_price=trade['price'], total_invested=ti, day_price_list=[]))

# Calculate total received from the companies to date
for item in earnings:
    total_earning = total_earning + item['value']

print(json.dumps(stocks, indent=4))

print('TOTAL PAID FEES TO DATE: ', str(total_fees))
print('TOTAL RECEIVED TO DATE: ', str(total_earning))

days = 90 
start = date.today() - timedelta(days=days)
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

while True:

	try:

		current_shares_value = 0
		last_shares_value = 0
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
				stock["day_price_list"].append(current_shares_value)
				day_price_list_series = pd.Series(stock["day_price_list"])
				
				# Console log
				print(stock["ticker"] + format_value(online_data_current_rate) + ' ' + format_value(online_data_change) + ' (' + format_value(online_data_change_percentage) + ')' )

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
		current_yield_percentage = (current_account_value * 100 / total_deposited) - 100
		
		current_day_yield_value = current_shares_value - last_shares_value
		current_day_yield_percentage = (current_shares_value * 100 / last_shares_value) - 100
		
		print('SHARES TOTAL : ' + format_value(current_shares_value))
		print('ACCOUNT TOTAL : ' + 	format_value(current_account_value) + ' ' + format_value(current_yield_value) + ' (' + format_value(current_yield_percentage) + '%)')

		# Row 3 - Historical and Intraday

		plt.subplot2grid((qtt_rows, qtt_elements), (2, 0), rowspan=1, colspan=2)
		plt.title('Total : ' + format_value(current_account_value) + ' ' + format_value(current_yield_value) + ' (' + format_value(current_yield_percentage) + '%)' )
		historical.plot(color=get_color(current_yield_value))		

		intraday.append(current_account_value)
		intraday_series = pd.Series(intraday)
		plt.subplot2grid((qtt_rows, qtt_elements), (2, 2), rowspan=1, colspan=3)
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

		plt.subplot2grid((qtt_rows, qtt_elements), (3, 0), rowspan=1, colspan=2)
		plt.title('IBOVESPA ' + str(days) + ' days')
		ibvsp_today.plot(color=get_color(online_ibvsp_change))		

		intraday.append(current_account_value)
		intraday_series = pd.Series(intraday)
		plt.subplot2grid((qtt_rows, qtt_elements), (3, 2), rowspan=1, colspan=3)
		plt.title('IBOVESPA today: ' + format_value(online_ibvsp_change) + ' (' + format_value(online_ibvsp_change_percentage) + '%)' )
		ibvsp_intraday_series.plot(color=get_color(online_ibvsp_current_rate))

		plt.pause(0.05)
		#time.sleep(0.1)

	except Exception as e:
		print(e)


