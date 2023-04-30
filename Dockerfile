FROM python:3.10

EXPOSE 9090

RUN mkdir -p /c2ng/service
WORKDIR /c2ng/service

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY service .

ENTRYPOINT ["python3", "app.py"]
