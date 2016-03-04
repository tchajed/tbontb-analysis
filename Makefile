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

extract: tbontb.epub
	rm -rf tbontb
	unzip -d tbontb tbontb.epub

clean:
	rm -f tbontb.dot tbontb.svgz tbontb.svg
