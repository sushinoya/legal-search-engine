import re
import nltk
import sys
import getopt
import pickle
import math
from time import time
import utils
from collections import Counter, defaultdict
from heapq import nlargest

def evaulate_query(query, doc_length_dictionary, dictionary):
    # Stems the query and normalises some terms
    processed_query = utils.preprocess_raw_query(query)
    query_tokens = nltk.word_tokenize(query)
    sanitised_query_tokens = [utils.preprocess_raw_word(token) for token in query_tokens]

    # We convert it to float here so that operations using N later return floats.
    N = float(utils.get_number_of_documents()) 

    scores = defaultdict(float)
    query_vector = Counter(sanitised_query_tokens)

    for token in query_vector:
        df = utils.get_doc_freq_for_term(token, dictionary)
        idf = math.log(N / df, 10) if df != 0 else 0.0
        log_tf = 1 + math.log(query_vector[token], 10)

        # Compute the weight for the token in the query
        tf_idf_query_token = log_tf * idf

        # Update term in query vector to reflect tf-idf
        query_vector[token] = tf_idf_query_token

        # Get postings list for token.
        postings = utils.get_postings_for_term(token, dictionary, postings_file)

        # Copmute scores for each document
        for doc_id, term_freq_in_doc in postings:
            log_tf_in_doc = 1 + math.log(term_freq_in_doc, 10)
            scores[doc_id] += log_tf_in_doc * tf_idf_query_token

    # Length of the query vector which can be used for normalisation
    query_vector_length = math.sqrt(sum([dim * dim for dim in query_vector.values()]))

    for doc_id in scores:
        doc_length = doc_length_dictionary[doc_id]
        scores[doc_id] /= doc_length  
        
        # We can also divide by query verctor length but since  every score will be divided by 
        # it then, so it would not make a difference to the final results.
        # scores[doc_id] /= query_vector_length

    # Return the document ids with the 10 highest scores
    return [x[0] for x in nlargest(10, scores.items(), key=lambda x: x[1])]

'''
Get the list of all the document ids
'''
def get_superset():
    dictionary = utils.deserialize_dictionary(dictionary_file)
    return utils.get_postings_for_term('ALL_WORDS_AND_POSTINGS', dictionary, postings_file)


def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"


# MAIN SEARCH FUNCTION
def get_postings_for_queries(file_of_queries):
    doc_length_dictionary = utils.deserialize_dictionary('doc_length_dictionary.txt')
    dictionary = utils.deserialize_dictionary(dictionary_file)
    # List of queries as strings fom the query file
    queries = [line.rstrip('\n') for line in open(file_of_queries)]
    for query in queries:
        output = evaulate_query(query, doc_length_dictionary, dictionary)
        # Write the result to the output file
        with open(file_of_output, 'a') as file:
            file.write(' '.join(map(str, output)) + '\n')


if __name__ == "__main__":
    dictionary_file = postings_file = file_of_queries = output_file_of_results = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
    except getopt.GetoptError, err:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == '-d':
            dictionary_file = a
        elif o == '-p':
            postings_file = a
        elif o == '-q':
            file_of_queries = a
        elif o == '-o':
            file_of_output = a
        else:
            assert False, "unhandled option"

    if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None:
        usage()
        sys.exit(2)

    # Delete content from the output file
    with open(file_of_output, "w"):
        pass

    utils.clock_and_execute(get_postings_for_queries, file_of_queries)
