build: 
	docker build -t c2ng:latest .

generate:
	python gen_openapi.py -f protocols/test.json
