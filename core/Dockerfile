FROM python:3.10

EXPOSE 9090

RUN mkdir -p /app
WORKDIR /app

RUN apt-get update -y && apt-get install -y iputils-ping 
COPY core/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY c2ng/service ./c2ng/service
COPY c2ng/common ./c2ng/common
COPY core/config ./config

ENV PYTHONPATH=/app

ENTRYPOINT ["python3", "c2ng/service/app.py"]
