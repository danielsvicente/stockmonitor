from datetime import date, timedelta
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web
import time
import numpy as np


# Some initial configurations
plt.style.use('dark_background')
plt.figure().subplots_adjust(hspace=0.5)
plt.ion()
mng = plt.get_current_fig_manager()
#mng.full_screen_toggle()

qgep_stock = 100
pomo_stock = 100
wege_stock = 100
movi_stock = 300
abev_stock = 50

investment_value = 7300.00
remaining_balance = 154.22

start = date.today() - timedelta(days=7)
end = date.today()


def calc_change(previous_close, current_rate):
	change = current_rate - previous_close
	change_percentage = change * 100 / previous_close
	return change, change_percentage

def format_value(value):
	return "{:.2f}".format(value)

while True:

	try:
		qgep = web.get_data_yahoo('QGEP3.SA', start, end)
		pomo = web.get_data_yahoo('POMO4.SA', start, end)
		wege = web.get_data_yahoo('WEGE3.SA', start, end)
		movi = web.get_data_yahoo('MOVI3.SA', start, end)
		abev = web.get_data_yahoo('ABEV3.SA', start, end)

		# Cleaning datasets from possible NaN values
		qgep.fillna(method='ffill', inplace=True)
		pomo.fillna(method='ffill', inplace=True)
		wege.fillna(method='ffill', inplace=True)
		movi.fillna(method='ffill', inplace=True)
		abev.fillna(method='ffill', inplace=True)

		print(qgep)

		qgep_current_rate = qgep.iloc[-1]['Close']
		pomo_current_rate = pomo.iloc[-1]['Close']
		wege_current_rate = wege.iloc[-1]['Close']
		movi_current_rate = movi.iloc[-1]['Close']
		abev_current_rate = abev.iloc[-1]['Close']

		qgep_previous_close = qgep.iloc[-2]['Close']
		pomo_previous_close = pomo.iloc[-2]['Close']
		wege_previous_close = wege.iloc[-2]['Close']
		movi_previous_close = movi.iloc[-2]['Close']
		abev_previous_close = abev.iloc[-2]['Close']

		# EACH SHARE
		qgep_change, qgep_change_percentage = calc_change(qgep_previous_close, qgep_current_rate)
		pomo_change, pomo_change_percentage = calc_change(pomo_previous_close, pomo_current_rate)
		wege_change, wege_change_percentage = calc_change(wege_previous_close, wege_current_rate)
		movi_change, movi_change_percentage = calc_change(movi_previous_close, movi_current_rate)
		abev_change, abev_change_percentage = calc_change(abev_previous_close, abev_current_rate)
		###

		# OVERALL
		current_shares_value = (qgep_current_rate * qgep_stock) + (pomo_current_rate * pomo_stock) + (wege_current_rate * wege_stock) + (movi_current_rate * movi_stock) + (abev_current_rate * abev_stock)
		current_account_value = current_shares_value + remaining_balance
		current_yield_value = current_account_value - investment_value
		current_yield_percentage = (current_account_value * 100 / investment_value) - 100
		###

		print('ABEV3 : ' + format_value(abev_current_rate) + ' ' + format_value(abev_change) + ' (' + format_value(abev_change_percentage) + ')' )
		print('MOVI3 : ' + format_value(movi_current_rate) + ' ' + format_value(movi_change) + ' (' + format_value(movi_change_percentage) + ')' )
		print('POMO4 : ' + format_value(pomo_current_rate) + ' ' + format_value(pomo_change) + ' (' + format_value(pomo_change_percentage) + ')' )
		print('QGEP3 : ' + format_value(qgep_current_rate) + ' ' + format_value(qgep_change) + ' (' + format_value(qgep_change_percentage) + ')' )
		print('WEGE3 : ' + format_value(wege_current_rate) + ' ' + format_value(wege_change) + ' (' + format_value(wege_change_percentage) + ')' )
		print('SHARES TOTAL : ' + format_value(current_shares_value))

		print('ACCOUNT TOTAL : ' + 	format_value(current_account_value) + ' ' + format_value(current_yield_value) + ' (' + format_value(current_yield_percentage) + '%)')

		plt.clf()
		plt.subplot(235)
		plt.title('ABEV3 : ' + format_value(abev_current_rate) + ' ' + format_value(abev_change) + ' (' + format_value(abev_change_percentage) + '%)' )
		abev['Close'].plot()

		plt.subplot(234)
		plt.title('MOVI3 : ' + format_value(movi_current_rate) + ' ' + format_value(movi_change) + ' (' + format_value(movi_change_percentage) + '%)' )

		movi['Close'].plot()

		plt.subplot(232)
		plt.title('POMO4 : ' + format_value(pomo_current_rate) + ' ' + format_value(pomo_change) + ' (' + format_value(pomo_change_percentage) + '%)' )
		pomo['Close'].plot()

		plt.subplot(231)
		plt.title('QGEP3 : ' + format_value(qgep_current_rate) + ' ' + format_value(qgep_change) + ' (' + format_value(qgep_change_percentage) + '%)' )
		qgep['Close'].plot()

		plt.subplot(233)
		plt.title('WEGE3 : ' + format_value(wege_current_rate) + ' ' + format_value(wege_change) + ' (' + format_value(wege_change_percentage) + '%)' )
		wege['Close'].plot()

		plt.pause(0.05)
		#time.sleep(0.1)
		
	except Exception as e:
		print("Failed to pull data from source.")
	
