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
def evaulate_query(query, doc_length_dictionary, dictionary, relevant_doc_ids=[]):
    does_and_exist = utils.check_and_existence(query)

    if does_and_exist:
        query_chunks = utils.query_chunker(query)
        processed_query_chunks = [ ' '.join(preprocess_string(single_query)) for single_query in query_chunks ]

        chunk_postings = [ utils.get_postings_for_word_or_phrase(chunk, dictionary, postings_file) for chunk in processed_query_chunks ]
        list_list_of_doc_ids = [ list(dic.keys()) for dic in chunk_postings ]

        #anded_list is the list of postings that satisfy all the AND queries 
        anded_list = reduce(lambda x, y: evaluate_and(x, y), list_list_of_doc_ids)        
    else:
        processed_query_chunks = preprocess_string(query)
        #['scandal', 'exchang', 'evaluate']
        #['fertility treatment', 'damage']

    #if the query has no AND, set it to None to be put into get_vsm_scores
    anded_list = anded_list if does_and_exist else None

    #vsm_score is a list of tuple sorted in desc order by score. tuple: (doc_id, score)
    vsm_scores = get_vsm_scores(processed_query_chunks, doc_length_dictionary, dictionary, relevant_doc_ids, anded_list)
    print(processed_query_chunks)
    print(vsm_scores)
    if does_and_exist:
        top_docs = { doc[0] for doc in vsm_scores }
        ranked_every_doc = get_vsm_scores(processed_query_chunks, doc_length_dictionary, dictionary, relevant_doc_ids)
        filtered_low_priority_docs = [ doc for doc in ranked_every_doc if doc[0] not in top_docs ]

    combined_score = vsm_scores + (filtered_low_priority_docs if does_and_exist else [])
    print(combined_score)
    return [doc_id for doc_id, score in combined_score]

def preprocess_string(single_query):
    processed_query = utils.preprocess_raw_query(single_query)
    query_tokens = nltk.word_tokenize(processed_query)
    return [utils.stem_raw_word(token) for token in query_tokens]

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def get_vsm_scores(processed_query_chunks, doc_length_dictionary, dictionary, relevant_doc_ids=[], allowed_doc_ids=None):
    # We convert it to float here so that operations using N later return floats.
    N = float(utils.get_number_of_documents()) 

    scores = defaultdict(float)
    query_vector = Counter(processed_query_chunks)

    # Construct query vector
    for token in query_vector:
        df = utils.get_doc_freq_for_term(token, dictionary, postings_file)
        idf = math.log(N / df, 10) if df != 0 else 0.0
        log_tf = 1 + math.log(query_vector[token], 10)

        # Compute the weight for the token in the query
        tf_idf_query_token = log_tf * idf

        # Update term in query vector to reflect tf-idf
        query_vector[token] = tf_idf_query_token
    

    # Relevance Feedback
    relevant_term_freq_doc_vectors = [utils.get_doc_vector(doc_id) for doc_id in relevant_doc_ids]
    relevant_tf_idf_doc_vectors = []
    
    for term_tf_dict in relevant_term_freq_doc_vectors:
        term_tf_idf_dict = {}
        for term, tf in term_tf_dict.items():
            log_tf = 1 + math.log(tf, 10)
            df = utils.get_doc_freq_for_term(term, dictionary, postings_file)
            idf = idf = math.log(N / df, 10) if df != 0 else 0.0
            term_tf_idf_dict[term] = log_tf * idf
        relevant_tf_idf_doc_vectors.append(term_tf_idf_dict)

    alpha = 2
    beta = 0.3

    sum_of_relevant_document_vectors = {}
    for vector in relevant_tf_idf_doc_vectors:
        sum_of_relevant_document_vectors = utils.add_vectors(sum_of_relevant_document_vectors, vector)
    
    scaled_sum_of_doc_vectors = utils.multiply_vector(sum_of_relevant_document_vectors, beta)

    normalising_length_of_vectors = 1/len(relevant_doc_ids) if len(relevant_doc_ids) > 0 else 1
    normalised_sum_of_doc_vectors = utils.multiply_vector(scaled_sum_of_doc_vectors, normalising_length_of_vectors)
    new_query_vector = utils.add_vectors(utils.multiply_vector(query_vector, alpha), normalised_sum_of_doc_vectors)
    # q_m = a * query + b(1/2)(doc1 + doc2)


    # Construct document vectors
    for token in new_query_vector:
        # Get postings dictionary for token {doc_id, term_freq}
        postings_dict = utils.get_postings_for_word_or_phrase(token, dictionary, postings_file)
        postings = postings_dict.keys()

        #this conditional checks if there is AND in the query, and shrink the postings if there is
        if allowed_doc_ids is not None:
            truncated_postings = [posting for posting in postings if posting in allowed_doc_ids]
        else:
            truncated_postings = postings

        # Compute scores for each document
        for doc_id in truncated_postings:
            term_freq_in_doc = postings_dict[doc_id]
            tf_idf_query_token = new_query_vector[token]
            log_tf_in_doc = 1 + math.log(term_freq_in_doc, 10)
            # print(f"tf_idf_query_token: {tf_idf_query_token}")

            scores[doc_id] += log_tf_in_doc * tf_idf_query_token

    # Length of the query vector which can be used for normalisation
    query_vector_length = math.sqrt(sum([dim * dim for dim in new_query_vector.values()]))

    for doc_id in scores:
        doc_length = doc_length_dictionary[doc_id]
        scores[doc_id] /= doc_length
        
        # We can also divide by query verctor length but since  every score will be divided by 
        # it then, so it would not make a difference to the final results.
        # scores[doc_id] /= query_vector_length

    #return all relevant ids and their vsm scores in sorted order
    return sorted(scores.items(), key=lambda kv: -kv[1])


# MAIN SEARCH FUNCTION
def get_postings_for_queries(file_of_queries):
    doc_length_dictionary = utils.deserialize_dictionary('doc_length_dictionary.txt')
    dictionary = utils.deserialize_dictionary(dictionary_file)


    lines = [line.rstrip('\n') for line in open(file_of_queries)]
    query = lines[0]
    relevant_doc_ids = lines[1:]
    output = evaulate_query(query, doc_length_dictionary, dictionary, relevant_doc_ids)
    
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
