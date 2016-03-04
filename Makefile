default: tbontb.svg tbontb.json stats.txt


all: tbontb.json tbontb.svg stats.txt


tbontb.dot tbontb.json: graph.py
	./graph.py

tbontb.svgz: tbontb.dot
	dot -Tsvgz $< -o $@

tbontb.svg: tbontb.dot
	dot -Tsvg $< -o $@

stats.txt: graph.py analysis.py
	./analysis.py > $@


package: resources.tar.gz


resources.tar.gz: tbontb.json tbontb.svg
	sh package.sh

extract: tbontb.epub
	rm -rf tbontb
	unzip -d tbontb tbontb.epub

clean:
	rm -f tbontb.dot tbontb.svgz tbontb.svg

.PHONY: default all package extract clean
