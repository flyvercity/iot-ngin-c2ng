FROM python:3.10

EXPOSE 9091

RUN mkdir -p /app
WORKDIR /app

RUN apt-get update -y && apt-get install -y iputils-ping 
COPY docker/uss_sim/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY c2ng/uss_sim ./c2ng/uss_sim

ENV PYTHONPATH=/app

ENTRYPOINT ["python3", "c2ng/uss_sim/uss_sim.py"]
