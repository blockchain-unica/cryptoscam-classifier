import sys
import string
import csv
import unicodedata
import utils


def initDictionary(path):
    dictionary = {}
    weights = {}
    categories = []

    # Build dictionary from a file
    with open(path, encoding='utf-8') as csv_file:
        readCSV = csv.reader(csv_file, delimiter=',')

        # Each row of the CSV contains the list of words of a scam category
        for row in readCSV:

            # The first column is the name of the scam
            if row[0] not in dictionary:
                dictionary[row[0]] = []
                weights[row[0]] = []

            categories.append(row[0])

            # The second column is the total number of words (columns) of the scam
            words = int(row[1])

            # The other columns contain the words associated with the scam
            for index in range(2, (words * 2)+2, 2):
                dictionary[row[0]].append(row[index].lower())
                weights[row[0]].append(row[index + 1])
                
    return dictionary, weights, categories

# Given an input text, the function counts, for each scam category,
# how many scam words appear in the text. It returns the list of scores
# where each position is related to a different category (ponzi,blackmail,malware,...).
def count(wordsDictionary, weights, categories, text, sub):
    score = []
    # Score of each type of scam
    for i in range(0, len(categories)):
        score.append(0)
    
    # Clean input string and split it in words
    text = utils.cleanText(text).split()

    # For each word, check if it is contained in the dictionary
    previousWord = 'previousWord'
    for word in text:
        word = unicodeToUTF(word).lower()
        doubleWord = previousWord + " " + word
        for category in range(0, len(categories)):
            wordsCategory = wordsDictionary[categories[category]]
            weightCategory = weights[categories[category]]

            # Perform a substring check (e.g. inspecting url domain)
            if(sub):
                temp=next((i for i,s in enumerate(wordsCategory) if s in word), None)
                if(temp is not None):
                    score[category]+=int(weightCategory[temp])
            
            # Perform an exact string check (e.g. inspecting description)
            else:
                if word in wordsCategory:
                    score[category] += int(weightCategory[wordsCategory.index(word)])
                if doubleWord in wordsCategory:
                    score[category] += int(weightCategory[wordsCategory.index(doubleWord)])
        previousWord = word
    # Return the updated list of scores
    return score;
    

def unicodeToUTF(word):
    utfLow = list(string.ascii_lowercase)
    uniLow = ['????','????','????','????','????','????','????','????','????','j','????','????','????','????','????','????','q','????','????','????','????','????','????','????','????','z']
    uniUP  = ['????','????','????','????','????','????','????','????','????','????','????','????','????','????','????','????','q','????','????','????','????','????','????','????','????','z']
    uniLow2= ['????','????','????','????','????','f','????','????','????','j','????','????','????','????','????','????','q','????','????','????','????','????','????','x','????','????']

    newWord = ""
    for l in word:
        if l in uniLow:
            newWord += utfLow[uniLow.index(l)]
        else:
            if l in uniUP:
                newWord += utfLow[uniUP.index(l)]
            else:
                if l in uniLow2:
                    newWord += utfLow[uniLow2.index(l)]
                else:
                    newWord += l
    return newWord