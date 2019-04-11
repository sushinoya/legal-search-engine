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
file_of_queries=tests/input$1.txt
output_of_results_file=tests/output.txt
expected_output_file=tests/expected_output$1.txt

if [[ $* == *-no-index* ]]
then
  python search.py -d $dictionary_file -p $postings_file -q $file_of_queries -o $output_of_results_file
else
  python index.py -i $directory_of_documents -d $dictionary_file -p $postings_file
  python search.py -d $dictionary_file -p $postings_file -q $file_of_queries -o $output_of_results_file
fi

cmp --silent $output_of_results_file $expected_output_file && echo '### Test Passed: Files Are Identical! ###' || echo '### Failed: Files Are Different! ###'
echo "Lines which don't match are:"
diff $output_of_results_file $expected_output_file | grep '^[1-9]'
if [[ $* == *-d* ]]
then 
  diff $output_of_results_file $expected_output_file
else
  echo "Use -d to see the diff between the two files"
fi