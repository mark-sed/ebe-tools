#!/usr/bin/python3
"""
Script for plotting Ebe's benchmark results.
"""
__author__ = "Marek Sedlacek"
__date__ = "January 2022"

import matplotlib.pyplot as plt
import pandas as pd
import json
import sys
import statistics

def print_help():
    """
    Prints script usage info and exits with success
    """
    print("Use: {} benchmark1.json <benchmark2.json>".format(sys.argv[0]))
    exit(0)

def subp(ax, row):
    """
    Returns subplot object based since it might be array or an object
    """
    try:
        return ax[row]
    except:
        return ax

def plot_single(benchmark_json, save_path):
    """
    Plots bar graph of one benchmark
    :param path Path to the benchmark results
    """
    ebec_test_names = None
    ebei_test_names = None
    graph_columns = 1
    graph_rows = 2

    ebec_data = benchmark_json["results"]["ebec"]
    ebei_data = benchmark_json["results"]["ebei"]
    # Extracting ebec results if ebec is not null
    if ebec_data is not None:
        ebec_test_names = list(ebec_data)
    else:
        graph_rows -= 1
    # Extracting ebei results if ebei is not null
    if ebei_data is not None:
        ebei_test_names = list(ebei_data)
    else:
        graph_rows -= 1
    # Plotting
    fig1, ax1 = plt.subplots(graph_rows, graph_columns)
    row = 0
    if ebec_data is not None:
        values = [statistics.median(ebec_data[name]["times"]) for name in ebec_data.keys()]
        subp(ax1, row).barh(ebec_test_names, values, color="#602af5")
        subp(ax1, row).bar_label(subp(ax1, row).containers[0], fmt='%.2f', label_type='edge')
        subp(ax1, row).margins(x=0.12)
        subp(ax1, row).set_xlabel("time [s]")
        subp(ax1, row).set_title("Compilation")
        row += 1
    if ebei_data is not None:
        values = [statistics.median(ebei_data[name]["times"]) for name in ebei_data.keys()]
        subp(ax1, row).barh(ebei_test_names, values, color="#602af5")
        subp(ax1, row).bar_label(subp(ax1, row).containers[0], fmt='%.2f', label_type='edge')
        subp(ax1, row).margins(x=0.12)
        subp(ax1, row).set_xlabel("time [s]")
        subp(ax1, row).set_title("Interpretation")
        row += 1
    fig1.suptitle("Ebe "+benchmark_json["ebe"]["version"]+" benchmarks")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.show()

def load_json(path):
    """
    Loads benchmarks results into a json object
    :param path Path results file
    :return Results as a json object
    """
    parsed = None
    with open(path, "r") as json_f:
        parsed = json.load(json_f)
    return parsed

if __name__ == "__main__":
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == '-h'):
        print_help()
    results_json1 = load_json(sys.argv[1]) #None
    results_json2 = None
    graph_output = "benchmark_graph.png"
    if results_json2 is None:
        # Single plot
        plot_single(results_json1, graph_output)
    else:
        # Double comparison plot
        plot_single(results_json1, graph_output)