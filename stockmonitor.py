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
            print(stock['ticker'], trade['ticker'])
            if stock['ticker'] == trade['ticker']:
                if trade['type'] == 'BUY':
                    stock['quantity'] = stock['quantity'] + int(trade['quantity'])
                    stock['total_invested'] = stock['total_invested'] + (int(trade['quantity']) * float(trade['price']))
                else:
                    stock['quantity'] = stock['quantity'] - int(trade['quantity'])
                    stock['total_invested'] = stock['total_invested'] - (int(trade['quantity']) * float(trade['price']))
                if stock['quantity'] > 0:
                    stock['average_price'] = stock['total_invested'] / stock['quantity']
                new_stock = False
        if new_stock is True:
            ti = int(trade['quantity']) * float(trade['price'])
            stocks.append(dict(ticker=trade['ticker'], quantity=int(trade['quantity']), average_price=float(trade['price']), total_invested=ti))


abev_stock = 50
movi_stock = 300
pomo_stock = 100
goau_stock = 100
wege_stock = 130

abev_buy_average = (980.00) / 50
movi_buy_average = (848.00 + 2198.00) / 300
pomo_buy_average = (401.00) / 100
goau_buy_average = (975.00) / 100
wege_buy_average = (1989.00) / 100

investment_value = float(total_deposited)
remaining_balance = float(available_to_invest)

days = 30
start = date.today() - timedelta(days=days)
end = date.today()

intraday = []
historical = []

def calc_change(previous_close, current_rate):
	change = current_rate - previous_close
	change_percentage = change * 100 / previous_close
	return change, change_percentage

def format_value(value):
	return "{:.2f}".format(value)

