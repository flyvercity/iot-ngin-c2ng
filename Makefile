build: 
	docker build -t c2ng:latest .

generate:
	PYTHONPATH=${PYTHONPATH}:`pwd`/service/ python tools/gen_openapi.py

keys:
	PYTHONPATH=${PYTHONPATH}:`pwd`/service/ python tools/crypto_keys.py

darglint:
	darglint service/*.py service/handlers/*.py tools/*.py

# Documentation

docbuild/title.pdf: docs/title.tex
	pdflatex -output-directory=docbuild docs/title.tex

docbuild/body.pdf: docs/README.md docs/DATABASE.md
	(cd docs; pandoc --toc README.md DATABASE.md -o ../docbuild/body.pdf)

D2.C2NG.pdf: docbuild/title.pdf docbuild/body.pdf
	python -m fitz join -o D2.C2NG.pdf \
						   docbuild/title.pdf \
						   docbuild/body.pdf

docs: D2.C2NG.pdf
