import json
import csv
import os
import html2text

import counter
import utils



# Main function
# scamDictionaryPath: Path of dictionary file (weighted scam words)
# cryptoDictionaryPath: Path of dictionary file (weighted cryptocurrency words) 
# dataset: Path of dataset directory containing one file for each scam
# results: Path of empty CSV file for saving results 
# unclassifiedThreshold: Minimum weight required to classify a snapshot as a scam
# featuresWeight: Choose the weight of each word if it appears in URL, Description, or HTML code 
# notEnoughWordsThreshold: Average number of snapshot characters required to classify a website as not empty
# cryptoThreshold: Minimum weight required to classify a snapshot as related to cryptocurrency
def urlClassifier(scamDictionaryPath, cryptoDictionaryPath, dataset, results, unclassifiedThreshold, featuresWeight, notEnoughWordsThreshold, cryptoThreshold):

    # Initialize scam dictionary
    result = counter.initDictionary(scamDictionaryPath)
    scamWordsDictionary = result[0]
    scamWeights = result[1] 
    scamCategories = result[2]

    # Initialize crypto dictionary
    result = counter.initDictionary(cryptoDictionaryPath)
    cryptoWordsDictionary = result[0]
    cryptoWeights = result[1] 
    cryptoCategories = result[2]

    # Results will be saved to file
    with open(results, 'a') as csvfile:
        writeCSV = csv.writer(csvfile, delimiter=',', lineterminator='\n')
        
        header = ["Name"]
        header.extend(utils.getScamTypes(scamDictionaryPath))
        header.extend(["Total", "Older", "Empty", "Error", "Domain", "NoCrypto", "Crypto", "Valid", "URLCrypto"])
        writeCSV.writerow(header)

    # Each scam has its own file
    files = os.listdir(dataset)
    for file in files:

        # Open scam file
        with open(dataset + file,'r') as json_file:
            scam = json.load(json_file)

            # Apply classification
            evaluation = [scam["Name"]]
            evaluation.extend(classify(scam, unclassifiedThreshold, featuresWeight, notEnoughWordsThreshold, 
            scamWordsDictionary, scamWeights, scamCategories, 
            cryptoWordsDictionary, cryptoWeights, cryptoCategories, cryptoThreshold, scamDictionaryPath))

            # Save results
            with open(results, 'a') as csvfile:
                writeCSV = csv.writer(csvfile, delimiter=',', lineterminator='\n')
                writeCSV.writerow(evaluation)



def classify(scam, unclassifiedThreshold, featuresWeight, notEnoughWordsThreshold, scamWordsDictionary, scamWeights, scamCategories, cryptoWordsDictionary, cryptoWeights, cryptoCategories, cryptoThreshold, scamDictionaryPath):

    # Stats of each snapshot
    total = 0
    older = 0
    empty = 0
    error = 0
    domain = 0
    noCrypto = 0
    crypto = 0
    valid = 0
    urlCrypto = 0
    inspect = False

    # The features analysed for each scam are:
    # URL, Description and list of HTML snapshots available
    features = []
    if("URL" in scam and scam["URL"]):
        l = counter.count(scamWordsDictionary, scamWeights, scamCategories, scam["URL"], True)
        l = [x * featuresWeight[1] for x in l]
        features.append(l)
        
        preprocessingURL = counter.count(cryptoWordsDictionary, cryptoWeights, cryptoCategories, scam["URL"], True)
        urlCrypto = preprocessingURL[0]
        
    if("Description" in scam and scam["Description"]):
        l = counter.count(scamWordsDictionary, scamWeights, scamCategories, scam["Description"], False)
        l = [x * featuresWeight[2] for x in l]
        features.append(l)

    # List of snapshots 
    total = len(scam["HTMLs"])
    htmls = []

    for idx, html in enumerate(scam["HTMLs"]):
        inspect = True

        # General stats: check if it is older than Bitcoin
        if("Timestamps" in scam and scam["Timestamps"][idx] < "20090103000000"):
            older += 1

        preprocessingHtml = counter.count(cryptoWordsDictionary, cryptoWeights, cryptoCategories, html, False)
        cryptoScore = preprocessingHtml[0]
        errorScore = preprocessingHtml[1]
        domainScore = preprocessingHtml[2]
        
        # 1) Empty text
        str = utils.cleanText(html)
        str = str.replace(' ', '')
        if(str == ''):
            empty += 1
        
        else:
            # 2) Either Error or domainForSale page
            if(errorScore > 0):
                error += 1
                inspect = False
            elif(domainScore > 0):
                domain += 1
                inspect = False

        # Inspect only valid HTMLs
        if(inspect):
            # General stats: check if it is related to crypto
            if(cryptoScore <= cryptoThreshold):
                noCrypto += 1
            else:
                crypto += 1

            l = counter.count(scamWordsDictionary, scamWeights, scamCategories, html, False)
            l = [x * featuresWeight[3] for x in l]
            htmls.append(l)
    
    # How many valid snapshot?
    valid = total - error - domain - empty
    
    # For each scam type, take the score of the snapshot
    # that reached the maximum score
    if (valid > 0):
        features.append(utils.maxScores(htmls))

    # Sum the scores of all features to build the 
    # list containing the final score for each type
    scores = utils.sumScores(features)
        
    temp = classification.classify(scam["URL"], scores, unclassifiedThreshold, notEnoughWordsThreshold, scam["HTMLs"], True, scamDictionaryPath)

    scamMainType = temp[1]    
    if (valid <= 0):
        scamMainType = 'No Valid Snapshots'    
    
    results = []
    results.append(scamMainType)
    results.extend(scores)
    results.append(total)
    results.append(older)
    results.append(empty)
    results.append(error)
    results.append(domain)
    results.append(noCrypto)
    results.append(crypto)
    results.append(valid)
    results.append(urlCrypto)
    
    return results