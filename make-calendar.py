#!/usr/bin/env python

import calendar
import tempfile

HEAD = "head.tex.in"

debug = False

class LatexCalendar(calendar.Calendar):


	def __init__(self, *args):
		super(calendar.Calendar, self)
		self.year = int(args[0])
		self.setfirstweekday(int(args[1]))
		if len(args) > 2:
			self.bday_file = args[2]
		else:
			self.bday_file = None
		self.texfile = tempfile.NamedTemporaryFile(delete=debug)
		self.heights = [0] * 7;
		self.heights[4] = 3
		self.heights[5] = 2.5
		self.heights[6] = 1.9
		self.sun_index = [ x for x in self.iterweekdays() ].index(6)

	@property
	def has_bdays(self):
		return self.bday_file is not None

	def generate_file(self):
		# add header to texfile
		with open(HEAD) as header:
			for line in header:
				self.texfile.write(line.replace("%year%", str(self.year)))

		# add months 1 - 12
		for month in xrange(1,13):
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
			for line in mdays:
				if line[self.sun_index] != 0:
					line[self.sun_index] = "\\textcolor{socol}{%s}" % line[self.sun_index]
				lines.append("&".join([str(y) if y != 0 else "" for y in line]))
			height = self.heights[len(lines)]

			# output
			self.texfile.write(("\\\\[%.1fcm]\n\hline\n"%height).join(lines))
			self.texfile.write("\\\\[%.1fcm]\n\hline\n"%height)
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


def usage():
	pass

# arguments: year, weekstart, birthday file
if __name__ == "__main__":
	import locale
	locale.setlocale(locale.LC_ALL, '')

	import sys
	if len(sys.argv) < 3:
		usage()

	pc = LatexCalendar(*sys.argv[1:])
	pc.generate_file()
	pc.pdflatex()

