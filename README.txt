This is the README file for A0155836W-A0157691U submission

== Python Version ==

We're using Python Version <3.7.2> for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

Indexing:
1. Go thorugh each document in the dataset and do the following to each document:
1.a. Read it's content
1.b. Stem and tokenize the content
1.b.1. We speed up stemming by using a dictionary to store stemmed words, because stemming takes a significant
        amount of time. If a word has been stemmed before, simply return the stemmed word from the dictionary,
        else stem it. There is a significant speed up after doing this (at least 2x).
1.c. Put the content into a Counter and store that into a dictionary whose key is the document id.
1.d. We use positional indexing for this assignment. First we used a dictionary whose key is the stemmed
        words. The value associated with each key is another dictionary of {doc_id: list of positional index}.
        This will be saved into our postings list later on. 
2. Save the document vectors into a file doc_vector.txt       
3. Save all the postings lists in postings.txt
4. Save a dictionary of all the words in dictionary.txt. The value of this dictionary is
   (offset, data_chunk_length, document_frequency_of_word). The first two are used to retreive
   the postings list from postings.txt
5. Save a last dictionary in doc_length_dictionary.txt. This one is rather interesting. We construct the
   document vector for each document and find the length of that vector. This vector's elements are
   the log term frequencies of the words in the document.

Searching: 
1. First we check if the query contains any 'AND'

1.a. If it does not, 
1.a.1. Tokenize and stem the query
1.a.2. Do a normal VSM (can be augmented with wordnet and/or Rocchio. More on this later.) More
        explanation of this VSM is provided in step 2.

1.b. If it does: say the query is `Alice AND Bob`.
1.b.1. Tokenize and stem the query. For this example let's assume that 'Alice' and 'Bob' do not change after stemming.
1.b.2. We first find all documents that contain 'Alice' and 'Bob'. We merge the postings together using the merge
        algorithm we learnt in the class. With these merged postings, we do a VSM with the queries stripped of the 'AND'.
        For example if the merged postings is 1, 5, 7, 9, 11. We will search `Alice Bob` on these merged postings. 
        The result is a ranked retrieval, and all the ranked documents will contain occurences of 'Alice' and 'Bob'.
1.b.3. We then do a normal VSM like that of step 1.a.2 e.g. search `Alice Bob` on all documents now. This step will return us
        a large number of ranked documents. We take the result from this step and minus the result from 1.b.2 to avoid duplicates.
1.b.4. Combine the result from step 1.b.2 and 1.b.3. Results from 1.b.2 will always be ranked higher than results from 1.b.3
        because all results from 1.b.1 satisfy the 'AND' condition. 
1.c. We analysed our results from a several queries. We found that step 1.b.2 perform well because it returns a ranked list of 
        documents which fulfill all the 'AND' queries. So we are fairly confident that documents retrieved from this step should
        be ranked the highest. 


2. In this step we discuss the VSM algorithm. 
2.a. (Optional) Perform relevance feedback(Rocchio) on the query vector with the relevant documents that the lawyers have provided.
2.b. For every term in the query, find it's tf-idf score. Then get all the postings of this term.
2.b.1 For each document in the just retrived postings, find it's log term frequency and update the score
      of the document by adding (doc's log term frequency * term's tf-idf)
2.c. For each document's score, divide it by the document length stored in doc_length_dictionary.txt
   to normalise the score.
2.d. We should have ideally also divided by the query vector length but since all scores will be divided
   by the same number, its unnecessary.
2.e. Return all relevant document ids sorted in descending order by their scores.

This procedure implicitly computes the cosine difference between the query and document vectors.
Step 2.b.1 is essentially computing the dot product going dimension by dimension (here a dimension
is a word). And then steps 2.c-2.d are the normalising steps.


Discussion of phrasal queries:
For phrasal queries like 'fertility treatment', they are first stemmed individually. In this case it will be
'fertil treatment'. We will then search for this stemmed phrase using positional indexing e.g. find all 
documents containing 'fertil', and all documents containing 'treatment'. From there, return the documents 
where the position of 'treatment' is +1 relative to the position of 'fertil'.
In our system, we have made the decision not to split up a phrasal query e.g. split 'fertility treatment' into 
'fertility' and 'treatment' because we think that is not the point of phrasal queries. 

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
7. doc_length_dictionary.txt - a file containing the document length of each document
8. doc_vector.txt - a file containing the document vector of each document
9. Bonus.docx - the bonus file

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
