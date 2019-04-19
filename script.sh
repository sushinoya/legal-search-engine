#!/bin/bash

# If --o, use the entire reuters data
if [[ $* == *-o* ]]
then
  dataset_file=dataset/dataset.csv
else
  dataset_file=dataset/dataset_chunked.csv
fi
dictionary_file=dictionary.txt
postings_file=postings.txt
file_of_queries=dataset/q4.txt
output_of_results_file=output.txt

if [[ $* == *-no-index* ]]
then
  python3 new_search.py -d $dictionary_file -p $postings_file -q $file_of_queries -o $output_of_results_file
else
  python3 index.py -i $dataset_file -d $dictionary_file -p $postings_file
  python3 new_search.py -d $dictionary_file -p $postings_file -q $file_of_queries -o $output_of_results_file
fi
