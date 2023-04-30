FROM python:3.10

EXPOSE 9090

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app .

ENTRYPOINT ["python3", "c2ng_service.py"]
