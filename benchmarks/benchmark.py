#!/usr/bin/python3
"""
Script for running and measuring benchmarks.
This script has to be run as a sudo.
"""
__author__ = "Marek Sedlacek"
__date__ = "January 2022"

import sys
import subprocess
import re

# Regex for matching whole number or float percentage
RE_PER_NUMBER = re.compile(r'([0-9]+.?[0-9]*)%')

def print_help():
    """
    Prints help message and exits with success
    """
    print("""Usage: {} [opts]
    No arguments runs all benchmarks.
    This script requires sudo privileges.
    -ebe <path> Path to Ebe
    -i          Run interpreter benchmarks
    -c          Run compiler benchmarks
    """.format(sys.argv[0]))
    exit(0)

def measure_ebec(ebe, f_in, f_out):
    """
    Benchmarks specific test for ebec
    :ebe Path to ebe
    :f_in -in file
    :f_out -out file
    :return touple of strings containing (run time, cpu usage, compilation precision)
    """
    result = subprocess.Popen([f"./measure.sh \"{ebe} -in {f_in} -out {f_out} -o /dev/null\""],
                              shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_stdout = result.communicate()[0].decode("utf-8")
    result_stderr = result.communicate()[1].decode("utf-8")
    
    time = result_stderr[:result_stderr.index(",")]
    cpu = result_stderr[result_stderr.index(",")+1:len(result_stderr)-2]
    match = RE_PER_NUMBER.search(result_stdout)
    precision = match.groups()[0]
    return (time, cpu, precision)

def measure_ebei(ebe, f_i, f_in):
    """
    Benchmarks specific test for ebei
    :ebe Path to ebe
    :f_i Ebel code
    :f_in List of input files
    :return touple of strings containing (run time, cpu usage)
    """
    f_in_str = " ".join(f_in)
    result = subprocess.Popen([f"./measure.sh \"{ebe} -i {f_i} {f_in_str}\""],
                              shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_stderr = result.communicate()[1].decode("utf-8")
    
    time = result_stderr[:result_stderr.index(",")]
    cpu = result_stderr[result_stderr.index(",")+1:len(result_stderr)-2]
    return (time, cpu)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "-h":
        print_help()
    # TODO: Extract call path from argv[0] to use as a prefix for folders
    
    #print(measure_ebec("../../ebe/build/ebe", "../../ebe/examples/ex2.in", "../../ebe/examples/ex2.output"))
    #print(measure_ebei("../../ebe/build/ebe", "../../ebe/examples/ex2.ebel", ["../../ebe/examples/ex2.in"]))