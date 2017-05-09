import nltk
import math
from nltk.corpus import state_union, stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import pandas as pd
import shutil

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk import tokenize
import requests
import json
import os
import re
import codecs

from ifc.db import StockArticle, Stock, Article, Author, ArticleFeature, db
import peewee

def tfidf():
	qry = (StockArticle.select(Article.id, Article.title, Article.content, Article.date, Stock.id.alias('stock_id'), Stock.ticker, StockArticle).join(Stock, on=(StockArticle.stock_id == Stock.id)).join(Article, on=(StockArticle.article_id == Article.id)).where((Stock.ticker == 'GM.N') | (Stock.ticker == 'TGT.N'), Article.date > '2016-01-01').limit(10).naive())
	corpusDict = {article.article_id : article.content for article in qry }
	corpus = corpusDict.values()
	corpusKeys = corpusDict.keys()

	#discard any stop words - saves on processing
	stopset = list(stopwords.words('english'))
	stopset.append('000')
	for i in range(9999):
		stopset.append(str(i))
	vectorizer = TfidfVectorizer(stop_words=stopset, use_idf=True, ngram_range=(2,3))
	
	#matrix of input set
	X = vectorizer.fit_transform(corpus)
	X = X.toarray()
	#print sorted(X[0], reverse=True)
	#print sorted(vectorizer.inverse_transform(X[0]), reverse=True)
	size_matrix = X.shape[0] 
	lsa = TruncatedSVD(n_components=size_matrix, n_iter=100)
	#lsa.fit(X)
	terms = vectorizer.get_feature_names()
	tfidfList = []
	for i, comp in enumerate(X):
		termsInComp = zip(terms,comp)
		sortedTerms = sorted(termsInComp, key=lambda x: x[1], reverse=True) [:10]
		#print "Article %s:" % corpusKeys[i]
		#f = open("processed/%d.txt" % corpusKeys[i], "w")
		
		#List with all the terms gathered from the tfidf vectorizer
		termList = [term[0] + '.' for term in sortedTerms]
		
		# List with Article ID and list of tfidf terms
		tfidfList = [corpusKeys[i],termList]
		vader(tfidfList)
		#for term in tfidfList:
		#	vader(term)
	#return tfidfList
		#print tfidfList
		#for term in sortedTerms:
			#termList = [corpusKeys[i],term[0] + '.']
		#print termList
			#print >> f, term[0] + '.'
			#print term[0]
		#print "   "
def vader(term):
	sentences = []
	#print term[0]
	#file = open(file_path, 'r')
	#base = os.path.basename(file_path)
	#articleID =  os.path.splitext(base)[0]
	
	data_file = term[1]
	#print data_file
	lines_list = data_file
	#lines_list = tokenize.sent_tokenize(data_file)
	#print lines_list
	sentences.extend(lines_list)
	result = {'compound':[], 'neg':[], 'neu':[], 'pos':[] }
	sid = SentimentIntensityAnalyzer()
	for sentence in sentences:
		#print sentence.encode('utf-8')
		ss = sid.polarity_scores(sentence)
		#for k in sorted(ss):
		#	print '{0}: {1}, '.format(k, ss[k]),
		#print ""
		result['compound'].append(ss['compound'])
		result['neg'].append(ss['neg'])
		result['neu'].append(ss['neu'])
		result['pos'].append(ss['pos'])
	vaderList = [sum(result[i]) for i in result.keys()]
	#print vaderList
	list = [term[0],vaderList]
	print list
	resultsKeys = result.keys()	
	db_data = ({'article': list[0], 'negative': list[1][0], 'neutral': list[1][1], 'positive': list[1][2], 'compound': list[1][3]})
	with db.atomic():
			ArticleFeature.insert(db_data).execute()
			print "1"
			
def main():

	tfidf()
	
if __name__== "__main__":
	main()