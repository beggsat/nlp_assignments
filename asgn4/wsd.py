# NLP assignment 4 - WSD (wsd.py)
# Austin Beggs - 3/31/2019

#before the main comment I wanted to say at least running on my machine I couldnt figure out how to get the output file to appear to the same directory as wsd.py
#it would place the file outside of the folder that wsd.py was in. Im not sure if this will happen for you but just a heads up it does output
# ie if it was in documents/nlp/asgn4 the file would appear in documents/nlp

# The goal of this program was to take in training data and learn word sense from this data,
# then based on log probabilities apply the wsd to a testing input  that was included in
# the line-train and line-text .txt files. To run this program you must include both of these
# in the arguments. The algorithm used to solve this was to take in the training data by removing some
# characters/lines that werent needed, loop through and process the data into dictionaries keeping track of the features
# and what sense they were associated with. Then calculate the log probability of tags and store them in a sorted dictionary.
# Lastly the program proccess the test data, pulls out the senses for each instance and then runs through a loop runs in order through
# the log probabilities and when there is a match, that sense is assigned/output to a file 
# using a decision list. The  output was then compared to the key given using a 2nd program called scorer.py 

#Example input and output 
#to run the program use 
#          python3 wsd.py line-train.txt line-test.txt my-model.txt > my-line-answers.txt
#on the command line, input files being corpus data that contains context and instance ids
#output would be my-line-answers.txt which formats answers like this
#          <answer instance="line-n.w8_059:8174:" senseid="phone"/>

#stats:
#Decision list
#Percent Correct : 85.71428571428571
#Confusion matrix:
#Predicted  phone  product
#Actual                   
#phone         59       13
#product        5       49


#Compared to baseline of Percent Correct: 57.14285714285714



import sys
from sys import argv
import re
import numpy as np
import math


#command line arguments
train = str(argv[1]) # Training Data
test = str(argv[2])  # Testing Data
k = 5 # k value
phone = 'phone'
product = 'product'


#opening training file and manipulating data
File = open(train, 'r') 
trainData = File.read() 
trainData = re.sub('<\/?context>\s|<\/instance>\s','', trainData) # deletes all context lines
trainData = re.split('\n', trainData) # line by line
trainData = trainData[2:len(trainData)-2] #</lexelt> and </corpus> 


#intialize dict
featureList = {}
featureList["+1 W"] = {}
featureList["-1 W"] = {}
featureList["-1 +1"] = {}
featureList["+1 +2"] = {}
featureList["-2 -1"] = {}
featureList["+-k W"] = {}


length = len(trainData)-1

#loop through training data
x = 0
while (x < length):
    instanceid1 = re.search(r'".*"', trainData[x]) 
    instanceid = instanceid1.group(0)
    wordSense1 = re.search(r'(phone)|(product)',trainData[x+1]) 
    wordSense = wordSense1.group(0)

    #fix up sentence
    sentence = trainData[x+2]
    sentence = re.sub('<s>|</s>|<p>|</p>|<@>', '', sentence) 
    sentence = re.sub(r"\/|\”|\“|\(|\)|\:|\;|\"|\’|\‘|\.|!|,|\?|\'", '', sentence)
    sentence = re.sub("\s+" , " ", sentence) 
    sentence = sentence.lower() 
    splitSentence = re.split(r'\s+', sentence)
    splitSentence = splitSentence[1:-1]

    #incrementing and getting index of line/lines   
    x+=3
    index = -1
    for place in range (0,len(splitSentence)):
        if splitSentence[place] == "<head>line<head>" or splitSentence[place] == "<head>lines<head>":
            index = place
    place = index


    #+1 W 
    try:
        if splitSentence[place+1] not in featureList['+1 W'].keys():
            featureList['+1 W'][splitSentence[place+1]] = {}
        if wordSense not in featureList['+1 W'][splitSentence[place+1]].keys():
            featureList['+1 W'][splitSentence[place+1]][wordSense] = 1
        else:
            featureList['+1 W'][splitSentence[place+1]][wordSense] += 1
    except:
        pass

    # -1 W 
    try:
        if splitSentence[place-1] not in featureList['-1 W'].keys():
            featureList['-1 W'][splitSentence[place-1]] = {}
        if wordSense not in featureList['-1 W'][splitSentence[place-1]].keys():
            featureList['-1 W'][splitSentence[place-1]][wordSense] = 1
        else:
            featureList['-1 W'][splitSentence[place-1]][wordSense] += 1
    except:
        pass
    

    #-1 +1
    try:
        temp = splitSentence[place-1] + " " + splitSentence[place+1]
        if temp not in featureList['-1 +1'].keys():
            featureList['-1 +1'][temp] = {}
        if wordSense not in featureList['-1 +1'][temp].keys():
            featureList['-1 +1'][temp][wordSense] = 1
        else:
            featureList['-1 +1'][temp][wordSense] += 1
    except:
        pass

    #+1 +2
    try:
        temp = splitSentence[place+1] + " " + splitSentence[place+2]
        if temp not in featureList['+1 +2'].keys():
            featureList['+1 +2'][temp] = {}
        if wordSense not in featureList['+1 +2'][temp].keys():
            featureList['+1 +2'][temp][wordSense] = 1
        else:
            featureList['+1 +2'][temp][wordSense] += 1
    except:
        pass

    #-2 -1
    try:
        temp = splitSentence[place-2] + " " + splitSentence[place-1]
        if temp not in featureList['-2 -1'].keys():
            featureList['-2 -1'][temp] = {}
        if wordSense not in featureList['-2 -1'][temp].keys():
            featureList['-2 -1'][temp][wordSense] = 1
        else:
            featureList['-2 -1'][temp][wordSense] += 1
    except:
        pass

    # +-k W 
    leftIndex = place-k #index - k for left
    rightIndex = place+k #index + k for right
    if leftIndex < 0:
        leftIndex = 0
    if rightIndex > len(splitSentence):
        rightIndex = len(splitSentence)-1 
    kWordsList = splitSentence[leftIndex:rightIndex]
    if '<head>line<head>' in kWordsList:
        kWordsList.remove('<head>line<head>')
    if '<head>lines<head>' in kWordsList:
        kWordsList.remove('<head>lines<head>')
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
rankingDictonary["+1 W"] = {}
rankingDictonary["-1 W"] = {}
rankingDictonary["-1 +1"] = {}
rankingDictonary["+1 +2"] = {}
rankingDictonary["-2 -1"] = {}
rankingDictonary["+-k W"] = {}

