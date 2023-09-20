LATEX = latex

DVIPS = dvips

PDFFLAGS = -dCompatibilityLevel=1.4 -dPDFSETTINGS=/prepress \
           -dCompressPages=true -dUseFlateCompression=true  \
           -dEmbedAllFonts=true -dSubsetFonts=true -dMaxSubsetPct=100

%.dvi: %.tex
	$(LATEX) $<

%.ps: %.dvi
	$(DVIPS) -o $@ $<

%.pdf: %.ps
	ps2pdf $(PDFFLAGS) $<

all:	top.tex
	latex top
	makeindex top
	latex top
	dvips -T 6.75in,9.25in -Ppdf -o thinkCSpy.ps top
#	dvips -T 7.444in,9.681in -Ppdf -o thinkCSpy.ps top
	ps2pdf $(PDFFLAGS) thinkCSpy.ps

DEST = /home/downey/public_html/greent/thinkpython/thinkCSpy

distrib:
	rm -rf dist
	mkdir dist dist/tex dist/html
	rsync -a thinkCSpy.pdf thinkCSpy.ps dist
	rsync -a Makefile *.tex dist/tex
	rsync -a illustrations dist/tex
	rm dist/tex/illustrations/*.bak
	rsync -a images dist/html
	mkdir dist/html/illustrations
	rsync -a illustrations/*.png dist/html/illustrations
	cd dist/tex; make clean
	cd dist; tar -czf thinkCSpy.tex.tar.gz tex
	cd ltoh; perl make_book_html.pl ../dist/tex ../dist/html
	cd dist; tar -czf thinkCSpy.html.tar.gz html
	cd dist; cp thinkCSpy.tex.tar.gz thinkCSpy.tex.tgz
	cd dist; cp thinkCSpy.html.tar.gz thinkCSpy.html.tgz
	rsync -a dist/* $(DEST)
	chmod -R o+r $(DEST)/*

clean:
	rm -f *~ *.aux *.log *.dvi *.idx *.ilg *.ind *.toc


prop:
	zip downey_software_design.zip proposal/proposal.pdf proposal/table_of_contents.pdf proposal/chapters12-14.pdf


