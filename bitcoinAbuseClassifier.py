import collections
import sys
import string
import csv

import counter
import utils


unclassifiedThreshold     = 2  #sum of weighted words
notEnoughWordsThreshold   = 1000

scamDictionaryPath = ''
datasetPath = ''
resultsPath = ''

results = {}
reports = {}
addresses = []

with open(datasetPath,encoding='utf-8') as csv_file:
    # Initialize dictionary
    result = counter.initDictionary(scamDictionaryPath)
    wordsDictionary = result[0]
    weights = result[1] 
    categories = result[2]
    #id,address,abuse_type_id,abuse_type_other,abuser,description,from_country,from_country_code,created_at
    readCSV = csv.reader(csv_file, delimiter=',')
    arrayScore = []

    i     = 0 #used to skip the first row (contains the header)
    descriptionScore = 0
    description = ''

    for row in readCSV:
        if i!=0:
            description = row[5]
            descriptionScore = counter.count(wordsDictionary, weights, categories, description, False)
            abuser = row[4]
            abuserScore = counter.count(wordsDictionary, weights, categories, abuser, False)
            abuseOtherTypeScore = counter.count(wordsDictionary, weights, categories, row[3], False)

            descriptionPlusAbuse = []
            descriptionPlusAbuse.append(descriptionScore)
            descriptionPlusAbuse.append(abuserScore)
            descriptionPlusAbuse.append(abuseOtherTypeScore)
            score = utils.sumScores(descriptionPlusAbuse)

            if row[1] not in results:
                results[row[1]] = []
                reports[row[1]] = []
                results[row[1]] = score
                reports[row[1]] = description+abuser
                addresses.append(row[1])
            else:
                lists = []
                lists.append(results[row[1]])
                lists.append(score)
                # Give same weight to all three scores
                results[row[1]] = utils.sumScores(lists)
                reports[row[1]] = description+abuser

        i += 1
        if i%1000 == 0:
            print(i)

    with open(resultsPath, 'a') as csvfile:
        # Save results to file
        header = ["Name"]
        header.extend(utils.getScamTypes(scamDictionaryPath))
        
        writeCSV = csv.writer(csvfile, delimiter=',', lineterminator='\n')
        writeCSV.writerow(header)
        for address in addresses:
            temp = classification.classify(address, results[address], unclassifiedThreshold, notEnoughWordsThreshold, reports[address], False, scamDictionaryPath)
            evaluation = [address]
            evaluation.append(temp[1])
            evaluation.extend(results[address])
            writeCSV.writerow(evaluation)