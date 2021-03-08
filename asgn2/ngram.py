#CMSC 416 Programming Assignment 2
#Austin Beggs 2/13/19
#The goal of this program was to generate sentences using ngrams that were compiled using text files given through the console
#however I couldnt figure out how to get dictionary to work for the probability so it doesnt generate sentences


import sys
import re
import os
import nltk
from nltk import word_tokenize
from nltk import sent_tokenize
from nltk.util import ngrams
from collections import Counter, defaultdict

print ("This program generates random sentences based on an Ngram probability. Created by Austin Beggs")
if len(sys.argv) < 1 :
    exit("please use the command line arguments (ngram.py n m textfiles)")

print ("Command line settings: ngram.py " + sys.argv[1] + " " + sys.argv[2])

n = sys.argv[1]
sentencesToGenerate = sys.argv[2]



#with open(filename) as f:
#    text = f.read()
#sentences = re.split(r' *[\.\?!][\'"\)\]]* *', text)

corpus = []
#path = sys.argv[3]

num = -1
num2 = 3


#looping through the inputfiles and adding them to the corpus
while num == -1 :
    fileName = sys.argv[num2]
    f = open(fileName, encoding="utf8")
    text = f.read()
    lowerCaseText = text.lower()
    lowerCaseText = re.sub(r"[\n]", " ", lowerCaseText)
    lowerCaseText = lowerCaseText[1:]
    #corpus.append(re.findall(r"[\w']+|[.,!?;]", text))
    corpus.append(lowerCaseText)

    if len(sys.argv) > num2 :
        num2 += 1
    else :
        num = 99999


# splitting the corpus into sentences and then padding/appending start and end tags to them 

count = Counter([])
token = nltk.sent_tokenize(lowerCaseText)
token = [re.split(r"[\s]|(?<!\d|')[,.]|[,.](?!\d|')", i) for i in token] 
#grams = [nltk.word_tokenize(token) for i in token]

for i in range(len(token)):
    token[i].insert(0, '<s>') 
    token[i].append('</s>')


history = n-1

probability = defaultdict(lambda: defaultdict(lambda: 0))

#getting the count of each ngram

for i in range(len(token)):
    #token = nltk.word_tokenize(token)
    xgrams = ngrams(tuple(token[i]), n)
    count += Counter(xgrams)

    #for grams in count:
    #    probability[grams] += 1
    

l = count.most_common()


#dict[history][word]
#hdict[history]

#this was where i got lost trying to calculate the probability using a dict

for history in probability:
    total_count = float(sum(probability[history].values()))
    for word in probability[history]:
        probability[history][word] /= total_count


dict(probability["<s>", "it"])

print ("program finished")