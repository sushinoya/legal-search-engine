import pickle
from time import time
import re
import math
import os
from nltk.stem.porter import PorterStemmer
import nltk
from collections import defaultdict
from nltk.corpus import wordnet as wn

# MARK - TEXT PREPROCESSING FUNCTIONS

def query_chunker(query):
	return [s.replace("\"", '') for s in query.split(' AND ')]

def query_combiner(query):
	return query.replace("\"", '').replace(' AND ', ' ')

stemmer = PorterStemmer()

def stem_raw_word(word):
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

#add 2 vectors together. The vectors are represented in terms of dictionaries
def add_vectors(dic1, dic2):
    indexes = set(list(dic1.keys()) + list(dic2.keys()))
    output = {}
    for index in indexes:
        output[index] = dic1.get(index, 0) + dic2.get(index, 0)
    return output

def multiply_vector(dic, multiplier):
    return { index: value * multiplier for index, value in dic.items() }

# Get the number of documents
def get_number_of_documents():
	with open('doc_length_dictionary.txt', 'rb') as f:
		dictionary = pickle.load(f)
	return len(dictionary)

# Retrieve the document vector
def get_doc_vector(doc_id):
	with open('doc_vector.txt', 'rb') as f:
		dictionary = pickle.load(f)

	return dictionary[doc_id]


# MARK - FILE I/O FUNCTIONS

# Load the dictionary from dictionary_file_path using pickle
def deserialize_dictionary(dictionary_file_path):
	with open(dictionary_file_path, 'rb') as f:
		dictionary = pickle.load(f)
	return dictionary

# Takes in a term and dictionary, and generate the posting list
def get_postings_for_term(term, dictionary, postings_file_path):
    # Handle unseen words
    if term not in dictionary: 
        return {}

    # Byte offset and length of data chunk in postings file
    offset, length, doc_freq = dictionary[term]
    
    with open(postings_file_path, 'rb') as f:
        f.seek(offset)
        posting_byte = f.read(length)
        posting_dict = pickle.loads(posting_byte)
    return posting_dict

# Retrieve the postings for a single word or a phrase
def get_postings_for_word_or_phrase(term, dictionary, postings_file_path):
    # Handle Phrase
    if len(term.split()) > 1:
        return get_postings_for_phrase(term, dictionary, postings_file_path)
    # Handle Word
    else:     
        posting_dict = get_postings_for_term(term, dictionary, postings_file_path)
        return { word: len(indexes) for word, indexes in posting_dict.items() }



# Takes in a term, dictionary, and postings file, and generate the posting list
def get_doc_freq_for_term(term, dictionary, postings_file):
    # Handle Phrases
    if len(term.split()) > 1:
        return len(get_postings_for_phrase(term, dictionary, postings_file))

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


def get_first_of_tuple(lst_of_tuple):
    return [x[0] for x in lst_of_tuple]

def check_and_existence(query):
	return "AND" in query

# Get the postings for a phrase, e.g. 'a tiny boy'
# This function will retrieve the postings for 'a', 'tiny', and 'boy'
# and get the get the postings based on the positional indices of each word in the phrase
def get_postings_for_phrase(query_string, dictionary, postings_file):
    tokens = query_string.split()

    # Query_dictionaries is a list of dictionaries
    query_dictionaries = { token: get_postings_for_term(token, dictionary, postings_file) for token in tokens }
    common_document_ids = set(query_dictionaries[tokens[0]])
    for doc_index_dict in query_dictionaries.values():
        common_document_ids = common_document_ids & set(doc_index_dict.keys())

    output = defaultdict(int)
 
    for doc in common_document_ids:
        phrases = list(nltk.ngrams(tokens, 2))
        last_round = len(phrases) - 1
  
        for iteration_round, phrase in enumerate(phrases):
            wordA, wordB = phrase
            position_indexesA = query_dictionaries[wordA][doc]
            position_indexesB = query_dictionaries[wordB][doc]

            query_dictionaries[wordB][doc] = []
            
            indexesB_set = set(position_indexesB)
            for index in position_indexesA:
                if index + 1 in indexesB_set:
                    if iteration_round == last_round: 
                        output[doc] += 1
                    query_dictionaries[wordB][doc].append(index + 1)

    return output

def flatten_list_of_list(list_of_list):
    return [y for x in list_of_list for y in x]

# Generate synonyms for a list of queries based on wordnet
def wordnet_generate_synonyms(list_of_queries):
    sysnet_for_queries = [wn.synsets(query) for query in list_of_queries] #generates a list of list
    flattened_sysnet = flatten_list_of_list(sysnet_for_queries)
    lemma_names_list = [x.lemma_names() for x in flattened_sysnet]
    flattened_lemma_names = flatten_list_of_list(lemma_names_list)
    unique_lemma_names = list(set(flattened_lemma_names))
    return unique_lemma_names