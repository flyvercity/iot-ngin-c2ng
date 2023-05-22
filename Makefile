src := $(wildcard service/*.py service/handlers/*.py tools/*py)

build: 
	docker build -t c2ng:latest .

generate:
	PYTHONPATH=${PYTHONPATH}:`pwd`/service/ python tools/gen_openapi.py

keys:
	PYTHONPATH=${PYTHONPATH}:`pwd`/service/ python tools/crypto_keys.py

darglint: $(src)
	darglint service/*.py service/handlers/*.py tools/*.py


# Documentation

autogen: $(src)
	PYTHONPATH=${PYTHONPATH}:`pwd`/service:`pwd`/tools lazydocs \
		--src-base-url=https://github.com/flyvercity/iot-ngin-c2ng/blob/main/ \
		--output-path ./docbuild \
		service \
		tools

docbuild/title.pdf: docs/title.tex
	pdflatex -output-directory=docbuild docs/title.tex

markdowns := $(wildcard docs/*.md)
images := $(wildcard docs/*.png)

docbuild/body.pdf: autogen $(markdowns) $(images)
	(cd docs; pandoc -s -V papersize:a4 \
		-F mermaid-filter --toc -o ../docbuild/body.pdf \
		GLOSSARY.md \
		GENERAL.md \
		ADMINISTRATION.md \
		../docbuild/app.md \
	)

docbuild/release/D2.C2NG.pdf: docbuild/title.pdf docbuild/body.pdf
	mkdir -p docbuild/release
	python -m fitz join -o docbuild/release/D2.C2NG.pdf \
						   docbuild/title.pdf \
						   docbuild/body.pdf

docs: docbuild/release/D2.C2NG.pdf
