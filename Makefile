build: 
	docker build -t c2ng:latest .

generate:
	PYTHONPATH=${PYTHONPATH}:`pwd`/service/ python gen_openapi.py -f test.yaml
