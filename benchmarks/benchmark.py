#!/usr/bin/python3
"""
Script for running and measuring benchmarks.
This script has to be run as a sudo.
"""
__author__ = "Marek Sedlacek"
__date__ = "January 2022"

import sys
import subprocess

def print_help():
    """
    Prints help message and exits with success
    """
    print("""Usage: {} [opts]
    -[]         No arguments runs all benchmarks
    -ebe <path> Path to Ebe
    -i          Run interpreter benchmarks
    -c          Run compiler benchmarks
    """.format(sys.argv[0]))
    exit(0)

def measure_compile(ebe, f_in, f_out):
    """
    Benchmarks specific test
    :ebe Path to the ebe
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
    precision = result_stdout
    return (time, cpu, precision)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "-h":
        print_help()
    #print(measure_compile("../../ebe/build/ebe", "../../ebe/examples/ex2.in", "../../ebe/examples/ex2.output"))