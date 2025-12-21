#!/usr/bin/env python3

import argparse
import calendar
import tempfile

from pathlib import Path

HEAD = "head.tex.in"


class LatexCalendar(calendar.Calendar):

    def __init__(self, tempdir: Path, args: argparse.Namespace):
        super(calendar.Calendar, self)

        # set year
        self.year = args.year

        # setup csv data
        if args.csv_data:
            self.parse_file(args.csv_data)
        else:
            self.data = None

        # configure calendar
        if args.first_day_of_week < 0 or args.first_day_of_week > 6:
            raise ValueError(
                "Expected first day of week to be 0-6 (0: Monday, 6: Sunday)"
            )
        self.setfirstweekday(args.first_day_of_week)

        # helper stuff
        self.debug = args.debug
        self.texfile = tempfile.NamedTemporaryFile(
            dir=tempdir, mode="w", delete=not self.debug
        )
        self.heights = [0] * 7
        self.heights[4] = 3
        self.heights[5] = 2.5
        self.heights[6] = 1.9
        self.sun_index = [x for x in self.iterweekdays()].index(6)

    def parse_file(self, filename):

        self.data = dict()
        for i in range(1, 13):
            self.data[i] = dict()

        with open(filename) as datafile:
            first = True
            for line in datafile:
                if first:
                    first = False
                    continue

                date, name, special = line.strip().split(",")
                d, m, _ = map(int, date.split("/"))

                if m in self.data.keys() and d in self.data[m].keys():
                    self.data[m][d].append((name, special))
                else:
                    self.data[m][d] = [(name, special)]

    @property
    def has_bdays(self):
        return self.data is not None

    def generate_file(self):
        # add header to texfile
        with open(HEAD, "r") as header:
            for line in header:
                self.texfile.write(line.replace("%year%", str(self.year)))

        # add months 1 - 12
        for month in range(1, 13):
            # get additional data for this month
            if self.has_bdays:
                monthdata = self.data[month]
            else:
                monthdata = dict()

            # table header
            self.texfile.write(
                "\\begin{calmonth}{%s}{%d}\n\hline\n"
                % (calendar.month_name[month], self.year)
            )
            # table header: day names
            days = [d[0:2] for d in calendar.day_abbr]
            days[self.sun_index] = "\\textcolor{socol}{%s}" % days[self.sun_index]
            self.texfile.write("&".join(days))
            self.texfile.write("\\\\\n\hline\n")

            # generate day entries
            mdays = self.monthdayscalendar(self.year, month)
            lines = []
            for l in mdays:
                sunday_done = False
                last_day_in_week = False
                # insert special data
                line = list(l)
                for day, datas in monthdata.items():
                    try:
                        i = l.index(day)
                    except ValueError:
                        continue
                    if i != -1:
                        # add day number
                        if i == self.sun_index:
                            # color sundays red
                            line[i] = "\\textcolor{socol}{%s}" % l[i]
                            sunday_done = True
                        else:
                            line[i] = str(l[i])

                        # TODO: refactor + move latex magic into macros
                        # process extra data
                        if len(datas) == 1:
                            data = datas[0]
                            if data[1] != "":
                                line[i] = line[
                                    i
                                ] + "\\newline \\parbox{3.5cm}{\\raggedright\\tiny\\textcolor{special}{%s}}" % (
                                    data[0]
                                )
                            else:
                                line[i] = line[
                                    i
                                ] + "\\newline \\parbox{3.5cm}{\\raggedright\\tiny %s}" % (
                                    data[0]
                                )
                        elif len(datas) > 1:
                            line[i] = (
                                line[i]
                                + "\\vspace*{.5\\baselineskip} \\newline \\parbox{3.5cm}{\\raggedright\\tiny "
                            )
                            for data in datas:
                                if data[1] != "":
                                    line[i] = line[
                                        i
                                    ] + " \\textcolor{special}{%s}\\newline" % (data[0])
                                else:
                                    line[i] = line[i] + "{%s}\\newline" % (data[0])
                            line[i] = line[i] + " }"

                    if i == 6:
                        last_day_in_week = True

                if not sunday_done:
                    # color sundays red
                    if line[self.sun_index] != 0:
                        line[self.sun_index] = (
                            "\\textcolor{socol}{%s}" % line[self.sun_index]
                        )

                # output is more complicated when last day in week has additional data
                lines.append(
                    (
                        "&".join([str(y) if y != 0 else "" for y in line]),
                        last_day_in_week,
                    )
                )

            height = self.heights[len(lines)]

            # output
            for line, last_day_in_week in lines:
                if last_day_in_week:
                    h = height - 1
                else:
                    h = height
                self.texfile.write("%s\\\\[%.1fcm]\n\hline\n" % (line, h))
            # self.texfile.write(("\\\\[%.1fcm]\n\hline\n"%height).join(lines))
            # self.texfile.write("\\\\[%.1fcm]\n\hline\n"%height)
            self.texfile.write("\\end{calmonth}\n")

        self.texfile.write("\end{document}\n\n")
        self.texfile.flush()

    def pdflatex(self, outprefix="cal"):
        import subprocess

        ret = subprocess.call(["pdflatex", self.texfile.name])
        if not self.debug and ret == 0:
            import os, os.path

            fname = os.path.basename(self.texfile.name)
            os.remove(fname + ".aux")
            os.remove(fname + ".log")
            os.rename(fname + ".pdf", "%s_%d.pdf" % (outprefix, self.year))


if __name__ == "__main__":
    # set locale: used for generating month and day names
    import locale

    locale.setlocale(locale.LC_ALL, "")
    locale.setlocale(locale.LC_TIME, "")

    import os, sys

    parser = argparse.ArgumentParser(
        prog="make-calendar",
        description="Generate a year calendar with LaTeX.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "year", type=int, help="The year for which to generate the calendar"
    )
    parser.add_argument(
        "-d",
        "--csv-data",
        default=None,
        type=Path,
        help="Additional data to add to the calendar. See README for details",
    )
    parser.add_argument(
        "-p",
        "--prefix",
        help="The prefix for the calendar pdf. The program defaults to prefix `cal` if this option is unset.",
    )
    parser.add_argument(
        "-f",
        "--first-day-of-week",
        type=int,
        default=0,
        help="On which day to start the week, 0=Monday, 6=Sunday",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Don't delete the generated LaTeX source file",
    )

    args = parser.parse_args()

    outprefix = args.prefix or "cal"
    if args.csv_data and not args.prefix:
        print(
            "Using data file name as output prefix. Override this behavior by providing an explicit prefix"
        )
        outprefix = os.path.splitext(args.csv_data)[0]

    pc = LatexCalendar(os.path.dirname(sys.argv[0]), args)
    pc.generate_file()
    pc.pdflatex(outprefix=outprefix)
