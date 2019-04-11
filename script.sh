#!/bin/bash

# If --o, use the entire reuters data
if [[ $* == *-o* ]]
then
  directory_of_documents=reuters_original/training
else
  directory_of_documents=reuters_chunk/training
fi
dictionary_file=dictionary.txt
postings_file=postings.txt
file_of_queries=query.txt
output_of_results_file=output.txt

if [[ $* == *-no-index* ]]
then
  python search.py -d $dictionary_file -p $postings_file -q $file_of_queries -o $output_of_results_file
else
  python index.py -i $directory_of_documents -d $dictionary_file -p $postings_file
  python search.py -d $dictionary_file -p $postings_file -q $file_of_queries -o $output_of_results_file
fi
