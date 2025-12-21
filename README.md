LaTeX Calendar Generator
========================

This tool uses python's
[calendar](http://docs.python.org/library/calendar.html) library (which
provides modular `ncal` functionality) to generate a TeX based, A4-sized wall
calendar with one month per page.

Prerequisites
-------------

* Python 3
* A working LaTeX installation, including `pdflatex`.

Usage
-----


	./make-calendar.py 2012 # will generate a calendar for 2012

The complete invocation syntax is

```
usage: make-calendar [-h] [-d CSV_DATA] [-p PREFIX] [-f FIRST_DAY_OF_WEEK] [--debug] year

Generate a year calendar with LaTeX.

positional arguments:
  year                  The year for which to generate the calendar

options:
  -h, --help            show this help message and exit
  -d CSV_DATA, --csv-data CSV_DATA
                        Additional data to add to the calendar. See README for details (default: None)
  -p PREFIX, --prefix PREFIX
                        The prefix for the calendar pdf. The program defaults to prefix `cal` if this option is unset. (default: None)
  -f FIRST_DAY_OF_WEEK, --first-day-of-week FIRST_DAY_OF_WEEK
                        On which day to start the week, 0=Monday, 6=Sunday (default: 0)
  --debug               Don't delete the generated LaTeX source file (default: False)
```

The option `--csv-data` is intended to be used for e.g. birthday data and the csv should have three columns containing: 

- the date in `M/D/YYYY` format
- a text to display on that date
- a type for the entry

The first line of the CSV file is ignored

The option `--first-day-of-week` is used to select on which weekday (0=Monday through to 6=Sunday) the week starts.
If the parameter is omitted the week starts on Monday.

The option `--prefix` is used as the prefix for the output file.
If not provided, defaults to `cal`.


Customization
-------------

You can change the calendar style in the file `head.tex.in`. 
Note that all lengths and widths are predefined for DIN A4 paper.
Month and day names will be printed according to `LC_TIME` (or `LC_ALL` if `LC_TIME` is not set separately).
