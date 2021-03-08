# NLP assignment 5 - Sentiment (sentiment.py)
# Austin Beggs - 3/31/2019

# The goal of this program was to take in training data and learn sentiment from this data,
# then based on log probabilities apply the wsd to a testing input that was included in
# the sentiment-train and sentiment-test .txt files. To run this program you must include both of these
# in the arguments. The algorithm used to solve this was to take in the training data by removing some
# characters/lines that werent needed, loop through and process the data into dictionaries keeping track of the features (only bag of words)
# and what sentiment they were associated with. Then calculate the log probability of tags and store them in a sorted dictionary.
# Lastly the program proccess the test data, pulls out the sentiment for each instance and then runs through a loop runs in order through
# the log probabilities and when there is a match, that sentiment is assigned/output to a file 
# using a decision list. The output was then compared to the key given using a 2nd program called scorer.py 

#Example input and output 
#to run the program use 
#          python sentiment.py sentiment-train.txt sentiment-test.txt my-model.txt > my-sentiment-answers.txt
#on the command line, input files being corpus data that contains context and instance ids
#output would be my-line-answers.txt which formats answers like this
#          <answer instance="line-n.w8_059:8174:" senseid="positive"/>

#stats:
#Decision list
#Number Correct : 140
#Number Total : 232
#Percent : 60.3448275862069 %    I tried to get better than this but couldnt get it more than 1-2% higher
#Confusion matrix:
#Predicted  negative  positive
#Actual
#negative         37        35
#positive         57       103

#Compared to baseline of Percent Correct: 68.965517241 %



import sys
from sys import argv
import re
import numpy as np
import math


#command line arguments
train = str(argv[1]) # Training Data
test = str(argv[2])  # Testing Data
k = 100 # k value
positive = 'positive'
negative = 'negative'


#opening training file and manipulating data
File = open(train, 'r') 
trainData = File.read() 
trainData = re.sub('<\/?context>\s|<\/instance>\s','', trainData) # deletes all context lines
trainData = re.split('\n', trainData) # line by line
trainData = trainData[2:len(trainData)-2] #</lexelt> and </corpus> 


#intialize dict
featureList = {}
featureList["+-k W"] = {}


length = len(trainData)-1

#loop through training data
x = 0
while (x < length):
    instanceid1 = re.search(r'".*"', trainData[x]) 
    instanceid = instanceid1.group(0)
    wordSense1 = re.search(r'(positive)|(negative)',trainData[x+1]) 
    wordSense = wordSense1.group(0)

    #fix up sentence
    sentence = trainData[x+2]
    sentence = re.sub('<s>|</s>|<p>|</p>|<@>', '', sentence) 
    sentence = re.sub('http\S+', '', sentence)   #removing links
    sentence = re.sub('@\S+', '', sentence) 
    sentence = re.sub('-|--', ' ', sentence)
    sentence = re.sub(r"\/|\”|\“|\(|\)|\:|\;|\’|\‘|\.|!|,|\?", '', sentence)
    sentence = re.sub("\s+" , " ", sentence) 
    sentence = sentence.lower() 
    splitSentence = re.split(r'\s+', sentence)
    
    #removing stopwords made my accuracy go down 
    #stopwordsArray = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
    #splitSentence = [word for word in splitSentence if not word in stopwordsArray]
    splitSentence = splitSentence[1:-1]

    #incrementing and getting index of line/lines   
    x+=3
    index = 0
    #for place in range (0,len(splitSentence)):
    #    if splitSentence[place] == "<head>line<head>" or splitSentence[place] == "<head>lines<head>":
    #        index = place
    place = index


    # bag of words
    leftIndex = place-k #index - k for left
    rightIndex = place+k #index + k for right
    if leftIndex < 0:
        leftIndex = 0
    if rightIndex > len(splitSentence):
        rightIndex = len(splitSentence)-1 
    kWordsList = splitSentence[leftIndex:rightIndex]

    try:
        # looping through
        for word in kWordsList:
            if word not in featureList['+-k W'].keys():
                featureList['+-k W'][word] = {}
            if wordSense not in featureList['+-k W'][word].keys():
                featureList['+-k W'][word][wordSense] = 1
            else:
                featureList['+-k W'][word][wordSense] += 1
    except:
        
        pass

#initializing dictionary
rankingDictonary = {}
rankingDictonary["+-k W"] = {}

