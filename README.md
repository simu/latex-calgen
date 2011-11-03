LaTeX Calendar Generator
========================

This tool uses the bsd utility `ncal` to generate a simple wall calendar with
one page per month. The output of `ncal` is parsed using a small perl script.


Usage
-----

	YEAR=2012 make # will generate a calendar for 2012

You have to specify the year as the environment variable `YEAR`, otherwise make
will abort. You can also specify the environment variable `WEEK_START` which
should be eiter `-M` if you want the week to start on Monday or `-S` if you
want the week to start on Sunday. Standard behaviour is to start the week on Monday.

Customization
-------------

You can change the calendar style in the file `head.tex.in`. Note that all
lengths and widths are predefined for DIN A4 paper. Month names will be
printed according to `LC_TIME` (or `LC_ALL` if `LC_TIME` is not set
separately).
