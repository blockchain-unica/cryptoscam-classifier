import csv
import config
import sys
import string


# Given a list composed of several lists of scores, it returns a single 
# final list of scores where each value is calculated as the sum of 
# the corresponding values from all lists
def sumScores(lists):
    result = []
    
    for i in range(len(lists[0])):
        sum = 0
        for j in range(len(lists)):
            sum = sum + lists[j][i]
        result.append(sum)
    return result


# Given a list composed of several lists of scores, it returns a single 
# final list of scores where each value is calculated as the max of 
# the corresponding values from all lists
def maxScores(lists):
    result = []
    
    for i in range(len(lists[0])):
        max = 0
        for j in range(len(lists)):
            if(lists[j][i] > max):
                max = lists[j][i]
        result.append(max)

    return result


# Given an integer representing the index of the position of a score list,
# it returns the name of the type of scam associated to that position
def positionToType(position, dictionaryPath):
    with open(dictionaryPath, encoding='utf-8') as csv_file:
        readCSV = csv.reader(csv_file, delimiter=',')

        i = 0
        for row in readCSV:
            if(i == position):
                return row[0]
            i+=1

# Given a dictionary it returns the list of scam types
def getScamTypes(dictionary):
    with open(dictionary, encoding='utf-8') as csv_file:
        readCSV = csv.reader(csv_file, delimiter=',')
        
        result = []
        
        # Each row of the CSV contains the list of words of a scam category
        for row in readCSV:

            # The first column is the name of the scam
            result.append(row[0])
        
        return result

# Given a list of scores and its max, it calculates the
# percentage difference with the second max value
def getNextDistance(scores, maxScore):
    
    if(scores.count(maxScore) > 1):
        return 0
    
    secondMax = 0
    for sc in scores:
        if (sc > secondMax and sc<maxScore):
            secondMax=sc
    confident = 100 - ((100 * secondMax) / maxScore)
    return float("{:.2f}".format(confident))

# Given a list of scores and a max value V, it calculates 
# the value minor than V closest to it.
def getNextMax(scores, maxScore):
    
    position = scores.index(maxScore)
    result = maxScore
    diff = sys.maxsize
    for i in range(len(scores)):
        if(i != position and scores[i] <= maxScore):
            if (abs(maxScore - scores[i]) < diff):
                diff = abs(maxScore - scores[i])
                result = scores[i]
    
    return result
    
    
# Aggregates scores of subcategories belonging to the same category
def aggregateScores(scores):
    result = [0] * 13
    
    # Ponzi
    result[0] = scores[0] 

    # Fake services
    temp = []
    temp.append(scores[1])  # Fake services
    temp.append(scores[2])  # Fake exchange
    temp.append(scores[3])  # Fake wallet
    temp.append(scores[4])  # Fake mixing
    temp.append(scores[5])  # Fake mining
    temp.append(scores[6])  # Fake donation
    result[1] = max(temp)

    # Malware
    temp = []
    temp.append(scores[7])  # Malware
    temp.append(scores[8])  # Ransomware
    temp.append(scores[9])  # Crypto logger
    result[7] = max(temp)

    # Black mail
    result[10] = scores[10]
    
    # Advance-fee scam
    result[11] = scores[11]
    
    # Fake ICO
    result[12] = scores[12]
    
    return result

# Cleans a text from useless characters, such as those appended by Web Archive (\n, \t)
def cleanText(text):
    text = text.replace("\ufeff","")
    text = text.replace("\n", "")
    text = text.replace("\t", "")
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    return text