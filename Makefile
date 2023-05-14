build: 
	docker build -t c2ng:latest .

generate:
	PYTHONPATH=${PYTHONPATH}:`pwd`/service/ python gen_openapi.py -f docs/c2ng.yaml

keys:
	PYTHONPATH=${PYTHONPATH}:`pwd`/service/ python tools/configure.py
