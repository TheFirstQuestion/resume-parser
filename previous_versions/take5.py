import os
import textract
import nltk
import csv
from collections import Counter
from tqdm import tqdm
from datetime import datetime


###################### Config ########################
RESUME_DIRECTORY = "./sample_resumes/"
TERMS_LOCATION = "./terms_of_interest/"
OUTPUT_DIRECTORY = "./output/"
RESUME_ID_COLUMN_NAME = "resumeName"
# This is a lot of terms and may not add much
SKIP_GREEK = True
######################################################


# Set up the global variables used in other methods (word and terms lists)
def initializeConstants():
    # Stop Words: A stop word is a commonly used word (such as “the”, “a”, “an”, “in”) that a search engine has been programmed to ignore, both when indexing entries for searching and when retrieving them as the result of a search query.
    global StopWords
    StopWords = set(nltk.corpus.stopwords.words("english"))

    # Get the set of all English words (https://stackoverflow.com/a/3788947)
    global EnglishWords
    with open("words.txt") as word_file:
        wordsFile = set(word.strip().lower() for word in word_file)
    # Words from the NLTK corpus
    nltkWords = set(w.lower() for w in nltk.corpus.words.words())
    # A file I made that include things that are words but aren't in the other lists (hacky)
    with open("words_also.txt") as word_file:
        alsoWords = set(word.strip().lower() for word in word_file)
    EnglishWords = wordsFile.union(nltkWords).union(alsoWords)

    # Load the terms lists into one big array
    global TermsOfInterest
    TermsOfInterest = []
    for thisFilename in os.listdir(TERMS_LOCATION):
        if SKIP_GREEK and thisFilename == "greek.csv":
            continue
        TermsOfInterest = [*TermsOfInterest, *(readCSV(thisFilename))]


# Create the files and folders that will organize the intermediate and final output
def createFileStructure():
    # Uee the date and time to identify the output for convenience
    global timestamp
    timestamp = t0.strftime("%Y-%m-%d__%p-%H_%M_%S")

    # Save the directory path because we'll use it a lot
    global THIS_RUN_OUTPUT_DIR
    THIS_RUN_OUTPUT_DIR = OUTPUT_DIRECTORY + timestamp + "/"

    # Make the directories
    os.mkdir(THIS_RUN_OUTPUT_DIR)

    # Create the word count CSVs
    with open(THIS_RUN_OUTPUT_DIR + "words_headers.csv", "w") as outputFile:
        outputFile.write(RESUME_ID_COLUMN_NAME)
    with open(THIS_RUN_OUTPUT_DIR + "bigrams_headers.csv", "w") as outputFile:
        outputFile.write(RESUME_ID_COLUMN_NAME)
    with open(THIS_RUN_OUTPUT_DIR + "trigrams_headers.csv", "w") as outputFile:
        outputFile.write(RESUME_ID_COLUMN_NAME)

    # Terms CSV stuff:
    # Each term has a column, using the first term as the general name
    headers = [synonyms[0] for synonyms in TermsOfInterest]
    # Add a column for the resume ID
    headers.insert(0, RESUME_ID_COLUMN_NAME)
    # Create the CSV and return its reference
    csvfile = open(OUTPUT_DIRECTORY + timestamp + "/" + "terms.csv", "w+")
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()
    return writer, csvfile


# Read in the terms lists
def readCSV(filename):
    with open(TERMS_LOCATION + filename, mode="r") as file:
        lines = list()
        for line in csv.reader(file):
            thisLine = []
            for term in line:
                thisLine.append(term.strip())
            lines.append(thisLine)
        return lines


# Check if the token is a valid English word
def isEnglishWord(token):
    word = token.lower()

    # is itself a word
    if word in EnglishWords:
        return True

    # is made of words separated by punctuation (with no space)
    punctuation = ["-", ".", "/", ":"]
    for pMark in punctuation:
        if pMark in word:
            allSubwordsAreWords = True
            for subword in word.split(pMark):
                if not isEnglishWord(subword):
                    allSubwordsAreWords = False
                    break
            if allSubwordsAreWords:
                return True

    return False


# Naive check: the first character is uppercase and the last isn't
def isProperNoun(token):
    return token[0].isupper() and token[-1].islower()


# Naive check: the token is all uppercase
def isAcronym(token):
    return token.isupper()


# Checks that the token is: (a) a valid English word, (b) a proper noun, or (c) an acronym
def isValidTerm(token):
    if isEnglishWord(token):
        return True

    if isProperNoun(token):
        return True

    if isAcronym(token):
        return True

    return False


