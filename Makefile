default: tbontb.svgz stats.txt

tbontb.dot: graph.py
	./graph.py

tbontb.svgz: tbontb.dot
	dot -Tsvgz $< -o $@

stats.txt: graph.py analysis.py
	./analysis.py > $@

svg: tbontb.svg

tbontb.svg: tbontb.dot
	dot -Tsvg $< -o $@

extract: tbontb.epub
	rm -rf tbontb
	unzip -d tbontb tbontb.epub

clean:
	rm -f tbontb.dot tbontb.svgz tbontb.svg
