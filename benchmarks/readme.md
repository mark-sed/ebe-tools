# Ebe benchmarks

Scripts for benchmarking Ebe's performance.

Benchmark contains tests within its directory, but can be run on any tests as long as they follow test structure (described bellow).

_Note_: Tests are made currently only for Linux.

## Running benchmarks

All options and their description can be seen by running:
```
./benchmarks.py -h
```

The benchmarks use process priority (command `nice`), so benchmarks needs to be run with root privileges.  

If ran from structure as is in the git repository, then no arguments need to be provided:
```
./benchmarks.py
```

If Ebe is not under `ebe` command then it needs to be linked using `-ebe <path>` option and the same can be done for test directories. It is also possible to envoke only ebei or ebec benchmarks with `-i` and `-c` command and output result json directory can be specified using `-o` option. For example:
```
./benchmarks.py -i -ebe /usr/bin/ebe -ebei ../ebei_test/ -o ../results/
```

## Plotting benchmarks

Benchmark results (.json files) can be plotted and compared using the `plot_benchmarks.py` script. All its options can be seen running it with `-h` option.

It can plot benchmarks in a form of bar plot or boxplot and save output to many different output formats based on specified output extention. 

Example of plotting single benchmark results:
```
./plot_benchmarks.py ../results.json -bp -o results.png
```

## Test structure

Each test has to reside in its own folder within the ebei/ebec folder, where the name of the folder is then used as the name of the test. All tests can have one `*.args` file containing any additional program arguments (such as `-expr`...).

### Ebec test structure

Ebec benchmarks looks for 2 files:
* `*.in` - containing example input (`-in`),
* `*.out` - containing example output (`-out`).  

And then as already mentioned for optional `*.args` file with program arguments.

Example of such structure with 2 tests would be:
```
ebec-tests/
|- test1/
|  |- test1.in
|  |- test1.out
|  |- test1.args
|- test2/
   |- test2.in
   |- test2.out
```

### Ebei test structure

Ebei benchmarks looks for multiple files:
* `*.ebel` - containing ebel code (`-i`),
* `*.txt` - any `.txt` file will be used for the input (for multi-file interpretation).  

And for optional `*.args` file with program arguments.

Example of such structure with 2 tests would be:
```
ebei-tests/
|- test1/
|  |- test1.ebel
|  |- test1.args
|  |- a.txt
|  |- b.txt
|  |- c.txt
|- test2/
   |- test2.ebel
   |- test2.txt
```