#ranking and sorting features
for featType in featureList:
    for currentFeature in featureList[featType]:

        #zeroing out for features that only saw positive or negative
        if(positive not in featureList[featType][currentFeature].keys()):
            featureList[featType][currentFeature][positive] = 0
        if(negative not in featureList[featType][currentFeature].keys()):
            featureList[featType][currentFeature][negative] = 0

        #getting numbers for log 
        positiveCount = featureList[featType][currentFeature][positive]       
        negativeCount = featureList[featType][currentFeature][negative]        
        sum1 = positiveCount+negativeCount                                                

        if currentFeature not in rankingDictonary[featType]:         
            rankingDictonary[featType][currentFeature] = {}
        #cant divide by 0 
        positiveCount = positiveCount + 0.1
        negativeCount = negativeCount + 0.1
        sum1 = sum1 + 0.1
        rankingDictonary[featType][currentFeature] = abs(math.log((positiveCount/sum1)/(negativeCount/sum1)))

#Sorting
rankedOutput = {}
for feature in rankingDictonary:
    for word in rankingDictonary[feature]:
        rankedOutput[(feature,word)] = rankingDictonary[feature][word]
sortedDictionary = {}
sortedDictionary = sorted(rankedOutput.items(), key=lambda x: (x[1],x[0]), reverse=True)

# Output to my-model.txt
File2 = open(str(argv[3]), "w+")
for x in sortedDictionary:
    File2.write(str(x) + "\n")



#reading test data
File = open(test, 'r') # Open file
testData = File.read() # Read file
testData = re.sub('</?context>\s|</instance>\s','', testData) # removing context lines
testData = re.split('\n', testData) # Split up everything by line
testData = testData[2:len(testData)-2] #</lexelt> and </corpus> 


length = len(testData)-1
testDictionary = {}

#looping through the test data
x = 0
while (x < length):
    instanceid1 = re.search(r'".*"', testData[x]) 
    instanceid = instanceid1.group(0)

    #initializing dict
    testDictionary[instanceid] = {}
    testDictionary[instanceid]["+-k W"] = {}

    #cleaning up sentence
    sentence = testData[x+1] # The sentence itself
    sentence = re.sub('<s>|</s>|<p>|</p>|<@>', '', sentence) 
    sentence = re.sub(r"\/|\”|\“|\(|\)|\:|\;|\"|\’|\‘|\.|!|,|\?", '', sentence)
    sentence = re.sub('-|--', ' ', sentence)
    sentence = re.sub('http\S+', '', sentence)   #removing links
    sentence = re.sub('@\S+', '', sentence) 
    sentence = re.sub("\s+" , " ", sentence) 
    sentence = sentence.lower() 
    splitSentence = re.split(r'\s+', sentence)
    splitSentence = splitSentence[1:-1]
    
    #getting index of line/lines
    index = 0
    place = index

  
    # +-k W 
    rightIndex = place+k
    leftIndex = place-k

    if rightIndex > len(splitSentence):
        rightIndex = len(splitSentence)-1 
    if leftIndex < 0:
        leftIndex = 0
    
    kWordsList = splitSentence[leftIndex:rightIndex]
    if '<head>' in kWordsList:
        kWordsList.remove('<head>')

    try:
        # For every word in the list from leftIndex to rightIndex
        testDictionary[instanceid]['+-k W'] = kWordsList
    except:
        pass
    x+=2 #increment counter


#I think something with my file io is messed up because I cant redirect print with >
#fileString = "my-sentiment-answers.txt"
#outputFile = open(fileString,"w") 

#decision list
#loop through every instance
for _ in testDictionary:
    output = "<answer instance=" + str(_)+ " senseid=\"" 
    wordSenseFound = False
    #looping through sorteddict to find highest value of log prob
    for feature in sortedDictionary:
        Ftype = feature[0][0] 
        wordFromFeature = feature[0][1]  
        #if the feature is k
        if (Ftype == '+-k W'):
            for testWords in testDictionary[_][Ftype]:
                if wordFromFeature in testWords: 
                    if featureList[Ftype][wordFromFeature][negative] > featureList[Ftype][wordFromFeature][positive]:
                        output = output + "negative\"/>"
                    else:
                        output = output + "positive\"/>"
                    wordSenseFound = True
                    break
         #had an issue with the for loop/// any feature other than +-k comes down here
        else:
            try: 
                testWords = testDictionary[_][Ftype][:]
            except:
                pass
            if (wordFromFeature == testWords): 
                if featureList[Ftype][wordFromFeature][negative] > featureList[Ftype][wordFromFeature][positive]:
                    output = output + "negative\"/>"
                else:
                    output = output + "positive\"/>"
                wordSenseFound = True
        if (wordSenseFound == True):
            break

    #default value    
    if not wordSenseFound:
        output = output + "positive\"/>"

    print(output) 
    #outputFile.write(output)
#outputFile.close()

