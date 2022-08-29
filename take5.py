import os
import textract
import nltk
import csv
from collections import Counter
from pprint import pprint
from tqdm import tqdm
import datetime
import json
import warnings
import pandas as pd


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

    # Save the directory paths because we'll use them a lot
    global THIS_RUN_OUTPUT_DIR
    THIS_RUN_OUTPUT_DIR = OUTPUT_DIRECTORY + timestamp + "/"
    global THIS_RUN_JSON_DIR
    THIS_RUN_JSON_DIR = THIS_RUN_OUTPUT_DIR + "json/"

    # Make the directories
    os.mkdir(THIS_RUN_OUTPUT_DIR)
    os.mkdir(THIS_RUN_JSON_DIR)
    os.mkdir(THIS_RUN_JSON_DIR + "words")
    os.mkdir(THIS_RUN_JSON_DIR + "bigrams")
    os.mkdir(THIS_RUN_JSON_DIR + "trigrams")

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


# Write the {word: count} pairs to a JSON file
def collectWords(words, whichWords, resumeName):
    postProcessed = postprocessAllWords(countWords(words))
    postProcessed[RESUME_ID_COLUMN_NAME] = resumeName

    with open(
        THIS_RUN_JSON_DIR + whichWords + "/" + resumeName + ".json",
        "w",
    ) as outputFile:
        json.dump(postProcessed, outputFile)


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


# Merge all the JSON files into a CSV
def combineTermsCounts(whichWords):
    dfs = []
    folderRoot = THIS_RUN_JSON_DIR + whichWords + "/"
    # Go through every json file and convert to a dataframe
    print("Reading in files...")
    for thisFilename in tqdm(os.listdir(folderRoot)):
        file_path = folderRoot + thisFilename
        with open(file_path, "r") as inputFile:
            data = json.load(inputFile)
            tmpDF = pd.DataFrame.from_dict([data])
            dfs.append(tmpDF)
    print("Combining files...")
    # TODO: this is way, way too slow. Do it as we go instead of after?
    # Combine all the dataframes
    finalDF = pd.DataFrame()
    # with warnings.catch_warnings():
    #     # append is deprecated; hide the error message (via https://stackoverflow.com/a/66504876)
    #     warnings.simplefilter(action="ignore", category=FutureWarning)
    #     for df in tqdm(dfs):
    #         finalDF = finalDF.append(df)
    # finalDF = pd.concat(dfs, axis=0, join="outer")

    # Set the index column
    finalDF = finalDF.set_index(RESUME_ID_COLUMN_NAME)
    # Replace all NaNs with 0
    finalDF = finalDF.fillna(0)
    # Convert everything to int (default seems to be float)
    finalDF = finalDF.apply(pd.to_numeric, downcast="integer")
    # Write out to CSV
    finalDF.to_csv(THIS_RUN_OUTPUT_DIR + whichWords + ".csv")


def main():
    global t0
    t0 = datetime.datetime.now()

    print("Initializing constants...")
    initializeConstants()
    t1 = datetime.datetime.now()
    print(f"(took {(t1 - t0).total_seconds()} seconds)\n")

    print("Creating output file structure...")
    termsWriter, termsFileRef = createFileStructure()
    t2 = datetime.datetime.now()
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

    t3 = datetime.datetime.now()
    print(f"(took {(t3 - t2).total_seconds()} seconds)\n")

    termsFileRef.close()

    print("\nCombining single word counts...")
    combineTermsCounts("words")
    t4 = datetime.datetime.now()
    print(f"(took {(t4 - t3).total_seconds()} seconds)\n")

    print("\nCombining bigram counts...")
    combineTermsCounts("bigrams")
    t5 = datetime.datetime.now()
    print(f"(took {(t5 - t4).total_seconds()} seconds)\n")

    print("\nCombining trigram counts...")
    combineTermsCounts("trigrams")
    t6 = datetime.datetime.now()
    print(f"(took {(t6 - t5).total_seconds()} seconds)\n")

    print("Done! :)")
    tLast = datetime.datetime.now()
    print(f"(total runtime: {(tLast - t0).total_seconds()} seconds)")


if __name__ == "__main__":
    main()
