#!/usr/bin/python3
"""
Script for running and measuring benchmarks.
This script has to be run as a sudo.
"""
__author__ = "Marek Sedlacek"
__date__ = "January 2022"
__version__ = "1.0.0"

import platform
import sys
import subprocess
import re
import os
import json
import psutil
import platform
from datetime import datetime

# Regex for matching whole number or float percentage
RE_PER_NUMBER = re.compile(r'([0-9]+.?[0-9]*)%')
RE_EBE_VERSION = re.compile(r'Ebe ([0-9]+\.[0-9]+\.[0-9]+)')
# Option to exit on warning
werror = False

def print_help():
    """
    Prints help message and exits with success
    """
    print("""Usage: {} [opts]
    No arguments runs all benchmarks.
    This script requires sudo privileges.
    -ebe <path>  Path to Ebe.
    -o           Path to a directory where to save results.
    -i           Run only interpreter benchmarks.
    -c           Run only compiler benchmarks.
    -ebec <path> Path to folder containing ebec tests.
    -ebei <path> Path to folder containing ebei tests.
    -iter <num>  Number of iteration to be done for each test.
    -args "args" Extra compilation arguments.
    -Werror      Exits with error on warning.
    """.format(sys.argv[0]))
    exit(0)

def error(msg):
    print("ERROR: "+msg+".", file=sys.stderr)
    exit(1)

def warning(msg, test):
    print("WARNING: "+test+": "+msg+".", file=sys.stderr)
    if werror:
        error("(Werror) Warning raised, exiting")

def log(msg, test=None, test_number=None, test_amount=None):
    """
    Logs current benchmark status
    :param msg Message to print
    :param test Test name
    :param test_number Test number
    :param test_amount Amount of all tests
    """
    if test_number is not None and test_amount is not None:
        print("TEST({}/{}): ".format(test_number, test_amount), end="", file=sys.stderr)
    else:
        print("INFO: ", end="", file=sys.stderr)
    if test is not None:
        print(test+": ", end="", file=sys.stderr)
    print(msg, file=sys.stderr)

def get_ebe_version(ebe):
    """
    Returns ebe's version
    :return ebe's version number
    """
    result = subprocess.Popen([f"{ebe} --version"],
                              shell=True, stdout=subprocess.PIPE)
    result_stdout = result.communicate()[0].decode("utf-8")
    match = RE_EBE_VERSION.search(result_stdout)
    return match.groups()[0]

def get_ebe_info(ebe):
    """
    Extracts information about used Ebe
    :return Ebe information as a dict
    """
    return {"version": get_ebe_version(ebe)}

def get_cpu_model():
    """
    Attempts to get cpu model name
    :return Model name or empty string
    """
    
    result = subprocess.Popen(["lscpu | sed -nr '/Model name/ s/.*:\s*(.*) @ .*/\\1/p'"],
                              shell=True, stdout=subprocess.PIPE)
    result_stdout = result.communicate()[0].decode("utf-8")
    return result_stdout.rstrip()

def get_platform_info():
    """
    Extracts information about current platform
    :return Platform information as a dictionary
    """
    return  {
                "memory": {"size": psutil.virtual_memory().total},
                "cpu":    {"model": get_cpu_model(),
                           "freq_min": psutil.cpu_freq().min, 
                           "freq_max": psutil.cpu_freq().max,
                           "cores": psutil.cpu_count()
                          },
                "os":     platform.platform()
            }

