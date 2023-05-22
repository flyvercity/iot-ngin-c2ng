build: 
	docker build -t c2ng:latest .

generate:
	PYTHONPATH=${PYTHONPATH}:`pwd`/service/ python tools/gen_openapi.py

keys:
	PYTHONPATH=${PYTHONPATH}:`pwd`/service/ python tools/crypto_keys.py

darglint:
	darglint service/*.py service/handlers/*.py tools/*.py


# Documentation
src := $(wildcard service/*.py service/handlers/*.py tools/*py)

autogen: src
	PYTHONPATH=${PYTHONPATH}:`pwd`/service:`pwd`/tools lazydocs \
		--src-base-url=https://github.com/flyvercity/iot-ngin-c2ng/blob/main/ \
		--output-path ./docbuild \
		service \
		tools

docbuild/title.pdf: docs/title.tex
	pdflatex -output-directory=docbuild docs/title.tex

markdowns := $(wildcard docs/*.md)
images := $(wildcard docs/*.png)
gen_markdowns := $(wildcard docbuild/*.md)

docbuild/body.pdf: $(markdowns) $(gen_markdowns) $(images)
	(cd docs; pandoc -s -V papersize:a4 --toc -o ../docbuild/body.pdf \
		README.md \
		DATABASE.md \
		../docbuild/app.md \
	)

D2.C2NG.pdf: docbuild/title.pdf docbuild/body.pdf
	python -m fitz join -o D2.C2NG.pdf \
						   docbuild/title.pdf \
						   docbuild/body.pdf

docs: D2.C2NG.pdf
