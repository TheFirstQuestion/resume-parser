import nltk
import csv

###################### Config ########################
TERMS_LOCATION = "./terms_of_interest/"
OUTPUT_FILENAME = "greek.csv"
######################################################

###################### Constants ########################
GREEK_ALPHABET = [
    "Alpha",
    "Beta",
    "Gamma",
    "Delta",
    "Epsilon",
    "Zeta",
    "Eta",
    "Theta",
    "Iota",
    "Kappa",
    "Lambda",
    "Mu",
    "Nu",
    "Xi",
    "Omicron",
    "Pi",
    "Rho",
    "Sigma",
    "Tau",
    "Upsilon",
    "Phi",
    "Chi",
    "Psi",
    "Omega",
]
######################################################


def createGreekList():
    with open(TERMS_LOCATION + OUTPUT_FILENAME, "w+") as csvfile:
        csvfile.write("Greek_2_letter, ")

        # Two-letter combinations
        for letter1 in GREEK_ALPHABET:
            for letter2 in GREEK_ALPHABET:
                csvfile.write(letter1 + " " + letter2 + ", ")

        csvfile.write("\n")
        csvfile.write("Greek_3_letter, ")

        # Three-letter combinations
        for letter1 in GREEK_ALPHABET:
            for letter2 in GREEK_ALPHABET:
                for letter3 in GREEK_ALPHABET:
                    csvfile.write(letter1 + " " + letter2 + " " + letter3 + ", ")

    print("Greek org list generated!")


def main():
    # Download dependencies
    nltk.download("punkt")

    # Write Greek org names to CSV file
    createGreekList()


if __name__ == "__main__":
    main()
