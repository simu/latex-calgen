all: compile

pre: 
ifdef YEAR
	@true
else
	@false
endif

create: pre
	./make-calendar.pl $(YEAR) $(WEEK_START) > cal$(YEAR).tex

compile: pre cal$(YEAR).tex
	pdflatex cal$(YEAR).tex >/dev/null 2>&1

cal$(YEAR).tex: create
