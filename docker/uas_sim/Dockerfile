# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

FROM python:3.10

EXPOSE 9092/udp
EXPOSE 9093/udp

RUN mkdir -p /app
WORKDIR /app

RUN apt-get update -y && apt-get install -y iputils-ping 

COPY docker/uas_sim/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY c2ng/common ./c2ng/common
COPY c2ng/uas_sim ./c2ng/uas_sim
COPY integration/ppssi/py-verifier/IAA/jwt_pep.py .
COPY integration/ppssi/py-verifier/IAA/resolver.py .

ENV PYTHONPATH=/app

ENTRYPOINT ["python3", "c2ng/uas_sim/uas_sim.py"]