# Go through the tokens of a text and get rid of junk
def getValidWords(word_tokens):
    retVal = []
    for token in word_tokens:
        # Ignore tokens that begin with non-alphanumeric characters
        if token[0].isalpha():
            # Ignore stop words
            if token.lower() not in StopWords:
                # Check validity of token
                if isValidTerm(token):
                    # Only lower-case it after checks
                    retVal.append(token.lower())
    return retVal


# Find all the occurances of terms of interest in the text
def searchForTerms(text, tokens):
    wordCounts = countWords(tokens)
    termCounts = {}

    for term in TermsOfInterest:
        rowID = term[0]
        termCounts[rowID] = 0

        for synonym in term:
            # Check for multi-word term (which won't be in tokens)
            if len(synonym.split(" ")) > 1:
                termCounts[rowID] += text.count(synonym)
            else:
                termCounts[rowID] += wordCounts[synonym]

    return termCounts


# Returns {word: count} for every word in a text
def countWords(words):
    return Counter(words)


# Write the {word: count} pairs
def collectWords(words, whichWords, resumeName):
    postProcessed = postprocessAllWords(countWords(words))
    postProcessed[RESUME_ID_COLUMN_NAME] = resumeName

    # Read existing header file
    with open(THIS_RUN_OUTPUT_DIR + whichWords + "_headers.csv", "r") as inputFile:
        headers = inputFile.readline().strip().split(",")

    # Write to file
    with open(THIS_RUN_OUTPUT_DIR + whichWords + ".csv", "a") as outputFile:
        keys = list(postProcessed.keys())
        keysAlreadyRecorded = set()
        thisRow = ""

        # Add counts for every word already seen
        for h in headers:
            header = h.strip()
            if header in keys:
                thisRow += str(postProcessed[header]) + ","
            else:
                thisRow += "0,"
            keysAlreadyRecorded.add(header)

        # Add new words (with counts)
        for key in keys:
            if key not in keysAlreadyRecorded:
                headers.append(key)
                thisRow += str(postProcessed[key]) + ","

        # Write the new info to the file
        # [-1] to trim off the last extra comma
        outputFile.write(thisRow[:-1] + "\n")

    # Write new headers
    with open(THIS_RUN_OUTPUT_DIR + whichWords + "_headers.csv", "w") as outputFile:
        outputFile.write(",".join(headers))


# Sort {word: count} pairs by count
def sortByCount(words):
    return dict(sorted(words.items(), key=lambda item: item[1], reverse=True))


# Sort {word: count} pairs by word
def sortAlphabetically(words):
    return dict(sorted(words.items(), key=lambda item: item[0]))


# Sort (by count) and filter the word list
def postprocessAllWords(allSeen):
    newList = {}
    # Could do some filtering here
    for term, count in allSeen.items():
        if count > 1:
            # If term is a tuple (bi/trigrams), JSON will fail -- make string
            if type(term) == tuple:
                term = " ".join(term)
            newList[term] = count
    return sortByCount(newList)


def main():
    global t0
    t0 = datetime.now()

    print("Initializing constants...")
    initializeConstants()
    t1 = datetime.now()
    print(f"(took {(t1 - t0).total_seconds()} seconds)\n")

    print("Creating output file structure...")
    termsWriter, termsFileRef = createFileStructure()
    t2 = datetime.now()
    print(f"(took {(t2 - t1).total_seconds()} seconds)\n")

    print("Searching resumes...")
    for thisFilename in tqdm(os.listdir(RESUME_DIRECTORY)):
        file_path = RESUME_DIRECTORY + thisFilename

        # text -- the plain text of the resume (case-sensitive)
        text = textract.process(file_path).decode("utf8")
        # wordTokens -- tokens in the text (space-separated, but a bit fancier)
        tokens = nltk.tokenize.word_tokenize(text)

        # results -- the counts for each term
        results = searchForTerms(text, tokens)
        # Add the resume ID column
        results[RESUME_ID_COLUMN_NAME] = thisFilename
        # Write results to the output CSV
        termsWriter.writerow(results)

        # words -- tokens that are English word or proper noun or acronym
        words = getValidWords(tokens)
        bigrams = nltk.bigrams(words)
        trigrams = nltk.trigrams(words)
        # collectWords -- add to the list of what's been seen across all resumes
        collectWords(words, "words", thisFilename)
        collectWords(bigrams, "bigrams", thisFilename)
        collectWords(trigrams, "trigrams", thisFilename)

    t3 = datetime.now()
    print(f"(took {(t3 - t2).total_seconds()} seconds)\n")

    termsFileRef.close()

    print("Done! :)")
    tLast = datetime.now()
    print(f"(total runtime: {(tLast - t0).total_seconds()} seconds)")


if __name__ == "__main__":
    main()
