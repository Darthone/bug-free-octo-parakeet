import time
import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as mplot
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.finance import candlestick_ochl
# custom matplotlib parameters
matplotlib.rcParams.update({'font.size': 9})

stocks = 'AAPL', 'FB', 'UAA'

# compute the n period relative strength indicator
# matploblib finance example
def rsiFunction(prices, n=14):
	deltas = np.diff(prices)
	seed = deltas[:n+1]
	up = seed[seed >= 0].sum()/n
	down = -seed[seed < 0].sum()/n
	rs = up/down
	rsi = np.zeros_like(prices)
	rsi[:n] = 100. - 100./(1. + rs)

	for i in range(n, len(prices)):
		delta = deltas[i-1] # diff is 1 shorter

		if delta > 0:
			upval = delta
			downval = 0.
		else:
			upval = 0.
			downval = -delta

		up = (up * (n - 1) + upval)/n
		down = (down * (n - 1) + downval)/n

		rs = up/down
		rsi[i] = 100. - 100./(1. + rs)

	return rsi

def movingaverage(values, window):
	weights = np.repeat(1.0, window) / window
	# line smoothening
	smas = np.convolve(values, weights, 'valid')
	# list of values being returned as numpy array
	return smas

def graphData(stock, MA1, MA2):
	try:
		s = stock + '.txt'

		# load values and format the date
		date, closePrice, highPrice, lowPrice, openPrice, volume = np.loadtxt(s, delimiter=',', unpack=True, converters={0: mdates.strpdate2num('%Y%m%d')})

		# add dates to data for candlestick to be plotted
		i = 0
		k = len(date)
		candles = []
		while i < k:
			newLine = date[i], openPrice[i], closePrice[i], highPrice[i], lowPrice[i], volume[i]
			candles.append(newLine)
			i = i + 1


		av1 = movingaverage(closePrice, MA1)
		av2 = movingaverage(closePrice, MA2)

		# starting point, plot exactly same amount of data
		SP = len(date[MA2-1:])
		
		label_1 = str(MA1) + ' SMA'
		label_2 = str(MA2) + ' SMA'

		f = mplot.figure()

		# on a 4x4 figure, plot at (0,0)
		a = mplot.subplot2grid((5,4), (1,0), rowspan=4, colspan=4)
		# using matplotlib's candlestick charting
		candlestick_ochl(a, candles[-SP:], width=0.5, colorup='g', colordown='r')
		# moving average applied to data
		a.plot(date[-SP:], av1[-SP:], label=label_1, linewidth=1.5)
		a.plot(date[-SP:], av2[-SP:], label=label_2, linewidth=1.5)
		mplot.ylabel('Stock Price ($) and Volume')
		mplot.legend(loc=9, ncol=2, prop={'size':7}, fancybox=True)
		a.grid(True)


		minVolume = 0
		# rotating angles by 90 degrees to fit properly
		for label in a.xaxis.get_ticklabels():
			label.set_rotation(45)

		# rsi
		rsiCol = 'b'
		c = mplot.subplot2grid((5,4), (0,0), sharex=a, rowspan=1, colspan=4)
		rsi = rsiFunction(closePrice)
		c.plot(date[-SP:], rsi[-SP:], rsiCol, linewidth=1.5)
		c.axhline(70, color=rsiCol)
		c.axhline(30, color=rsiCol)
		c.fill_between(date[-SP:], rsi[-SP:], 70, where=(rsi[-SP:]>=70), facecolor=rsiCol, edgecolor=rsiCol)
		c.fill_between(date[-SP:], rsi[-SP:], 30, where=(rsi[-SP:]<=30), facecolor=rsiCol, edgecolor=rsiCol)

		c.tick_params(axis='x')
		c.tick_params(axis='y')
		c.set_yticks([30,70])
		# mplot.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='lower'))
		mplot.ylabel('RSI')

		# fit 10 dates into graph and formatt properly
		a.xaxis.set_major_locator(mticker.MaxNLocator(10))
		a.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

		avol = a.twinx()
		avol.fill_between(date[-SP:], minVolume, volume[-SP:], facecolor='b', alpha=.5)
		avol.axes.yaxis.set_ticklabels([])
		avol.grid(False)
		avol.set_ylim(0,2*volume.max())
		avol.tick_params(axis='x')
		avol.tick_params(axis='y')

		# subplot profile parameters
		mplot.subplots_adjust(left=.10, bottom=.19, right=.93, top=.95, wspace=.20, hspace=.07)
		# plot profiling
		mplot.xlabel('Date (YYY-MM-DD)')
		# mplot.ylabel('Stock Price ($)')
		mplot.suptitle(stock + ' Stock Price')
		# remove x axis from first graph, used at bottom already
		mplot.setp(c.get_xticklabels(), visible=False)
		# adjusting plots in a clean manner
		mplot.subplots_adjust(left=.09, bottom=.18, right=.94, top=.94, wspace=.20, hspace=0)
		mplot.show()


		f.savefig('financial_graph.png')		


	except Exception, e:
		print 'error in main:', str(e)


graphData('AAPL', 10, 30)