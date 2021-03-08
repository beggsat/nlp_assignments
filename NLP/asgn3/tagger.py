# NLP assignment 3 - POS Tagging
# Austin Beggs - 3/8/2019
# The goal of this program was to take in training data and apply POS tags to a text file
# based on probabilities of tags from the training data. Actual training input was included in
# the pos-test and pos-train text files. To run this program you must include both of these
# in the arguments. The algorithm used to solve this was to take in the training data, process
# the data into dictionaries, calculate the probability of tags and apply to the test data. The 
# output was then compared to the key given using a 2nd program called scorer.py 

from sys import argv
import re
import numpy as np


#arguments
train = str(argv[1]) 
test = str(argv[2])

#fixing some of the training text
File = open(train, 'r')
trainingText = File.read()
trainingText = re.sub(r'\[ ', ' ', trainingText)
trainingText = re.sub(r' \]', ' ', trainingText) #removing brackets and \n
trainingText = trainingText.replace('\n', ' ')
trainingText = re.sub(r'/\.', '/. <e>/<e> <s>/<s>', trainingText)  #start/end tags
trainingText = re.sub(r'\|([^ ]+)', '', trainingText) #removing whats to the right of |
trainingText = re.split(r'\s+', trainingText)


#creating dictionaries and variables
wordCount = dict()
tagCount = dict()
tagGivenWord = dict() 
tagGivenPrevTag = dict() 
prevWord = "<s>"
prevTag = "<s>"
word = "" 
tag = "" 

#looping through the training text adding the words and tags to dictionaries
for _ in trainingText:
    temp = re.split('/',_)
    if(len(temp) < 2):
        continue
    
    #special case with //\ would be split weird
    if(len(temp) > 2):
        temp[0] = temp[0] + temp[1]
        temp[1] = temp[2]
        
    word = temp[0]
    tag = temp[1]


    #checking if word has been added yet

    if word not in wordCount.keys():
        wordCount[word] = 1
    else:
        wordCount[word] += 1
    
    #checking if tag has been added yet
    if tag not in tagCount.keys():
        tagCount[tag] = 1
    else:
        tagCount[tag] += 1

    #word hasnt been seen
    if word not in tagGivenWord.keys():
        tagGivenWord[word] = {}
        tagGivenWord[word][tag] = 1
    #word has been seen 
    else:
        if tag not in tagGivenWord[word].keys():
            tagGivenWord[word][tag] = 1
        else:
            tagGivenWord[word][tag] += 1
    # last tag hasnt been seen     
    if prevTag not in tagGivenPrevTag.keys():
        tagGivenPrevTag[prevTag] = {}
        tagGivenPrevTag[prevTag][tag] = 1
    # last tag has been seen 
    else:
        if tag not in tagGivenPrevTag[prevTag].keys():
            tagGivenPrevTag[prevTag][tag] = 1
        else:
            tagGivenPrevTag[prevTag][tag] += 1

    prevTag = tag
    prevWord = word


File.close()


#fixing up the file to apply pos tags
File2 = open(test, 'r')
testingText = File2.read()
testingText = re.sub(r'\[ ', ' ', testingText)
testingText = re.sub(r' \]', ' ', testingText)
testingText = testingText.replace('\n', ' ')
testingText = re.sub(r'(\.\s)', '. <e> <s>', testingText)
testingText = re.split(r'\s+', testingText)
tempDict = testingText


lastTag = "<s>"
output = []

# For every word in testing data
for currentWord in testingText:
    
    if(currentWord.isspace()):
        continue
    bestTagProbability = 0
    bestTag = ""
    if(currentWord in tagGivenWord.keys()):
        # For every tag
        for aTag in tagGivenWord[currentWord].keys():
            taglist = tagGivenWord[currentWord].keys() #for debugging
            x = tagGivenWord[currentWord][aTag]
            y = tagCount[aTag]
            if (aTag not in tagGivenPrevTag[lastTag].keys()):
                tagGivenPrevTag[lastTag][aTag] = 1
            u = tagGivenPrevTag[lastTag][aTag]         
            v = tagCount[lastTag]
            probabilityOfCurrentTag = (x/y)*(u/v)          
            #comparing the probability of current tag to highest probability so far, then storing both values
            if ( probabilityOfCurrentTag > bestTagProbability):
                bestTagProbability = ((tagGivenWord[currentWord][aTag])/(tagCount[aTag]))*((tagGivenPrevTag[lastTag][aTag])/(tagCount[lastTag]))
                bestTag = aTag
            
            

        lastTag = bestTag
        if(lastTag != "<e>" ) & (lastTag != "<s>"):
            output.append(currentWord + "/" + bestTag)    

    else:
        output.append(currentWord+"/NN")

for _ in output:
    print(_)

