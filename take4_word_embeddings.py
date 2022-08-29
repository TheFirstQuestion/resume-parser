# per https://stackoverflow.com/questions/55714135/how-can-i-fix-an-omp-error-15-initializing-libiomp5-dylib-but-found-libomp
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
os.environ["TOKENIZERS_PARALLELISM"] = "False"


# import spacy

# # python -m spacy download en_core_web_trf
# # Load the spacy model that you have installed
# nlp = spacy.load("en_core_web_trf")

# # process a sentence using the model
# doc = nlp("This is some text that I am processing with Spacy")

# It's that simple - all of the vectors and words are assigned after this point
# Get the vector for 'text':
# print(doc[3].vector)

# Get the mean vector for the entire sentence (useful for sentence classification etc.)
# print(doc.vector)

from gensim.models import KeyedVectors

# Load vectors directly from the file
model = KeyedVectors.load_word2vec_format(
    "pretrained_models/GoogleNews-vectors-negative300.bin", binary=True
)

for index, word in enumerate(model.index_to_key):
    if index == 10:
        break
    print(f"word #{index}/{len(model.index_to_key)} is {word}")
