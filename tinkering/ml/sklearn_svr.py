#!/usr/bin/env python -W ignore::DeprecationWarning
import numpy as np
import pandas as pd
from sklearn import preprocessing, cross_validation, neighbors, svm, metrics, grid_search
import peewee
from peewee import *
import ifc.ta as ta
import math

def addDailyReturn(dataset):
	"""
	Adding in daily return to create binary classifiers (Up or Down in relation to the previous day)
	"""

	#will normalize labels
	le = preprocessing.LabelEncoder()

	#print "dataset['Adj_Close']\n", dataset['Adj_Close'][:5]
	
	#print "dataset['Adj_Close'].shift(-1)\n", dataset['Adj_Close'].shift(1)[:5]

	dataset['UpDown'] = (dataset['Adj_Close']-dataset['Adj_Close'].shift(1))/dataset['Adj_Close'].shift(1)
	#print dataset['UpDown'][240:]

	# will be denoted by 3 when transformed
	dataset.UpDown[dataset.UpDown > 0] = "sell"

	dataset.UpDown[dataset.UpDown == 0] = "hold"

	dataset.UpDown[dataset.UpDown < 0] = "buy"
	#print dataset['UpDown'][:10]
	dataset.UpDown = le.fit(dataset.UpDown).transform(dataset.UpDown)

	#print dataset['UpDown']

accuracies = []

def preProcessing(stock_name, start_date, end_date):
	"""
	Clean up data to allow for classifiers to predict
	"""
	x = ta.get_series(stock_name, start_date, end_date)
	x.run_calculations()                            
	x.trim_fat()                                    
	df = x.df
	#df = pd.read_csv(csv)
	addDailyReturn(df)
	
	#The columns left will be the ones that are being used to predict
	df.drop(['Date'], 1, inplace=True)
	df.drop(['Low'], 1, inplace=True)
	df.drop(['Volume'], 1, inplace=True)
	#df.drop(['Open'], 1, inplace=True)
	#df.drop(['Adj_Close'],1, inplace=True)
	df.drop(['Close'],1, inplace=True)
	df.drop(['High'],1, inplace=True)
	df.drop(['mavg_10'],1, inplace=True)
	df.drop(['mavg_30'],1, inplace=True)
	df.drop(['rsi_14'],1, inplace=True)
	
	return df

def regressorOp(x, y):
	"""
	This will optimize the parameters for the algo
	"""
	regr_rbf = svm.SVR(kernel="rbf")
	C = [1000, 10, 1]
	gamma = [0.005, 0.004, 0.003, 0.002, 0.001]
	epsilon = [0.1, 0.01]
	parameters = {"C":C, "gamma":gamma, "epsilon":epsilon}
	
	gs = grid_search.GridSearchCV(regr_rbf, parameters, scoring="r2")	
	gs.fit(x, y)

	print "Best Estimator:\n", gs.best_estimator_
	print "Type: ", type(gs.best_estimator_)

	return gs.best_estimator_

for i in range(1):
	#calling in date ranges plus stock name to be pulled
	ticker = raw_input('Enter a stock ticker then press "Enter":\n')	

	train_df = preProcessing(ticker, "2015-04-17", "2016-04-17")
	test_df = preProcessing(ticker, "2016-04-17", "2017-04-17")

	print "-----------------------------------------"
	print "test_df[:5]:"
	print test_df[:5]	

	# separating the binary predictor into different arryays so the algo knows what to predict on
	X_train = np.array(train_df.drop(['UpDown'],1))
	y_train = np.array(train_df['UpDown'])
	X_test = np.array(test_df.drop(['UpDown'],1))
	y_test = np.array(test_df['UpDown'])

	#print test_df[:240]

	#X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.5)
	
	# regression optimization 
	clf = regressorOp(X_train, y_train)
	clf.fit(X_train,y_train)
	
	y_pred = clf.predict(X_test)

	accuracy = clf.score(X_test,y_test)
	variance = metrics.explained_variance_score(y_test, y_pred)

	# iterate and print average accuracy rate
	print "---------------------------------------"
	print "accuracy: " + str(accuracy)
	print "\nvariance: " + str(variance)
	accuracies.append(accuracy)	

	# test value
	test_set = np.array([[100,100],[0,0],[45, 42],[6,6]])
	print "--------------------------------------"
	print "np.array([100,100],[0,0],[45, 42],[6,6]])"
	prediction = clf.predict(test_set)
	
	print "--------------------------------------"
	print "prediction: "
	print prediction
	
#print sum(accuracies)/len(accuracies)