def measure_ebec(ebe, f_in, f_out, args, timeout=60*5):
    """
    Benchmarks specific test for ebec
    :param ebe Path to ebe
    :param f_in -in file
    :param f_out -out file
    :return touple of strings containing (run time, cpu usage, compilation precision)
    """
    result = subprocess.Popen([f"./measure.sh \"{ebe} -in {f_in} -out {f_out} {args} -t {timeout} -o /dev/null\""],
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

def get_ebei_tests(dir_path):
    """
    Walks directory extracting list of tuples of tests
    :param dir_path Path to the folder containing ebei tests
    :return List of tuples containing test_name, .ebel, list of .txt and args
    """
    tests = []
    all_items = os.listdir(dir_path)
    for item in all_items:
        ebel_file = None
        txt_files = []
        args_file = None
        incorrect = False
        # Get only directories
        if os.path.isdir(dir_path+"/"+item):
            parent = dir_path+"/"+item
            for i in os.listdir(parent):
                f = parent+"/"+i
                if len(f) > 5 and f[-5:] == ".ebel":
                    if ebel_file is None:
                        ebel_file = f
                    else:
                        warning("Multiple ebel files found", parent)
                        incorrect = True
                elif len(f) > 4 and f[-4:] == ".txt":
                    txt_files.append(f)
                elif len(f) > 5 and f[-5:] == ".args":
                    if args_file is None:
                        args_file = f
                    else:
                        warning("Multiple argument (.args) files for ebec found", parent)
                        incorrect = True
            if ebel_file is None:
                warning("Missing ebel (.ebel) file", parent)
                incorrect = True
            if len(txt_files) == 0:
                warning("Missing input files (.txt)", parent)
                incorrect = True
            if incorrect:
                warning("Incorrect structure. Skipping test", parent)
                continue
            tests.append((item, ebel_file, txt_files, extract_args(args_file)))
    return tests

def run_ebec_tests(ebe, ebec_dir, iterations, extra_args):
    """
    Benchmarks all ebec tests in ebe_dir
    :param ebe Path to ebe
    :param ebec_dir Path to ebec tests
    """
    results = {}
    tests = get_ebec_tests(ebec_dir)
    log("Running {} ebec tests ({} iterations).".format(len(tests), iterations))
    curr_num = 1
    for name, f_in, f_out, args in tests:
        results[name] = {"times": [], "cpus": [], "precisions": []}
        log("Started.", "ebec:"+name, curr_num, len(tests))
        for _ in range(iterations):
            mes = measure_ebec(ebe, f_in, f_out, extra_args+" "+args)
            results[name]["times"].append(float(mes[0]))
            results[name]["cpus"].append(int(mes[1]))
            results[name]["precisions"].append(float(mes[2]))
        log("Finished.", "ebec:"+name, curr_num, len(tests))
        curr_num += 1
    return results

def run_ebei_tests(ebe, ebei_dir, iterations):
    """
    Benchmarks all ebei tests in ebe_dir
    :param ebe Path to ebe
    :param ebei_dir Path to ebei tests
    """
    results = {}
    tests = get_ebei_tests(ebei_dir)
    log("Running {} ebei tests ({} iterations).".format(len(tests), iterations))
    curr_num = 1
    for name, f_ebel, f_ins, args in tests:
        results[name] = {"times": [], "cpus": []}
        log("Started.", "ebei:"+name, curr_num, len(tests))
        for _ in range(iterations):
            mes = measure_ebei(ebe, f_ebel, f_ins, args)
            results[name]["times"].append(float(mes[0]))
            results[name]["cpus"].append(int(mes[1]))
        log("Finished.", "ebei:"+name, curr_num, len(tests))
        curr_num += 1
    return results


# TODO: Add support for ebe_all (compilation + interpretation)
# TODO: Save current PC information (to have RPI and PC results)
# TODO: Add option to run just one specific test
if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "-h":
        print_help()
    # Start timer
    _start_time = datetime.now()

    _ebec_dir = "./ebec"
    _ebei_dir = "./ebei"
    _ebe_command = "ebe"
    _json_dir = "."
    _only_i = False
    _only_c = False
    werror = True
    _iterations = 10
    _extra_args = ""

    _i = 1
    while _i < len(sys.argv):
        if sys.argv[_i] == "-ebe":
            if len(sys.argv) <= _i+1:
                error("Missing value for -ebe option")
            _ebe_command = sys.argv[_i+1]
            _i += 1
        elif sys.argv[_i] == "-ebec":
            if len(sys.argv) <= _i+1:
                error("Missing value for -ebec option")
            _ebec_dir = sys.argv[_i+1]
            _i += 1
        elif sys.argv[_i] == "-ebei":
            if len(sys.argv) <= _i+1:
                error("Missing value for -ebei option")
            _ebei_dir = sys.argv[_i+1]
            _i += 1
        elif sys.argv[_i] == "-iter":
            if len(sys.argv) <= _i+1:
                error("Missing value for -iter option")
            try:
                _iterations = int(sys.argv[_i+1])
            except Exception:
                error("Incorrect value '{}' for -iter".format(sys.argv[_i+1]))
            _i += 1
        elif sys.argv[_i] == "-args":
            if len(sys.argv) <= _i+1:
                error("Missing value for -args option")
            _extra_args = sys.argv[_i+1]
            _i += 1
        elif sys.argv[_i] == "-o":
            if len(sys.argv) <= _i+1:
                error("Missing value for -o option")
            _json_dir = sys.argv[_i+1]
            _i += 1
        elif sys.argv[_i] == "-i":
            _only_i = True
        elif sys.argv[_i] == "-c":
            _only_c = True
        elif sys.argv[_i] == "-Werror":
            werror = True
        else:
            error("Unknown option '{}'".format(sys.argv[_i]))
        _i += 1

    log("Using:\n\t-ebec: {}\n\t-ebei: {}\n\t-ebe: {}\n\t-o: {}\n\t-iter: {}\n\t-args: {}\n\t-i: {}\n\t-c: {}\n\t-Werror: {}".format(
          _ebec_dir, _ebei_dir, _ebe_command, _json_dir, _iterations, _extra_args, _only_i, _only_c, werror))

    _ebec_dir = os.path.normpath(_ebec_dir)
    _ebei_dir = os.path.normpath(_ebei_dir)
    _json_dir = os.path.normpath(_json_dir)

    if _only_i and _only_c:
        error("Only -i or -c can be set, not both")

    if not os.path.isdir(_ebec_dir):
        error("Ebec test directory '{}' does not exist or is not a directory".format(_ebec_dir))
    if not os.path.isdir(_ebei_dir):
        error("Ebei test directory '{}' does not exist or is not a directory".format(_ebei_dir))
    if not os.path.isdir(_json_dir):
        error("Output test directory '{}' does not exist or is not a directory".format(_json_dir))
    if not os.path.isfile(_ebe_command):
        # Call ebe as a command
        try:
            subprocess.call([_ebe_command])
        except FileNotFoundError:
            error("Ebe cannot be found as a command nor binary under '{}'".format(_ebe_command))

    _ebec_results = None
    _ebei_results = None
    # Running tests
    if not _only_i:
        _ebec_results = run_ebec_tests(_ebe_command, _ebec_dir, _iterations, _extra_args)
    if not _only_c:
        _ebei_results = run_ebei_tests(_ebe_command, _ebei_dir, _iterations)

    # Save results
    _results = {"benchmark": {
                    "version": __version__,
                    "time:": int(datetime.now().timestamp()),
                    "args": _extra_args
                    },
                "platform": get_platform_info(),
                "ebe": get_ebe_info(_ebe_command),
                "results": {
                    "ebec": _ebec_results, 
                    "ebei": _ebei_results
                    }
               }
    _json_name = datetime.now().strftime("%Y-%m-%d_%H-%M")+"_Ebe"+get_ebe_version(_ebe_command)+"_benchmarks.json"
    with open(_json_dir+"/"+_json_name, "w") as json_f:
        json.dump(_results, json_f, indent=2)

    _run_time = datetime.now() - _start_time
    log("Benchmarks finished ({})".format(str(_run_time)[:str(_run_time).index('.')]))
