#!/bin/bash
root_dir=$(pwd)
cd "$root_dir/$1" || exit 1

#File: tree-md

tree=$(tree -tf --noreport -I '*~' --charset ascii . |
       sed -e 's/| \+/  /g' -e 's/[|`]-\+/ */g' -e 's:\(* \)\(\(.*/\)\([^/]\+\)\):\1[\4](\2):g')

printf "# Variable files tree consistend across each location\n\n${tree}" >> $root_dir/README.md
cd $root_dir || exit 1
