default: tbontb.svg stats.txt

all: tbontb.svg stats.txt

tbontb.dot: graph.py
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
