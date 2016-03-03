default: tbontb.svgz

tbontb.dot: graph.py
	./graph.py

tbontb.svgz: tbontb.dot
	dot -Tsvgz $< -o $@

clean:
	rm -f tbontb.dot tbontb.svgz
