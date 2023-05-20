build: 
	docker build -t c2ng:latest .

generate:
	PYTHONPATH=${PYTHONPATH}:`pwd`/service/ python tools/gen_openapi.py

keys:
	PYTHONPATH=${PYTHONPATH}:`pwd`/service/ python tools/crypto_keys.py

darglint:
	darglint service/*.py service/handlers/*.py tools/*.py
