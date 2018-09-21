#!/bin/bash

original_basename=$(print_tags $1 |grep "original_basename" |cut -d "'" -f 2 |cut -d "." -f 1)
convert "$1" "$(dirname $1)/$original_basename.jpeg"
inject_file --plugin=test_move "$(dirname $1)/$original_basename.jpeg"