while True:

	try:
		print("Pulling ABEV3")
		abev = web.get_data_yahoo('ABEV3.SA', start, end)
		print("Pulling MOVI3")
		movi = web.get_data_yahoo('MOVI3.SA', start, end)
		print("Pulling POMO4")
		pomo = web.get_data_yahoo('POMO4.SA', start, end)
		print("Pulling GOAU4")
		goau = web.get_data_yahoo('GOAU4.SA', start, end)
		print("Pulling WEGE3")
		wege = web.get_data_yahoo('WEGE3.SA', start, end)

		abev['Diff'] = abev['Close'].diff()
		movi['Diff'] = movi['Close'].diff()
		pomo['Diff'] = pomo['Close'].diff()
		goau['Diff'] = goau['Close'].diff()
		wege['Diff'] = wege['Close'].diff()

		abev['Total'] = abev['Close'] * abev_stock
		movi['Total'] = movi['Close'] * movi_stock
		pomo['Total'] = pomo['Close'] * pomo_stock
		goau['Total'] = goau['Close'] * goau_stock
		wege['Total'] = wege['Close'] * wege_stock

		historical = abev['Total'] + movi['Total'] + pomo['Total'] + goau['Total'] + wege['Total']
		
		'''
		abev['Diff'] = pd.Series(abev['Close'] - abev_buy_average, index=abev.index)
		movi['Diff'] = pd.Series(movi['Close'] - movi_buy_average, index=movi.index)
		pomo['Diff'] = pd.Series(pomo['Close'] - pomo_buy_average, index=pomo.index)
		goau['Diff'] = pd.Series(goau['Close'] - goau_buy_average, index=goau.index)
		wege['Diff'] = pd.Series(wege['Close'] - wege_buy_average, index=wege.index)
		'''

		# Cleaning datasets from possible NaN values
		abev.fillna(method='ffill', inplace=True)
		movi.fillna(method='ffill', inplace=True)
		pomo.fillna(method='ffill', inplace=True)
		goau.fillna(method='ffill', inplace=True)
		wege.fillna(method='ffill', inplace=True)

		goau_current_rate = goau.iloc[-1]['Close']
		pomo_current_rate = pomo.iloc[-1]['Close']
		wege_current_rate = wege.iloc[-1]['Close']
		movi_current_rate = movi.iloc[-1]['Close']
		abev_current_rate = abev.iloc[-1]['Close']

		goau_previous_close = goau.iloc[-2]['Close']
		pomo_previous_close = pomo.iloc[-2]['Close']
		wege_previous_close = wege.iloc[-2]['Close']
		movi_previous_close = movi.iloc[-2]['Close']
		abev_previous_close = abev.iloc[-2]['Close']

		# EACH SHARE
		goau_change, goau_change_percentage = calc_change(goau_previous_close, goau_current_rate)
		pomo_change, pomo_change_percentage = calc_change(pomo_previous_close, pomo_current_rate)
		wege_change, wege_change_percentage = calc_change(wege_previous_close, wege_current_rate)
		movi_change, movi_change_percentage = calc_change(movi_previous_close, movi_current_rate)
		abev_change, abev_change_percentage = calc_change(abev_previous_close, abev_current_rate)
		###

		# OVERALL
		current_shares_value = (goau_current_rate * goau_stock) + (pomo_current_rate * pomo_stock) + (wege_current_rate * wege_stock) + (movi_current_rate * movi_stock) + (abev_current_rate * abev_stock)
		current_account_value = current_shares_value + remaining_balance
		current_yield_value = current_account_value - investment_value
		current_yield_percentage = (current_account_value * 100 / investment_value) - 100

		last_shares_value = (goau_previous_close * goau_stock) + (pomo_previous_close * pomo_stock) + (wege_previous_close * wege_stock) + (movi_previous_close * movi_stock) + (abev_previous_close * abev_stock)
		current_day_yield_value = current_shares_value - last_shares_value
		current_day_yield_percentage = (current_shares_value * 100 / last_shares_value) - 100
		
		###

		print('ABEV3 : ' + format_value(abev_current_rate) + ' ' + format_value(abev_change) + ' (' + format_value(abev_change_percentage) + ')' )
		print('MOVI3 : ' + format_value(movi_current_rate) + ' ' + format_value(movi_change) + ' (' + format_value(movi_change_percentage) + ')' )
		print('POMO4 : ' + format_value(pomo_current_rate) + ' ' + format_value(pomo_change) + ' (' + format_value(pomo_change_percentage) + ')' )
		print('GOAU4 : ' + format_value(goau_current_rate) + ' ' + format_value(goau_change) + ' (' + format_value(goau_change_percentage) + ')' )
		print('WEGE3 : ' + format_value(wege_current_rate) + ' ' + format_value(wege_change) + ' (' + format_value(wege_change_percentage) + ')' )
		print('SHARES TOTAL : ' + format_value(current_shares_value))

		print('ACCOUNT TOTAL : ' + 	format_value(current_account_value) + ' ' + format_value(current_yield_value) + ' (' + format_value(current_yield_percentage) + '%)')
		intraday.append(current_account_value)

		plt.clf()

		# Row 1 - Close prices
		plt.subplot2grid((3, 5), (0, 0), rowspan=1, colspan=1)
		plt.title('ABEV3 : ' + format_value(abev_current_rate) + ' ' + format_value(abev_change) + ' (' + format_value(abev_change_percentage) + '%)' )
		abev['Close'].plot(color='cyan')

		plt.subplot2grid((3, 5), (0, 1), rowspan=1, colspan=1)
		plt.title('MOVI3 : ' + format_value(movi_current_rate) + ' ' + format_value(movi_change) + ' (' + format_value(movi_change_percentage) + '%)' )
		movi['Close'].plot(color='cyan')

		plt.subplot2grid((3, 5), (0, 2), rowspan=1, colspan=1)
		plt.title('POMO4 : ' + format_value(pomo_current_rate) + ' ' + format_value(pomo_change) + ' (' + format_value(pomo_change_percentage) + '%)' )
		pomo['Close'].plot(color='cyan')

		plt.subplot2grid((3, 5), (0, 3), rowspan=1, colspan=1)
		plt.title('GOAU4 : ' + format_value(goau_current_rate) + ' ' + format_value(goau_change) + ' (' + format_value(goau_change_percentage) + '%)' )
		goau['Close'].plot(color='cyan')

		plt.subplot2grid((3, 5), (0, 4), rowspan=1, colspan=1)
		plt.title('WEGE3 : ' + format_value(wege_current_rate) + ' ' + format_value(wege_change) + ' (' + format_value(wege_change_percentage) + '%)' )
		wege['Close'].plot(color='cyan')

		# Row 2 - Diff
		plt.subplot2grid((3, 5), (1, 0), rowspan=1, colspan=1)
		plt.tick_params(
		    axis='x',          # changes apply to the x-axis
		    which='both',      # both major and minor ticks are affected
		    bottom='off',      # ticks along the bottom edge are off
		    top='off',         # ticks along the top edge are off
		    labelbottom='off') # labels along the bottom edge are off
		abev['Diff'].plot(kind='bar', color='cyan')

		plt.subplot2grid((3, 5), (1, 1), rowspan=1, colspan=1)
		plt.tick_params(axis='x', which='both', bottom='off', top='off', labelbottom='off')
		movi['Diff'].plot(kind='bar', color='cyan')

		plt.subplot2grid((3, 5), (1, 2), rowspan=1, colspan=1)
		plt.tick_params(axis='x', which='both', bottom='off', top='off', labelbottom='off')
		pomo['Diff'].plot(kind='bar', color='cyan')

		plt.subplot2grid((3, 5), (1, 3), rowspan=1, colspan=1)
		plt.tick_params(axis='x', which='both', bottom='off', top='off', labelbottom='off')
		goau['Diff'].plot(kind='bar', color='cyan')

		plt.subplot2grid((3, 5), (1, 4), rowspan=1, colspan=1)
		plt.tick_params(axis='x', which='both', bottom='off', top='off', labelbottom='off')
		wege['Diff'].plot(kind='bar', color='cyan')
 
		# Row 3 - Historical and Intraday
		hist_series = pd.Series(historical)
		plt.subplot2grid((3, 5), (2, 0), rowspan=1, colspan=2)
		plt.title('Total : ' + format_value(current_account_value) + ' ' + format_value(current_yield_value) + ' (' + format_value(current_yield_percentage) + '%)' )
		hist_series.plot(color='cyan')		

		intraday_series = pd.Series(intraday)
		plt.subplot2grid((3, 5), (2, 2), rowspan=1, colspan=3)
		plt.title('No dia : ' + format_value(current_day_yield_value) + ' (' + format_value(current_day_yield_percentage) + '%)' )
		intraday_series.plot(color='cyan')
		
		plt.pause(0.05)
		#time.sleep(0.1)
		
	except Exception as e:
		print(e)


