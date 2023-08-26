# Environment

src := $(wildcard \
	c2ng/common/*.py \
	c2ng/service/*.py \
	c2ng/service/handlers/*.py \
	c2ng/service/backend/*.py \
	c2ng/service/backend/net_providers/*.py \
	c2ng/service/gui/*.py \
	c2ng/service/did/*.py \
	c2ng/uss-sim/src/*.py \
	c2ng/uas-sim/src/*.py \
	c2ng/tools/*.py \
)

deps-check:
	which python3
	which pip3
	pip3 --require-virtualenv install -r requirements.dev.txt -q
	which git
	which docker
	which docker-compose

deps-check-docs:
	which darglint
	which pdflatex
	which lazydocs
	which pandoc

# Core and simulators

build-core: 
	docker build ${C2NG_DOCKER_BUILD_ARGS} -t c2ng:latest -f docker/core/Dockerfile .

build-uss-sim:
	docker build ${C2NG_DOCKER_BUILD_ARGS} -t c2ng-uss-sim:latest -f docker/uss_sim/Dockerfile .

build-uas-sim:
	docker build ${C2NG_DOCKER_BUILD_ARGS} -t c2ng-uas-sim:latest -f docker/uas_sim/Dockerfile .

build: deps-check build-core build-uss-sim build-uas-sim

docker/core/config/c2ng/private.pem:
	./cli.sh cryptokeys

prerun: docker/core/config/c2ng/private.pem

# Decentralized Identities Support

did_files := $(addprefix docker/core/config/did/, \
	issuer.pem \
	issuer.did \
	sim-drone-id.pem \
	sim-drone-id.did \
	sim-drone-id.jwt \
)

$(did_files):
	./scripts/did-init.sh

did: $(did_files)

# Integrated start

up: build prerun did
	./scripts/ctrl-core.sh up -d
	./scripts/ctrl-sims.sh stop
	./scripts/ctrl-sims.sh create

start: up
	./cli.sh keycloak

# Tests

build-unit-tests:
	docker build ${C2MG_DOCKER_BUILD_ARGS} -t c2ng-unit-tests:latest -f test/docker/Dockerfile .

test: build-unit-tests
	./scripts/test-unit.sh

# API specification

docbuild:
	mkdir -p docbuild

generate: docbuild
	./cli.sh genapi

# Documentation

markdowns := $(wildcard docs/*.md)
images := $(wildcard docs/*.png)
revision := $(shell git describe --always)
gen_markdowns := $(addprefix docbuild/gen/, $(addsuffix .md, $(notdir $(src))))
deliverable := docbuild/release/D2.C2NG.Final.pdf

darglint: $(src)
	darglint -s google -z full $(src)

$(gen_markdowns) &: darglint $(src)
	PYTHONPATH=${PYTHONPATH}:`pwd`/service:`pwd`/tools lazydocs \
		--src-base-url=https://github.com/flyvercity/iot-ngin-c2ng/blob/main/ \
		--output-path ./docbuild/gen \
		--no-watermark \
		$(src)

docbuild/title.pdf: docs/title.tex
	pdflatex -output-directory=docbuild docs/title.tex

docbuild/openapi.md: docs/c2ng.yaml
	echo "# V. API Reference\n\n" > docbuild/openapi.md
	echo "\`\`\`yaml\n" >> docbuild/openapi.md
	cat docs/c2ng.yaml >> docbuild/openapi.md
	echo "\`\`\`\n" >> docbuild/openapi.md

docbuild/body.pdf: $(markdowns) $(gen_markdowns) $(images) docbuild/openapi.md
	echo "# Document Version Control" > docs/release.md
	echo "_This revision $(revision)_" >> docs/release.md
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
		VERIFICATION.md \
		$(addprefix ../, $(gen_markdowns)) \
		release.md \
	)

$(deliverable): docbuild/title.pdf docbuild/body.pdf
	mkdir -p docbuild/release
	python -m fitz join -o $(deliverable) \
		docbuild/title.pdf \
		docbuild/body.pdf

docs: deps-check-docs $(deliverable)
