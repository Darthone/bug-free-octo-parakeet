import nltk
import math
from nltk.corpus import state_union, stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import pandas as pd

#State of the Union Addresses
train_text = open("target1.txt") 
train_text2 = open("target2.txt")

temp_train_text = train_text.readlines()
print temp_train_text
str1 = ''.join(temp_train_text)
#print type(temp_train_text)
temp_train_text2 = train_text2.readlines()
str2 = ''.join(temp_train_text2)

#preprocessing
#tokenize by word - this is the Bag of Words
tokenized = word_tokenize(str1)
tokenized2 = word_tokenize(str2)

corpus = [str1, str2]

#print corpus[0]

#discard any stop words - saves on processing
stopset = set(stopwords.words('english'))

vectorizer = TfidfVectorizer(stop_words=stopset, use_idf=True)

X = vectorizer.fit_transform(corpus)

print X[0]

size_matrix = X.shape[0] 

lsa = TruncatedSVD(n_components=size_matrix, n_iter=100)
lsa.fit(X)

print lsa.components_[0]

terms = vectorizer.get_feature_names()
for i, comp in enumerate(lsa.components_):
	termsInComp = zip(terms,comp)
	sortedTerms = sorted(termsInComp, key=lambda x: x[1], reverse=True) [:10]
	print "Article %d:" % i
	for term in sortedTerms:
		print term[0]
	print "   "