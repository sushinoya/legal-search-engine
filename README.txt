This is the README file for A0155836W-A0157691U submission

== Python Version ==

We're using Python Version <2.7.10> for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

Indexing: Indexing is almost the same as the previous assignment. Here is how we index:
1. Go thorugh each file and do the following to each file:
1.a. Read it's content and load it into the program
1.b. Stem and tokenize the text.
1.c. Add the (document_id, term_frequency) to the postings list for each word in the stemmed text
2. Save all the postings lists in postings.txt
3. Save a dictionary of all the words in dictionary.txt. The value of this dictionary is
   (offset, data_chunk_length, document_frequency_of_word). The first two are used to retreive
   the postings list from postings.txt
4. Save a last dictionary in doc_length_dictionary.txt. This one is rather interesting. We construct the
   document vector for each document and find the length of that vector. This vector's elements are
   the log term frequencies of the words in the document.

Searching: 
5. For each query in the query file, preprocess it, tokenise it and follow the following steps:
5.a. For every term in the query, find it's tf-idf score. Then get all the postings of this term.
5.a.a For each document in the just retrived postings, find it's log term frequency and update the score
      of the document by adding (doc's log term frequency * term's tf-idf)
6. For each document's score, divide it by the document length stored in doc_length_dictionary.txt
   to normalise the score.
7. We should have ideally also divided by the query vector length but since all scores will be divided
   by the same number, its unnecessary.
8. Write the document ids with the top 10 highest scores to the output file.

This procedure implicitly computes the cosine difference between the query and document vectors.
Step 5.a.a is essentially computing the dot product going dimension by dimension (here a dimension
is a word). And then steps 6-7 are the normalising steps.


== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.
1. index.py - file for indexing the terms, and save them to dictionary.txt and postings.txt
2. dictionary.txt - the dictionary of the terms that are being indexed
3. postings.txt - the postings of the terms that are being indexed
4. search.py - file for executing the queries.
5. utils.py - file that contains some utility functions
6. README.txt - this file that you're reading

== Statement of individual work ==

Please initial one of the following statements.

[X] I, A0155836W-A0157691U, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:

<Please fill in>

== References ==
nil (or None in python :p)

<Please list any websites and/or people you consulted with for this
assignment and state their role>
