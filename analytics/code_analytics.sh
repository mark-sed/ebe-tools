#!/bin/bash

echo "Ebe code analytics:"
echo "-------------------"

printf "Amount of files: "
find $1 -type f -not -path "*build/*" -not -path "*googletest/*" -not -path "*logs/*" -not -path "*.git/*" -not -path "*.vscode/*" -not -name "*.git*" -not -path "*html/*" | wc -l

printf "Word count for all source code files:"
cat $(find $1 \( -name "*.cpp" -or -name "*.hpp" -or -name "*.h" -or -name "*.cc" -or -name "*.sh" -or -name "*.py" \) -not -path "*build/*" -prune) | wc 

printf "Word count for C++ source code files excluding tests:"
cat $(find $1 \( -name "*.cpp" -or -name "*.hpp" -or -name "*.h" -or -name "*.cc" \) -not -path "*build/*" -prune -not -path "*googletest/*") | wc 

printf "Word count for only proprietary source C++ code:"
cat $(find $1 \( -name "*.cpp" -or -name "*.hpp" \) -not -path "*build/*" -prune -not -name "*lexer_*.[ch]pp" -not -name "*parser_*.[ch]pp") | wc 

