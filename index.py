#!/usr/bin/python
import re
import nltk
import sys
import os
import getopt
import linecache
import pickle
import math
import pandas
from utils import preprocess_raw_text, deserialize_dictionary, save_to_disk, clock_and_execute, generate_occurences_file, stem_raw_word, convert_tuple_to_string
from collections import defaultdict, Counter

stemming_dictionary = {}

def index(input_file, output_file_dictionary, output_file_postings):
    df = pandas.read_csv(input_file)
    dictionary = defaultdict(lambda: defaultdict(list))
    doc_vector = {}
    doc_length_dictionary = {}
    num = 1
    total_entries_len = len(list(df.itertuples(index=False)))

    for row in df.itertuples(index=False):
        print(f'currently indexing number {num}, {num / total_entries_len * 100}% done')
        num += 1
        content = getattr(row, "content")
        document_id = getattr(row, "document_id")

        words = process_content(content)
        ctr = dict(Counter(words))
        doc_vector[document_id] = ctr
        # positional_indexes = [ (word,  index) for index, word in enumerate(words) ]
        # positional_indexes = { word :  index for index, word in enumerate(words) }

        # {the: {(doc1, [23, 45,..]), (doc2..)}
        positional_indexes_in_doc = defaultdict(list)
        for index, word in enumerate(words):
            positional_indexes_in_doc[word].append(index)

        for word, indexes in positional_indexes_in_doc.items():
            dictionary[word][document_id] = positional_indexes_in_doc[word]

        # for term in all_tokens:
        #     dictionary[term][document_id] += 1

        # Create dictionary of document length
        tf_dictionary = Counter(words)
        log_tf_dictionary = { word: 1 + math.log(tf, 10) for word, tf in tf_dictionary.items() } 
        length_of_log_tf_vector = math.sqrt(sum([dim * dim for dim in log_tf_dictionary.values()]))
        doc_length_dictionary[document_id] = length_of_log_tf_vector

    save_to_disk(doc_length_dictionary, "doc_length_dictionary.txt")
    save_to_disk(doc_vector, "doc_vector.txt")

    # for key, value in dictionary.items():
    #     dictionary[key] = sorted(value.items(), key=lambda x: x[0])
    
    # Generates a file of human readable postings and occurences. Maily used for debugging
    # Each line is of the format: `word`: num_of_occurences -> `[2, 10, 34, ...]` (postings list)
    generate_occurences_file(dictionary)  # Uncomment the next line if needed for debugging

    # Saves the postings file and dictionary file to disk
    process_dictionary(dictionary, output_file_dictionary, output_file_postings)

    # os._exit()
    # sys.exit(0)

def process_dictionary(dictionary, output_file_dictionary, output_file_postings):
    dictionary_to_be_saved = save_to_postings_and_generate_dictionary(dictionary, output_file_postings)
    save_to_disk(dictionary_to_be_saved, output_file_dictionary)

'''
This function saves the postings to the postings file.
It also generates the dictonary of object which will be stored later in the
dictionary file.

The structure of this dictionary is { word: (byte_offset, data_chunk_size, doc freq) }

Byte offset and data chunk size allow us to retrive the postings for a given word
relatively fast from the postings file because we can seek to the relevant bytes
and only load those into the program.
'''
def save_to_postings_and_generate_dictionary(dictionary, output_file_postings):
    dictionary_to_be_saved = {}
    current_pointer = 0
    with open(output_file_postings, 'wb') as f:
        for term, dictionary_of_doc_to_pos_index in dictionary.items():
            f.write(pickle.dumps(dictionary_of_doc_to_pos_index)) # Use pickle to save the posting and write to it
            byte_size = f.tell() - current_pointer
            dictionary_to_be_saved[term] = (current_pointer, byte_size, len(dictionary_of_doc_to_pos_index.keys()))
            current_pointer = f.tell()
    
    return dictionary_to_be_saved

'''
Process a content and return a list of all terms in that file.
'''
def process_content(content):
    text = content.replace('\n', ' ')
    preprocessed_text = preprocess_raw_text(text)
    return process_text(preprocessed_text)


'''
Process a text and return a list of all terms in that text.
The terms are normalised and stemmed. 
'''
def process_text(text):
    sentences = nltk.sent_tokenize(text)
    all_terms = []
    for sentence in sentences:
        all_terms.extend(process_sentence(sentence))
    
    return all_terms

'''
Process a sentence and return a list of all terms in that sentence
Stemmer is done using NLTK's PorterStemmer
'''
def process_sentence(sentence):
    words = nltk.word_tokenize(sentence)
    return [process_word(word) for word in words]


'''
Processes the word with operations such as stemming
'''
def process_word(word): 
    if word in stemming_dictionary:
        return stemming_dictionary[word]
    else:
        stemmed_word = stem_raw_word(word)
        stemming_dictionary[word] = stemmed_word
        return stemmed_word

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

input_file = output_file_dictionary = output_file_postings = None

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
    except getopt.GetoptError:
        usage()
        sys.exit(2)
        
    for o, a in opts:
        if o == '-i': # input directory
            input_file = a
        elif o == '-d': # dictionary file
            output_file_dictionary = a
        elif o == '-p': # postings file
            output_file_postings = a
        else:
            assert False, "unhandled option"
            
    if input_file == None or output_file_postings == None or output_file_dictionary == None:
        usage()
        sys.exit(2)

    print("Indexing...")
    clock_and_execute(index, input_file, output_file_dictionary, output_file_postings)

