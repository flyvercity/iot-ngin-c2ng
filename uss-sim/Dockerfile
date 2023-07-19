FROM python:3.10

EXPOSE 9090

RUN mkdir -p /c2ng/uss-sim
WORKDIR /c2ng/uss-sim

RUN apt-get update -y && apt-get install -y iputils-ping 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src .

ENTRYPOINT ["python3", "uss_sim.py"]
