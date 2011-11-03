all: compile

pre: 
ifdef YEAR
	@true
else
	@false
endif

create: pre
	sed "s/%year%/$(YEAR)/" head.tex.in > head.tex
	./make-calendar.pl $(YEAR) > cal$(YEAR).tex

compile: pre cal$(YEAR).tex
	pdflatex cal$(YEAR).tex >/dev/null 2>&1

cal$(YEAR).tex: create
