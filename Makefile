# Environment

src := $(wildcard \
	core/service/*.py \
	core/service/handlers/*.py \
	tools/*.py \
	uss-sim/src/*.py \
)

deps-check:
	which git
	which python3
	which docker
	which docker-compose

deps-check-docs:
	which darglint
	which pdflatex
	which lazydocs
	which pandoc

# Core and simulators

build-core: 
	docker build -t c2ng:latest -f docker/core/Dockerfile .

build-uss-sim:
	docker build -t c2ng-uss-sim:latest -f docker/uss_sim/Dockerfile .

build-uas-sim:
	docker build -t c2ng-uas-sim:latest -f docker/uas_sim/Dockerfile .

build: deps-check build-core build-uss-sim build-uas-sim

docker/core/config/c2ng/private.pem:
	./cli.sh cryptokeys

prerun: docker/core/config/c2ng/private.pem

up: build prerun
	./scripts/ctrl-core.sh up -d
	./scripts/ctrl-sims.sh create

start: up
	./cli.sh keycloak

# Tests

build-unit-tests:
	docker build -t c2ng-unit-tests:latest -f test/docker/Dockerfile .

test: build-unit-tests
	./scripts/test-unit.sh

# API specification

docbuild:
	mkdir -p docbuild

generate: docbuild
	./cli.sh genapi

# Documentation

darglint: $(src)
	darglint -s google -z full $(src)

.autogen: docbuild $(src)
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
deliverable := docbuild/release/D2.C2NG.pdf

docbuild/openapi.md: docs/c2ng.yaml
	echo "# V. API Reference\n\n" > docbuild/openapi.md
	echo "\`\`\`yaml\n" >> docbuild/openapi.md
	cat docs/c2ng.yaml >> docbuild/openapi.md
	echo "\`\`\`\n" >> docbuild/openapi.md

docbuild/body.pdf: .autogen $(markdowns) $(images) docbuild/openapi.md
	echo "# Document Version Control" > docbuild/release.md
	echo "_This revision $(revision)_" >> docbuild/release.md
	(cd docs; pandoc -s \
		-V papersize:a4 -V geometry:margin=1in \
		-F mermaid-filter  \
		--toc -o ../docbuild/body.pdf \
		GLOSSARY.md \
		GENERAL.md \
		START.md \
		ADMINISTRATION.md \
		EXPERIMENTS.md \
		REFERENCE.md \
		../docbuild/app.md \
		../docbuild/secman.md \
		../docbuild/uss.md \
		../docbuild/sliceman.md \
		../docbuild/mongo.md \
		../docbuild/c2ng.md \
		../docbuild/crypto_keys.md \
		../docbuild/gen_openapi.md \
		../docbuild/oath_admin.md \
		../docbuild/openapi.md \
		VERIFICATION.md \
		../docbuild/release.md \
	)

$(deliverable): docbuild/title.pdf docbuild/body.pdf
	mkdir -p docbuild/release
	python -m fitz join -o $(deliverable) \
						   docbuild/title.pdf \
						   docbuild/body.pdf

docs: deps-check-docs $(deliverable)
