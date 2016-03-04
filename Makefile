default: tbontb.svgz

tbontb.dot: graph.py
	./graph.py

tbontb.svgz: tbontb.dot
	dot -Tsvgz $< -o $@

svg: tbontb.svg


tbontb.svg: tbontb.dot
	dot -Tsvg $< -o $@

extract: tbontb.epub
	rm -rf tbontb
	unzip -d tbontb tbontb.epub

clean:
	rm -f tbontb.dot tbontb.svgz
