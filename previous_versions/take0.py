import pdftotext

# Load PDF
with open("resumes/resume.pdf", "rb") as f:
    pdf = pdftotext.PDF(f)
# Make it a string
pdfString = "\n\n".join(pdf)


import phonenumbers
from phonenumbers import geocoder
from phonenumbers import carrier
import area_code_nanp
# phone number and location
for match in phonenumbers.PhoneNumberMatcher(pdfString, "US"):
    if phonenumbers.is_possible_number(match.number) and phonenumbers.is_valid_number(match.number):
        phoneAsString = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.NATIONAL)
        print(phoneAsString)
        print(carrier.name_for_number(match.number, "en"))
        # these may be the same?
        print(geocoder.description_for_number(match.number, "en"))
        print(area_code_nanp.get_region(int(phoneAsString[1:4])))


# email addresses -- https://www.geeksforgeeks.org/extracting-email-addresses-using-regular-expressions-python/
import re
for x in re.findall('\S+@\S+', pdfString):
    print(x)


print()
print()
print()

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Stop Words: A stop word is a commonly used word (such as “the”, “a”, “an”, “in”) that a search engine has been programmed to ignore, both when indexing entries for searching and when retrieving them as the result of a search query.
stop_words = set(stopwords.words('english'))
word_tokens = word_tokenize(pdfString)

# parse all english words (https://stackoverflow.com/a/3788947)
with open("words.txt") as word_file:
    english_words = set(word.strip().lower() for word in word_file)

def is_english_word(word):
    word = word.lower()
    # is itself a word
    if (word) in english_words:
        return True

    # is hyphenated words
    allSubwordsOkay = True
    for subword in word.split("-"):
        if subword not in english_words:
            allSubwordsOkay = False
            break
    if allSubwordsOkay:
        return True

    # is a period
    allSubwordsOkay = True
    for subword in word.split("."):
        if subword not in english_words:
            allSubwordsOkay = False
            break
    if allSubwordsOkay:
        return True

    return False


filtered_sentence = []
for w in word_tokens:
    if w[0].isalpha():
        if w not in stop_words:
            if is_english_word(w):
                filtered_sentence.append(w)
            else:
                print(f'"{w}" is not a word')


print()
print()
print()

# print(filtered_sentence)
