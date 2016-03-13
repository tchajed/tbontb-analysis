default: tbontb.svg tbontb.json stats.yaml


all: tbontb.svg tbontb.json stats.yaml package


tbontb.dot tbontb.json: tbontb/ graph.py
	./graph.py

tbontb.svgz: tbontb.dot
	dot -Tsvgz $< -o $@

tbontb.svg: tbontb.dot
	dot -Tsvg $< -o $@

stats.yaml: tbontb/ graph.py analysis.py
	./analysis.py > $@

package: resources.tar.gz


resources.tar.gz: tbontb tbontb.json tbontb.svg
	sh package.sh

tbontb/: tbontb.epub
	unzip -d tbontb tbontb.epub

clean:
	rm -f tbontb.dot tbontb.svgz tbontb.svg stats.yaml
	rm -rf tbontb

.PHONY: default all package clean
