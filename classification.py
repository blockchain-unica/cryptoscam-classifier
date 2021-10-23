import utils
import html2text

# Classification function
def classify(name, scores, unclassifiedThreshold, notEnoughWordsThreshold, texts, isHtml, dictionaryPath):
    
    results = []
    
    # Aggregates scores of subcategories belonging to the same category
    scoresCategories = utils.aggregateScores(scores)
    
    # Take the highscore
    highscore = max(scoresCategories)
    
    scamMainType = 'None'
    
    # Check that it reaches the minimum score for classification
    if(highscore < unclassifiedThreshold):
        scamMainType = 'Other'
        
        # Is it a 'Not enough words'?
        if(isHtml):
            h = html2text.HTML2Text()
            h.ignore_links = True   # Ignore converting links from HTML
            h.escape_snob = True    # Escape special characters
            if (len(texts) > 0):
                weight = 0
                for html in texts:
                    html = h.handle(html)           # Remove html tags and javascript
                    html = utils.cleanText(html)    # Remove \n,\t from Web Archive
                    weight += len(html)             # Get number of characters
                averageWeight = int(weight / len(texts))
                if(averageWeight<notEnoughWordsThreshold):
                    scamMainType = 'Not enough words'
        else:
            if(len(texts)<notEnoughWordsThreshold):
                    scamMainType = 'Not enough words'

    # Try anyway to classify it
    position = scores.index(highscore)
    
    # In that case, the classification is safe:
    if(scamMainType == 'None'):
        scamMainType = utils.positionToType(position, dictionaryPath)

    results.append(highscore)
    results.append(scamMainType)

    return results