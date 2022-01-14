#!/usr/bin/python3
"""
Script for plotting Ebe's analytics (-a) output.
"""
__author__ = "Marek Sedlacek"
__date__ = "December 2021"

import matplotlib.pyplot as plt
import csv
import sys

def print_help():
    """
    Prints script usage info and exits with success
    """
    print("Use: {} data.csv <output_image> <xlabel> <ylabel> <title>".format(sys.argv[0]))
    exit(0)


if __name__ == "__main__":
    # Argument handeling
    if len(sys.argv) <= 1 or (len(sys.argv) == 2 and sys.argv[1] == "-h"):
        print_help()

    data = []
    x_data = []
    y_data = []
    with open(sys.argv[1]) as csvf:
        reader = csv.reader(csvf, delimiter=',')
        for row in reader:
            if int(row[0]) in x_data:
                data.append((x_data, y_data))
                x_data = []
                y_data = []
            x_data.append(int(row[0]))
            y_data.append(float(row[1]))
        data.append((x_data, y_data))

    e_num = 1
    for x, y in data:
        plt.plot(x, y, label='Evolution {}'.format(e_num))
        e_num += 1

    # Parse args to graph
    if len(sys.argv) >= 4:
        plt.xlabel(sys.argv[3])
    if len(sys.argv) >= 5:
        plt.ylabel(sys.argv[4])
    if len(sys.argv) >= 6:
        plt.title(sys.argv[5])
    plt.ylim([0.0, 1.05])
    plt.legend()
    # Show graph and save it to a pdf
    if len(sys.argv) >= 3:
        plt.savefig(sys.argv[2])
    plt.show()
