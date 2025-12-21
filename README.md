LaTeX Calendar Generator
========================

This tool uses python's
[calendar](http://docs.python.org/library/calendar.html) library (which
provides modular `ncal` functionality) to generate a TeX based, A4-sized wall
calendar with one month per page.

Prerequisites
-------------

* Python 3
* [uv](https://docs.astral.sh/uv/getting-started/installation/)
* A working LaTeX installation, including `pdflatex`.

Usage
-----


```
uv run make-calendar.py 2026 # will generate a calendar for 2026
```

The complete invocation syntax is

```
usage: make-calendar [-h] [-d CSV_DATA] [-p PREFIX] [--date-format DATE_FORMAT] [-f FIRST_DAY_OF_WEEK] [-H PUBLIC_HOLIDAYS] [--debug] year

Generate a year calendar with LaTeX.

positional arguments:
  year                  The year for which to generate the calendar

options:
  -h, --help            show this help message and exit
  -d CSV_DATA, --csv-data CSV_DATA
                        Additional data to add to the calendar. See README for details (default: None)
  -p PREFIX, --prefix PREFIX
                        The prefix for the calendar pdf. The program defaults to prefix `cal` if this option is unset. (default: None)
  --date-format DATE_FORMAT
                        The date format (for `strptime`) to expect in the first column of the provided CSV file (default: %d/%m/%Y)
  -f FIRST_DAY_OF_WEEK, --first-day-of-week FIRST_DAY_OF_WEEK
                        On which day to start the week, 0=Monday, 6=Sunday (default: 0)
  -H PUBLIC_HOLIDAYS, --public-holidays PUBLIC_HOLIDAYS
                        Country code (with optional subdivision, separated by ':') to mark public holidays with red day number and public holiday text (default: None)
  --debug               Don't delete the generated LaTeX source file (default: False)
```

The option `--csv-data` is intended to be used for e.g. birthday data and the csv should have three columns containing (in order):

- the date (in `DD/MM/YYYY` format by default, the format can be overridden by option `--date-format`)
- a text to display on that date
- a type marker for the entry.
  Currently, the program will set the text color to red for type marker `HOLIDAY` and to blue for any other non-empty type marker.

Empty lines, lines starting with `#`, lines which don't have exactly three columns, and lines for which the date can't be parsed with the provided format are skipped.

The option `--first-day-of-week` is used to select on which weekday (0=Monday through to 6=Sunday) the week starts.
If the parameter is omitted the week starts on Monday.

The option `--prefix` is used as the prefix for the output file.
If not provided, defaults to `cal`.

The option `--public-holidays` can be set to a country code (or a country code with subdivision separated by a `:`) to mark public holidays with red day number and public holiday text.


Customization
-------------

You can change the calendar style in the file `head.tex.in`. 
Note that all lengths and widths are predefined for DIN A4 paper.
Month and day names will be printed according to `LC_TIME` (or `LC_ALL` if `LC_TIME` is not set separately).