#ranking and sorting features
for featType in featureList:
    for currentFeature in featureList[featType]:

        #zeroing out for features that only saw phone or product
        if(phone not in featureList[featType][currentFeature].keys()):
            featureList[featType][currentFeature][phone] = 0
        if(product not in featureList[featType][currentFeature].keys()):
            featureList[featType][currentFeature][product] = 0

        #getting numbers for log 
        phoneCount = featureList[featType][currentFeature][phone]       
        productCount = featureList[featType][currentFeature][product]        
        sum1 = phoneCount+productCount                                                

        if currentFeature not in rankingDictonary[featType]:         
            rankingDictonary[featType][currentFeature] = {}
        #cant divide by 0 
        phoneCount = phoneCount + 0.1
        productCount = productCount + 0.1
        sum1 = sum1 + 0.1
        rankingDictonary[featType][currentFeature] = abs(math.log((phoneCount/sum1)/(productCount/sum1)))

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
    testDictionary[instanceid]["+1 W"] = {}
    testDictionary[instanceid]["-1 W"] = {}
    testDictionary[instanceid]["-1 +1"] = {}
    testDictionary[instanceid]["+1 +2"] = {} 
    testDictionary[instanceid]["-2 -1"] = {}
    testDictionary[instanceid]["+-k W"] = {}

    #cleaning up sentence
    sentence = testData[x+1] # The sentence itself
    sentence = re.sub('<s>|</s>|<p>|</p>|<@>', '', sentence) 
    sentence = re.sub(r"\/|\”|\“|\(|\)|\:|\;|\"|\’|\‘|\.|!|,|\?|\'", '', sentence)
    sentence = re.sub("\s+" , " ", sentence) 
    sentence = sentence.lower() 
    splitSentence = re.split(r'\s+', sentence)
    splitSentence = splitSentence[1:-1]
    
    #getting index of line/lines
    index = 0
    for place in range (0,len(splitSentence)):
        if splitSentence[place] == "<head>line<head>" or splitSentence[place] == "<head>lines<head>":
            index = place
    place = index

    #+1 W Feature Type
    try:
        testDictionary[instanceid]['+1 W'] = splitSentence[place+1]
    except:
        pass

    #-1 W 
    try:
        testDictionary[instanceid]['-1 W'] = splitSentence[place-1]
    except:
        pass


    # -1 +1
    try:
        temp = splitSentence[place-1] + " " + splitSentence[place+1]
        testDictionary[instanceid]['-1 +1'] = temp
    except:
        pass

    # +1 +2 
    try:
        temp = splitSentence[place+1] + " " + splitSentence[place+2]
        testDictionary[instanceid]['+1 +2'] = temp
    except:
        pass

    #-2 -1 
    try:
        temp = splitSentence[place-2] + " " + splitSentence[place-1]
        testDictionary[instanceid]['-2 -1'] = temp
    except:
        pass

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
fileString = "my-line-answers.txt"
outputFile = open(fileString,"w") 

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
                    if featureList[Ftype][wordFromFeature][product] > featureList[Ftype][wordFromFeature][phone]:
                        output = output + "product\"/>\n"
                    else:
                        output = output + "phone\"/>\n"
                    wordSenseFound = True
                    break
         #had an issue with the for loop/// any feature other than +-k comes down here
        else:
            try: 
                testWords = testDictionary[_][Ftype][:]
            except:
                pass
            if (wordFromFeature == testWords): 
                if featureList[Ftype][wordFromFeature][product] > featureList[Ftype][wordFromFeature][phone]:
                    output = output + "product\"/>\n"
                else:
                    output = output + "phone\"/>\n"
                wordSenseFound = True
        if (wordSenseFound == True):
            break

    #default value    
    if not wordSenseFound:
        output = output + "phone\"/>\n"

    print(output) 
    outputFile.write(output)
outputFile.close()

