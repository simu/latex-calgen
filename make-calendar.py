#!/usr/bin/env python

import calendar
import tempfile

HEAD = "head.tex.in"

debug = False

class LatexCalendar(calendar.Calendar):

    def __init__(self, tempdir, *args):
        super(calendar.Calendar, self)

        # set year
        self.year = int(args[0])

        # setup csv data
        if len(args) > 1:
            self.parse_file(args[1])
        else:
            self.data = None

        # configure calendar
        if len(args) > 2:
            self.setfirstweekday(int(args[2]))
        else:
            self.setfirstweekday(0)

        # helper stuff
        self.texfile = tempfile.NamedTemporaryFile(dir=tempdir, mode='w', delete=not debug)
        self.heights = [0] * 7;
        self.heights[4] = 3
        self.heights[5] = 2.5
        self.heights[6] = 1.9
        self.sun_index = [ x for x in self.iterweekdays() ].index(6)

    def parse_file(self, filename):

        self.data = dict()
        for i in range(1, 13):
            self.data[i]=dict()

        with open(filename) as datafile:
            first = True
            for line in datafile:
                if first:
                    first = False
                    continue

                date,name,special=line.strip().split(',')
                d,m,_ = map(int, date.split('/'))

                if (m in self.data.keys() and d in self.data[m].keys()):
                    self.data[m][d].append((name, special))
                else:
                    self.data[m][d] = [(name, special)]

    @property
    def has_bdays(self):
        return self.data is not None

    def generate_file(self):
        # add header to texfile
        with open(HEAD) as header:
            for line in header:
                self.texfile.write(line.replace("%year%", str(self.year)))

        # add months 1 - 12
        for month in range(1,13):
            # get additional data for this month
            if self.has_bdays:
                monthdata = self.data[month]
            else:
                monthdata = dict()

            # table header
            self.texfile.write("\\begin{calmonth}{%s}{%d}\n\hline\n" % (calendar.month_name[month], self.year))
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
                for (day, datas) in monthdata.items():
                    try:
                        i = l.index(day)
                    except ValueError:
                        continue
                    if i != -1:
                        # add day number
                        if i == self.sun_index:
                            # color sundays red
                            line[i] = "\\textcolor{socol}{%s}" % l[i]
                            sunday_done=True
                        else:
                            line[i] = str(l[i])

                        # TODO: refactor + move latex magic into macros
                        # process extra data
                        if len(datas) == 1:
                            data = datas[0]
                            if data[1] != "":
                                line[i] = line[i] + "\\newline \\parbox{3.5cm}{\\raggedright\\tiny\\textcolor{special}{%s}}" % (data[0])
                            else:
                                line[i] = line[i] + "\\newline \\parbox{3.5cm}{\\raggedright\\tiny %s}" % (data[0])
                        elif len(datas) > 1:
                            line[i] = line[i] + "\\vspace*{.5\\baselineskip} \\newline \\parbox{3.5cm}{\\raggedright\\tiny "
                            for data in datas:
                                if data[1] != "":
                                    line[i] = line[i] + " \\textcolor{special}{%s}\\newline" % (data[0])
                                else:
                                    line[i] = line[i] + "{%s}\\newline" % (data[0])
                            line[i] = line[i] + " }"

                    if i == 6:
                        last_day_in_week = True

                if not sunday_done:
                    # color sundays red
                    if line[self.sun_index] != 0:
                        line[self.sun_index] = "\\textcolor{socol}{%s}" % line[self.sun_index]


                # output is more complicated when last day in week has additional data
                lines.append(("&".join([str(y) if y != 0 else "" for y in line]), last_day_in_week))

            height = self.heights[len(lines)]

            # output
            for line,last_day_in_week in lines:
                if last_day_in_week:
                    h = height - 0.8
                else:
                    h = height
                self.texfile.write("%s\\\\[%.1fcm]\n\hline\n"%(line,h))
            #self.texfile.write(("\\\\[%.1fcm]\n\hline\n"%height).join(lines))
            #self.texfile.write("\\\\[%.1fcm]\n\hline\n"%height)
            self.texfile.write("\\end{calmonth}\n")

        self.texfile.write("\end{document}\n\n")
        self.texfile.flush()


    def pdflatex(self):
        import subprocess
        ret = subprocess.call(["pdflatex", self.texfile.name]);
        if not debug and ret == 0:
            import os, os.path
            fname = os.path.basename(self.texfile.name)
            os.remove(fname + ".aux")
            os.remove(fname + ".log")
            os.rename(fname + ".pdf", "cal%d.pdf" % self.year)


def usage(*args):
    print("usage: {} <year> [csv-data [first-day-of-week]]".format(args[0][0]))
    print()
    print("   where first-day-of-week is one of 0=Monday, ..., 6=Sunday")
    print()

# arguments: year, csv-data, weekstart
if __name__ == "__main__":
    # set locale: used for generating month and day names
    import locale
    locale.setlocale(locale.LC_ALL, '')
    locale.setlocale(locale.LC_TIME, '')

    import sys, os
    if len(sys.argv) < 2:
        usage(sys.argv)
        sys.exit(1)

    pc = LatexCalendar(os.path.dirname(sys.argv[0]), *sys.argv[1:])
    pc.generate_file()
    pc.pdflatex()

