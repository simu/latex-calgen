import argparse
import calendar
import locale
import os, os.path
import sys
import tempfile

from datetime import date, datetime
from pathlib import Path

import holidays

HEAD = "head.tex.in"


def translate(h: str, lang: str) -> str:
    de = {
        "Easter Sunday": "Ostern",
        "Whit Sunday": "Pfingsten",
    }
    match lang:
        case "de":
            return de[h]
        case _:
            return h


class LatexCalendar(calendar.Calendar):
    def __init__(self, tempdir: Path, args: argparse.Namespace):
        super(calendar.Calendar, self)

        # set year
        self.year = args.year

        # setup csv data
        if args.csv_data:
            self.parse_file(args)
        else:
            self.data = None

        # configure calendar
        if args.first_day_of_week < 0 or args.first_day_of_week > 6:
            raise ValueError(
                "Expected first day of week to be 0-6 (0: Monday, 6: Sunday)"
            )
        self.setfirstweekday(args.first_day_of_week)

        self.setup_holidays(args)

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

    def setup_holidays(self, args: argparse.Namespace):
        if args.public_holidays:
            if ":" in args.public_holidays:
                cn, div = args.public_holidays.split(":")
            else:
                cn = args.public_holidays
                div = None
            # set holidays language from first part of LC_TIME locale (e.g. "de" for "de_CH.utf-8")
            lang = locale.getlocale(locale.LC_TIME)[0].split("_")[0]
            self.holidays = holidays.country_holidays(
                cn, years=self.year, subdiv=div, language=lang
            )
            self.fixup_holidays(cn, lang)
        else:
            self.holidays = {}

    def fixup_holidays(self, country: str, lang: str):
        match country.lower():
            case "ch":
                # holidays lib goes strictly with CH official documentation which doesn't contain Easter
                # Sunday and Whit Sunday as public holidays. However, most Swiss calendars will have a
                # note for those two Sundays anyway, so we patch the holiday data for CH here.
                self.holidays._add_easter_sunday(translate("Easter Sunday", lang))
                self.holidays._add_whit_sunday(translate("Whit Sunday", lang))

    def parse_file(self, args: argparse.Namespace):
        filename = args.csv_data
        self.data = dict()
        for i in range(1, 13):
            self.data[i] = dict()

        with open(filename, newline="") as datafile:
            for line in datafile:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                try:
                    datum, text, typ = line.split(",")
                    datum = datetime.strptime(datum, args.date_format)
                except ValueError as e:
                    print(f"Skipping entry '{line}': {e}")
                    continue

                self.data.setdefault(datum.month, []).setdefault(datum.day, []).append(
                    (text, typ)
                )

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
                # insert special data
                line = list(l)
                for i, day in enumerate(l):
                    if day == 0:
                        line[i] = ""
                        continue

                    today = date(self.year, month, day)
                    datas = monthdata.get(day, [])

                    if today in self.holidays:
                        datas = [[self.holidays[today], "HOLIDAY"]] + datas

                    # add day number
                    if i == self.sun_index or today in self.holidays:
                        # color sundays and public holidays red
                        line[i] = "\\textcolor{socol}{%s}" % day
                    else:
                        line[i] = str(day)

                    # TODO: refactor + move latex magic into macros
                    # process extra data
                    if len(datas) > 0:
                        if len(datas) > 1:
                            line[i] += "\\vspace*{.2\\baselineskip}"
                        line[i] += "\\newline \\parbox{3.5cm}{\\raggedright\\tiny"

                        for data in datas:
                            if data[1] == "HOLIDAY":
                                color = "socol"
                            elif data[1] != "":
                                color = "special"

                            if data[1] != "":
                                line[i] += " \\textcolor{%s}{%s}\\newline" % (
                                    color,
                                    data[0],
                                )
                            else:
                                line[i] += "{%s}\\newline" % (data[0])
                        line[i] += " }"

                lines.append(
                    "&".join([str(y) if y != 0 else "" for y in line]),
                )

            height = self.heights[len(lines)]

            # output
            for line in lines:
                self.texfile.write(f"{line}\\\\[{height:.1f}cm]\n\hline\n")
            self.texfile.write("\\end{calmonth}\n")

        self.texfile.write("\end{document}\n\n")
        self.texfile.flush()

    def pdflatex(self, outprefix="cal"):
        import subprocess

        ret = subprocess.call(["pdflatex", self.texfile.name])
        if not self.debug and ret == 0:
            fname = os.path.basename(self.texfile.name)
            os.remove(fname + ".aux")
            os.remove(fname + ".log")
            os.rename(fname + ".pdf", "%s_%d.pdf" % (outprefix, self.year))


def main():
    # set locale: used for generating month and day names
    locale.setlocale(locale.LC_ALL, "")
    locale.setlocale(locale.LC_TIME, "")

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
        "--date-format",
        default="%d/%m/%Y",
        help="The date format (for `strptime`) to expect in the first column of the provided CSV file",
    )
    parser.add_argument(
        "-f",
        "--first-day-of-week",
        type=int,
        default=0,
        help="On which day to start the week, 0=Monday, 6=Sunday",
    )
    parser.add_argument(
        "-H",
        "--public-holidays",
        help="Country code (with optional subdivision, separated by ':') to mark public holidays with red day number and public holiday text",
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


if __name__ == "__main__":
    main()
