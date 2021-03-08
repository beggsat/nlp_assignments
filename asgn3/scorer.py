import sys
from sys import argv
import re
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
'''Handle command line arguments'''
testFile = str(argv[1]) 
keyFile = str(argv[2])

File = open(testFile , 'r')
test = File.read()
test = re.sub('(.*)/', '', test)  #removes word before the slash so its just the tag
test = re.split(r'\s+', test)    #splitting 
File2 = open(keyFile, 'r')
key = File2.read()
key = re.sub(r'\[ ', '', key)
key = re.sub(r' \]', ' ', key)
key = key.replace('\n', ' ')
key = re.sub(r'([^ ]*)/', '', key)
key = re.split(r'\s+', key)
File.close()

File2.close()

correct = 0
total = 0
for x in range(0 , len(key)-1):
    if(test[x] == key[x]):
        correct += 1
    total += 1


print("Number Correct : " + str(correct))
print("Number Total : " + str(total))
print("Percent : " + str((correct/total)*100))





y_actu = pd.Series(key, name='Actual')
y_pred = pd.Series(test, name='Predicted')
df_confusion = pd.crosstab(y_actu, y_pred)
pd.set_option('display.expand_frame_repr', False)
print("Confusion matrix:\n%s" % df_confusion)


# for _ in test:
#     print(_)