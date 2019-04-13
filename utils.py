import pickle
from time import time
import re
import math
import os
from nltk.stem.porter import PorterStemmer

# MARK - TEXT PREPROCESSING FUNCTIONS

stemmer = PorterStemmer()

def preprocess_raw_word(word):
	# Stemming and Casefolding
	# In most cases stemming lowercases the words but in some special
	# cases like to, in , the, we found that both TO and to, IN and in
	# THE and the were in our dictionary, so we are going to an extra
	# step to lowercase it for certain.
	return stemmer.stem(word).lower()


text_preprocessing_rules = {
	# Slashes, dot, comma, dash preceeded and succeeded by a digit
	r"(?P<back>\d*)(\/|-|,|\.)(?P<front>\d*)": r"\g<back>\g<front>",
	
	# Eg. Change suyash/shekhar to suyash shekhar
	r"(?P<back>[a-zA-Z0-9]*)(\/|-|,|\.)(?P<forward>[a-zA-Z0-9]*)": r"\g<back> \g<forward>"
}

def preprocess_raw_text(text):
	for regex, replacement in text_preprocessing_rules.items():
		text = re.sub(regex, replacement, text)
	return text

def preprocess_raw_query(query):
	for regex, replacement in text_preprocessing_rules.items():
		query = re.sub(regex, replacement, query)
	return query


# Get the number of documents
def get_number_of_documents():
	with open('doc_length_dictionary.txt') as f:
		dictionary = pickle.load(f)
	return len(dictionary)

# MARK - FILE I/O FUNCTIONS

# Load the dictionary from dictionary_file_path using pickle
def deserialize_dictionary(dictionary_file_path):
	with open(dictionary_file_path) as f:
		dictionary = pickle.load(f)
	return dictionary

# Takes in a term and dictionary, and generate the posting list
def get_postings_for_term(term, dictionary, postings_file_path):
    # Handle unseen words
    if term not in dictionary: 
        return []

    # Byte offset and length of data chunk in postings file
    offset, length, doc_freq = dictionary[term]
    
    with open(postings_file_path, 'r') as f:
        f.seek(offset)
        posting_byte = f.read(length)
        posting_list = pickle.loads(posting_byte)
    return posting_list

# Takes in a term and dictionary, and generate the posting list


def get_doc_freq_for_term(term, dictionary):
    # Handle unseen words
    if term not in dictionary:
        return 0

    # Byte offset and length of data chunk in postings file
    offset, length, doc_freq = dictionary[term]
    return doc_freq

# Save an object to disk 
def save_to_disk(obj, file):
    with open(file, 'wb') as fr:
        pickle.dump(obj, fr)



# MARK - DEBUGGING FUNCTIONS

# This function takes in a function and that functions argumnents and
# times how long the function execution took. It is used for debugging
# similar to how timeit is used but we wanted a simpler solution
def clock_and_execute(func, *args):
	start_time = time()
	ret = func(*args)
	end_time = time()
	print("Executed {}{} in {} sec." \
		.format(func.__name__, args, end_time - start_time))
	return ret

# Generates a file of human readable postings and occurences. Maily used for debugging
# Each line is of the format: `word`: num_of_occurences -> `[2, 10, 34, ...]` (postings list)
def generate_occurences_file(dictionary):
	len_dict = {word: len(v) for word, v in dictionary.items()}
	with open("occurences.txt", 'w') as f:
		for k, v in sorted(len_dict.items(), key=lambda x: x[1]):
			f.write("{}: {} -> {}\n".format(k.ljust(30), str(v).ljust(5), dictionary[k]))
    
def convert_tuple_to_string(tuple):
    return ' '.join(tuple)