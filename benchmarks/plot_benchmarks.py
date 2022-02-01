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

def error(msg):
    print("ERROR: "+msg+".", file=sys.stderr)
    exit(1)

def print_help():
    """
    Prints script usage info and exits with success
    """
    print("""Usage: {} benchmark1.json <benchmark2.json> [opts]
    -bp          Generates boxplot (instead of bar graph).
    -o           Output file.
    -i           Platform information won't be printed.
    """.format(sys.argv[0]))
    exit(0)

def subp(ax, row):
    """
    Returns subplot object based since it might be array or an object
    """
    try:
        return ax[row]
    except:
        return ax

def get_plot_text(benchmark_json):
    """
    :return Text to place under the graph
    """
    p = benchmark_json["platform"]
    cpu = p["cpu"]["model"]+" @ "+str(p["cpu"]["freq_max"])+" MHz"
    ram = str(round(p["memory"]["size"]/1e9, 2))+" GB"
    os = p["os"]
    return f"Processor: {cpu}\nRam: {ram}\nOS: {os}"

def boxplot(benchmark_json, save_path, no_platform_info):
    """
    Plots benchmarks as a boxplot
    :param benchmark_json Benchmarks as a json object
    :param save_path Path to which save the output
    :param no_platform_info If True then the platform information won't be printed
    """
    graph_columns = 1
    graph_rows = 2

    ebec_data = benchmark_json["results"]["ebec"]
    ebei_data = benchmark_json["results"]["ebei"]
    # Extracting ebec results if ebec is not null
    if ebec_data is None:
        graph_rows -= 1
    # Extracting ebei results if ebei is not null
    if ebei_data is None:
        graph_rows -= 1
    # Plotting
    fig1, ax1 = plt.subplots(graph_rows, graph_columns)

    plt.subplots_adjust(bottom=0.1 if no_platform_info else 0.3, hspace=0.6)
    row = 0
    if ebec_data is not None:
        values = {}
        for k, v in ebec_data.items():
            values[k] = v["times"]
        subp(ax1, row).boxplot(values.values())
        subp(ax1, row).set_xticklabels(values.keys())
        subp(ax1, row).set_xlabel("time [s]")
        subp(ax1, row).set_title("Compilation")
        row += 1 
    if ebei_data is not None:
        values = {}
        for k, v in ebei_data.items():
            values[k] = v["times"]
        subp(ax1, row).boxplot(values.values())
        subp(ax1, row).set_xticklabels(values.keys())
        subp(ax1, row).set_xlabel("time [s]")
        subp(ax1, row).set_title("Interpretation")
        row += 1
    # Info text
    if not no_platform_info:
        plt.figtext(0.5, 0.02, get_plot_text(benchmark_json), horizontalalignment='center', color="gray")
    fig1.suptitle("Ebe "+benchmark_json["ebe"]["version"]+" benchmarks")
    plt.savefig(save_path)
    plt.show()

def plot_single(benchmark_json, save_path, no_platform_info):
    """
    Plots bar graph of one benchmark
    :param benchmark_json Benchmarks as a json object
    :param save_path Path to which save the output
    :param no_platform_info If True then the platform information won't be printed
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

    plt.subplots_adjust(bottom=0.1 if no_platform_info else 0.3, left=0.3, hspace=0.6)
    row = 0
    if ebec_data is not None:
        values = [statistics.median(ebec_data[name]["times"]) for name in ebec_data.keys()]
        colors = ["#602af5" if max(ebec_data[name]["precisions"]) == 100.0 else "#ffffff" for name in ebec_data.keys()]
        hatching = ["" if max(ebec_data[name]["precisions"]) == 100.0 else "///" for name in ebec_data.keys()]
        subp(ax1, row).barh(ebec_test_names, values, color=colors, edgecolor='black', linewidth=1, hatch=hatching)
        subp(ax1, row).bar_label(subp(ax1, row).containers[0], fmt='%.2f', label_type='edge')
        subp(ax1, row).margins(x=0.12)
        subp(ax1, row).set_xlabel("time [s]")
        subp(ax1, row).set_title("Compilation")
        row += 1
    if ebei_data is not None:
        values = [statistics.median(ebei_data[name]["times"]) for name in ebei_data.keys()]
        subp(ax1, row).barh(ebei_test_names, values, color="#602af5")
        subp(ax1, row).bar_label(subp(ax1, row).containers[0], fmt='%.2f', label_type='edge')
        subp(ax1, row).margins(x=0.12, y=0.2)
        subp(ax1, row).set_xlabel("time [s]")
        subp(ax1, row).set_title("Interpretation")
        row += 1
    # Info text
    if not no_platform_info:
        plt.figtext(0.5, 0.02, get_plot_text(benchmark_json), horizontalalignment='center', color="gray")
    fig1.suptitle("Ebe "+benchmark_json["ebe"]["version"]+" benchmarks")
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

# TODO: Add precision to plots
# TODO: Add additional info under the graph, maybe even precision table
# TODO: Add option to not print platform info
# TODO: Dont print platform info for comparison (does not need it)
if __name__ == "__main__":
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == '-h'):
        print_help()
    _results_json = []
    _no_platform_info = False
    _graph_output = "benchmark_graph.png"
    _box_plot = False

    _i = 1
    while _i < len(sys.argv):
        if sys.argv[_i][0] != "-":
            _results_json.append(sys.argv[_i])
        elif sys.argv[_i] == "-i":
            _no_platform_info = True
        elif sys.argv[_i] == "-bp":
            _box_plot = True
        elif sys.argv[_i] == "-o":
            if len(sys.argv) <= _i+1:
                error("Missing value for -o option")
            _graph_output = sys.argv[_i+1]
            _i += 1
        else:
            error("Unknown option '{}'".format(sys.argv[_i]))
        _i += 1

    if len(_results_json) == 0:
        error("At least one benchmark file is required")

    _results = [load_json(f) for f in _results_json]

    if len(_results_json) == 1:
        # Single plot
        if _box_plot:
            boxplot(_results[0], _graph_output, _no_platform_info)
        else:
            plot_single(_results[0], _graph_output, _no_platform_info)
    else:
        # Double comparison plot
        pass
