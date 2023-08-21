# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

FROM python:3.10

RUN mkdir -p /test
WORKDIR /test

RUN apt-get update -y && apt-get install -y iputils-ping 

COPY test/docker/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY c2ng ./c2ng
COPY test/unit ./unit
COPY docker/core/config/did ./did
COPY integration/ppssi/py-verifier/IAA/jwt_pep.py ./unit
COPY integration/ppssi/py-verifier/IAA/resolver.py ./unit

ENV PYTHONPATH "${PYTHONPATH}:/test"

ENTRYPOINT ["pytest", "-v", "unit"]
