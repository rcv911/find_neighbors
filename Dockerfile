FROM python:3.7-alpine

RUN apk update && apk add --virtual build-deps \
    autoconf \
    automake \
    g++ \
    make \
    build-deps \
    gcc \
    python3-dev \
    musl-dev \
    gfortran \
    py-pip build-base wget freetype-dev libpng-dev openblas-dev

RUN pip install --no-cache-dir \
    pytoml \
    aiohttp \
    aiohttp-rest-api \
    numpy \
    scipy \
    namegenerator

COPY . /app

VOLUME ["/config/config.toml"]

WORKDIR /app

ENTRYPOINT ["python", "api.py", "-c", "/config/config.toml"]
