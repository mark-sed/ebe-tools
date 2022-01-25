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
import os

# Regex for matching whole number or float percentage
RE_PER_NUMBER = re.compile(r'([0-9]+.?[0-9]*)%')
# Option to exit on warning
werror = False

def print_help():
    """
    Prints help message and exits with success
    """
    print("""Usage: {} [opts]
    No arguments runs all benchmarks.
    This script requires sudo privileges.
    -ebe <path>  Path to Ebe
    -i           Run only interpreter benchmarks
    -c           Run only compiler benchmarks
    -ebec <path> Path to folder containing ebec tests
    -ebei <path> Path to folder containing ebei tests
    -iter <num>  Number of iteration to be done for each test
    -Werror      Exits with error on warning
    """.format(sys.argv[0]))
    exit(0)

def error(msg):
    print("ERROR: "+msg+".", file=sys.stderr)
    exit(1)

def warning(msg, test):
    print("WARNING: "+test+": "+msg+".", file=sys.stderr)
    if werror:
        error("(Werror) Warning raised, exiting")

def measure_ebec(ebe, f_in, f_out, args):
    """
    Benchmarks specific test for ebec
    :param ebe Path to ebe
    :param f_in -in file
    :param f_out -out file
    :return touple of strings containing (run time, cpu usage, compilation precision)
    """
    result = subprocess.Popen([f"./measure.sh \"{ebe} -in {f_in} -out {f_out} {args} -o /dev/null\""],
                              shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_stdout = result.communicate()[0].decode("utf-8")
    result_stderr = result.communicate()[1].decode("utf-8")
    
    time = result_stderr[:result_stderr.index(",")]
    cpu = result_stderr[result_stderr.index(",")+1:len(result_stderr)-2]
    match = RE_PER_NUMBER.search(result_stdout)
    precision = match.groups()[0]
    return (time, cpu, precision)

def measure_ebei(ebe, f_i, f_in, args):
    """
    Benchmarks specific test for ebei
    :param ebe Path to ebe
    :param f_i Ebel code
    :param f_in List of input files
    :return touple of strings containing (run time, cpu usage)
    """
    f_in_str = " ".join(f_in)
    result = subprocess.Popen([f"./measure.sh \"{ebe} -i {f_i} {args} {f_in_str}\""],
                              shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result_stderr = result.communicate()[1].decode("utf-8")
    
    time = result_stderr[:result_stderr.index(",")]
    cpu = result_stderr[result_stderr.index(",")+1:len(result_stderr)-2]
    return (time, cpu)

def extract_args(args_path):
    """
    Extracts arguments from .args file
    :param args_path Path to args file
    :return Arguments in .args file
    """
    if args_path is None:
        return ""
    args_list = []
    with open(args_path, "r") as f_a:
        args_list = [line.rstrip() for line in f_a]
    return "".join(args_list)

def get_ebec_tests(dir_path):
    """
    Walks directory extracting list of tuples of tests
    :param dir_path Path to the folder containing ebec tests
    :return List of tuples containing test_name, .in, .out and args
    """
    tests = []
    all_items = os.listdir(dir_path)
    for item in all_items:
        in_file = None
        out_file = None
        args_file = None
        incorrect = False
        # Get only directories
        if os.path.isdir(dir_path+"/"+item):
            parent = dir_path+"/"+item
            for i in os.listdir(parent):
                f = parent+"/"+i
                if len(f) > 3 and f[-3:] == ".in":
                    if in_file is None:
                        in_file = f
                    else:
                        warning("Multiple input (.in) files for ebec found", parent)
                        incorrect = True
                elif len(f) > 4 and f[-4:] == ".out":
                    if out_file is None:
                        out_file = f
                    else:
                        warning("Multiple output (.out) files for ebec found", parent)
                        incorrect = True
                elif len(f) > 5 and f[-5:] == ".args":
                    if args_file is None:
                        args_file = f
                    else:
                        warning("Multiple argument (.args) files for ebec found", parent)
                        incorrect = True
            if in_file is None:
                warning("Missing input (.in) file", parent)
                incorrect = True
            if out_file is None:
                warning("Missing output (.out) file", parent)
                incorrect = True
            if incorrect:
                warning("Incorrect structure. Skipping test", parent)
                continue
            tests.append((item, in_file, out_file, extract_args(args_file)))
    return tests

def run_ebec_tests(ebe, ebec_dir, iterations):
    """
    Benchmarks all ebec tests in ebe_dir
    :param ebe Path to ebe
    :param ebec_dir Path to ebec tests
    """
    results = {}
    for name, f_in, f_out, args in get_ebec_tests(ebec_dir):
        results[name] = {"times": [], "cpus": [], "precisions": []}
        for _ in range(iterations):
            mes = measure_ebec(ebe, f_in, f_out, args)
            results[name]["times"].append(mes[0])
            results[name]["cpus"].append(mes[1])
            results[name]["precisions"].append(mes[2])
    return results


# TODO: Add support for ebe_all (compilation + interpretation)
# TODO: Save current PC information (to have RPI and PC results)
# TODO: Add option to run just one specific test
if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "-h":
        print_help()
    ebec_dir = "./ebec"
    ebei_dir = "./ebei"
    ebe_command = "ebe"
    only_i = False
    only_c = False
    werror = True
    iterations = 5

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-ebe":
            if len(sys.argv) < i+1:
                error("Missing value for -ebe option")
            ebe_command = sys.argv[i+1]
            i += 1
        elif sys.argv[i] == "-ebec":
            if len(sys.argv) < i+1:
                error("Missing value for -ebec option")
            ebec_dir = sys.argv[i+1]
            i += 1
        elif sys.argv[i] == "-ebei":
            if len(sys.argv) < i+1:
                error("Missing value for -ebei option")
            ebei_dir = sys.argv[i+1]
            i += 1
        elif sys.argv[i] == "-iter":
            if len(sys.argv) < i+1:
                error("Missing value for -iter option")
            try:
                iterations = int(sys.argv[i+1])
            except Exception:
                error("Incorrect value '{}' for -iter".format(sys.argv[i+1]))
            i += 1
        elif sys.argv[i] == "-i":
            only_i = True
        elif sys.argv[i] == "-c":
            only_c = True
        elif sys.argv[i] == "-Werror":
            werror = True
        else:
            error("Unknown option '{}'".format(sys.argv[i]))
        i += 1

    print("Using:\n\t-ebec: {}\n\t-ebei: {}\n\t-ebe: {}\n\t-iter: {}\n\t-i: {}\n\t-c: {}\n\t-Werror: {}\n\t".format(
          ebec_dir, ebei_dir, ebe_command, iterations, only_i, only_c, werror))

    ebec_dir = os.path.normpath(ebec_dir)
    ebei_dir = os.path.normpath(ebei_dir)

    if only_i and only_c:
        error("Only -i or -c can be set, not both")

    if not os.path.isdir(ebec_dir):
        error("Ebec test directory '{}' does not exist or is not a directory".format(ebec_dir))
    if not os.path.isdir(ebei_dir):
        error("Ebei test directory '{}' does not exist or is not a directory".format(ebei_dir))
    if not os.path.isfile(ebe_command):
        # Call ebe as a command
        try:
            subprocess.call([ebe_command])
        except FileNotFoundError:
            error("Ebe cannot be found as a command nor binary under '{}'".format(ebe_command))

    if not only_i:
        ebec_results = run_ebec_tests(ebe_command, ebec_dir, iterations)
        print(ebec_results)

    #print(measure_ebec("../../ebe/build/ebe", "../../ebe/examples/ex2.in", "../../ebe/examples/ex2.output"))
    #print(measure_ebei("../../ebe/build/ebe", "../../ebe/examples/ex2.ebel", ["../../ebe/examples/ex2.in"]))