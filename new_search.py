import re
import nltk
import sys
import getopt
import pickle
import math
from time import time
import utils
from collections import Counter, defaultdict
from postings_eval import evaluate_and
from functools import reduce

# Returns the final output for a query
def evaulate_query(query, doc_length_dictionary, dictionary):
    does_and_exist = utils.check_and_existence(query)

    if does_and_exist:
        query_chunks = utils.query_chunker(query)
        processed_query_chunks = [preprocess_string(single_query) for single_query in query_chunks]
        
        chunk_postings = [ utils.get_postings_for_term(chunk, dictionary, postings_file) for chunk in processed_query_chunks ]
        chunk_postings = [utils.get_first_of_tuple(x) for x in chunk_postings]

        #anded_list is the list of postings that satisfy all the AND queries 
        anded_list = reduce(lambda x, y: evaluate_and(x, y), chunk_postings)
    else:
        query_chunks = query.split()
        processed_query_chunks = [preprocess_string(single_query) for single_query in query_chunks]

    #if the query has no AND, set it to None to be put into get_vsm_scores
    anded_list = anded_list if does_and_exist else None
    
    #vsm_score is a list of tuple sorted in desc order by score. tuple: (doc_id, score)
    vsm_scores = get_vsm_scores(processed_query_chunks, doc_length_dictionary, dictionary, anded_list)
    
    return [doc_id for doc_id, score in vsm_scores]
    # MIGHT BE NONE TAKE CARE LATER

def preprocess_string(single_query):
    processed_query = utils.preprocess_raw_query(single_query)
    query_tokens = nltk.word_tokenize(processed_query)
    sanitised_query_tokens = [utils.stem_raw_word(token) for token in query_tokens]
    return ' '.join(sanitised_query_tokens)

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def get_vsm_scores(processed_query_chunks, doc_length_dictionary, dictionary, allowed_doc_ids=None):
    # We convert it to float here so that operations using N later return floats.
    N = float(utils.get_number_of_documents()) 

    scores = defaultdict(float)
    query_vector = Counter(processed_query_chunks)

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
        
        #this conditional checks if there is AND in the query, and shrink the postings if there is
        if allowed_doc_ids is not None:
            truncated_postings = [posting for posting in postings if posting[0] in allowed_doc_ids]
        else:
            truncated_postings = postings

        # Compute scores for each document
        for doc_id, term_freq_in_doc in truncated_postings:
            log_tf_in_doc = 1 + math.log(term_freq_in_doc, 10)

            scores[doc_id] += log_tf_in_doc * tf_idf_query_token

    # Length of the query vector which can be used for normalisation
    query_vector_length = math.sqrt(sum([dim * dim for dim in query_vector.values()]))

    for doc_id in scores:
        doc_length = doc_length_dictionary[doc_id]
        scores[doc_id] /= doc_length
        scores[doc_id] /= query_vector_length
        
        # We can also divide by query verctor length but since  every score will be divided by 
        # it then, so it would not make a difference to the final results.
        # scores[doc_id] /= query_vector_length

    #return all relevant ids and their vsm scores in sorted order
    return sorted(scores.items(), key=lambda kv: -kv[1])


'''
Get the list of all the document ids
'''
def get_superset():
    dictionary = utils.deserialize_dictionary(dictionary_file)
    return utils.get_postings_for_term('ALL_WORDS_AND_POSTINGS', dictionary, postings_file)


# MAIN SEARCH FUNCTION
def get_postings_for_queries(file_of_queries):
    doc_length_dictionary = utils.deserialize_dictionary('doc_length_dictionary.txt')
    dictionary = utils.deserialize_dictionary(dictionary_file)
    
    query = [line.rstrip('\n') for line in open(file_of_queries)][0]
    output = evaulate_query(query, doc_length_dictionary, dictionary)
    
    # Write the result to the output file
    with open(file_of_output, 'a') as file:
        file.write(' '.join(map(str, output)) + '\n')


if __name__ == "__main__":
    dictionary_file = postings_file = file_of_queries = output_file_of_results = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
    except getopt.GetoptError:
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
