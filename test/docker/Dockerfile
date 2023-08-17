# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

FROM python:3.10

RUN mkdir -p /test
WORKDIR /test

RUN apt-get update -y && apt-get install -y iputils-ping 

COPY test/docker/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY test/unit ./unit

ENTRYPOINT ["pytest", "-v", "unit"]
