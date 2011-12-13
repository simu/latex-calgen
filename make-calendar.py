import calendar

class LatexCalendar(calendar):

	def __init__(self, *args):
		self.year = args[0]
		self.cal = super(args[1])
		self.bday_file = args[2]
	
	@property
	def has_bdays(self):
		return self.bday_file is not None
	
	def generate_file(self):
		pass

	def pdflatex(self):
		pass

def usage():
	pass

# arguments: year, weekstart, birthday file
if __name__ == "__main__":
	import sys
	if len(sys.argv) < 2:
		usage()

	pc = LatexCalendar(sys.argv)
	pc.generate_file()
	pc.pdflatex()

