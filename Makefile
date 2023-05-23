src := $(wildcard service/*.py service/handlers/*.py tools/*py)

build: 
	docker build -t c2ng:latest .

generate:
	PYTHONPATH=${PYTHONPATH}:`pwd`/service/ python tools/gen_openapi.py

keys:
	PYTHONPATH=${PYTHONPATH}:`pwd`/service/ python tools/crypto_keys.py

# Documentation

darglint: $(src)
	darglint service/*.py service/handlers/*.py tools/*.py

.autogen: $(src)
	PYTHONPATH=${PYTHONPATH}:`pwd`/service:`pwd`/tools lazydocs \
		--src-base-url=https://github.com/flyvercity/iot-ngin-c2ng/blob/main/ \
		--output-path ./docbuild \
		--no-watermark \
		service \
		tools
	touch .autogen

docbuild/title.pdf: docs/title.tex
	pdflatex -output-directory=docbuild docs/title.tex

markdowns := $(wildcard docs/*.md)
images := $(wildcard docs/*.png)
revision := $(shell git describe --always)
deliverable := docbuild/release/D2.C2NG.$(revision).pdf

docbuild/body.pdf: .autogen $(markdowns) $(images)
	echo "_Revision $(revision)_" > docbuild/release.md
	(cd docs; pandoc -s \
		-V papersize:a4 -V geometry:margin=1in \
		-F mermaid-filter --toc -o ../docbuild/body.pdf \
		GLOSSARY.md \
		GENERAL.md \
		START.md \
		ADMINISTRATION.md \
		REFERENCE.md \
		../docbuild/app.md \
		../docbuild/release.md \
	)

$(deliverable): docbuild/title.pdf docbuild/body.pdf
	mkdir -p docbuild/release
	python -m fitz join -o $(deliverable) \
						   docbuild/title.pdf \
						   docbuild/body.pdf

docs: $(deliverable)
