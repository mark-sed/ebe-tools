#!/bin/bash

# Author: Marek Sedlacek
# Date: January 2022
# 
# Bash script used by Ebe benchmarks to execute
# and measure Ebe's benchmark tests
#
# This script has to be run as a sudo

bash one_core.sh 4 time -f "%e,%P" "$1" | tail -n 1 | grep -Eoh "[0-9]+.?[0-9]*" | tr -d '%' | tr -d '\n'
