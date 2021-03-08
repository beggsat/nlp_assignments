# NLP assignment 5 - sentiment (scorer.py)
# Austin Beggs - 4/14/2019

# The goal of this program was to adapt the scorer from assignment 4 to work with sentiment. To run this program you must include both of these
# in the arguments. The algorithm used to solve this was to take in both files, trim out everything but the sense and 
# then compare the results to the key while keeping count of correct. The output is the amount correct, total, and percentage
# plus a confusion matrix from sklearn

#Example input and output 
#to run the program use 
#          python scorer.py my-sentiment-answers.txt sentiment-test-key.txt
#on the command line, input files being output from wsd.py and a key
#output is sent to STDOUT that displays correct/incorrect + a confusion matrix



import sys
from sys import argv
import re
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
#command line arguments
testFile = str(argv[1]) 
keyFile = str(argv[2])

File = open(testFile , 'r', encoding="utf-16")
test = File.read()
#test = re.sub('<[/]?context>\s|</instance>\s','', test)
#test = re.sub('(.*)/', '', test)  #removes word before the slash so its just the tag
test = re.split(r'\n', test)    #splitting 
File2 = open(keyFile, 'r')
key = File2.read()
#key = re.sub(r'\[ ', '', key)
#key = re.sub(r' \]', ' ', key)
#key = key.replace('\n', ' ')
#key = re.sub(r'([^ ]*)/', '', key)
key = re.split(r'\n', key)
test1 = []
key1 = []
for x in range(0, len(key)-1):
    tempTest = re.search("senseid=\"(.*)\"", test[x]) 
    tempKey = re.search("sentiment=\"(.*)\"", key[x]) 
    test1.append(tempTest.group(1))
    key1.append(tempKey.group(1))

File.close()
File2.close()

correct = 0
total = 0
for x in range(0 , len(key)-1):
    if(test1[x] == key1[x]):
        correct += 1
    total += 1


#output
print("Number Correct : " + str(correct))
print("Number Total : " + str(total))
print("Percent : " + str((correct/total)*100))

#confusion  matrix
y_actu = pd.Series(key1, name='Actual')
y_pred = pd.Series(test1, name='Predicted')
df_confusion = pd.crosstab(y_actu, y_pred)
pd.set_option('display.expand_frame_repr', False)
print("Confusion matrix:\n%s" % df_confusion)


# for _ in test:
#     print(_)