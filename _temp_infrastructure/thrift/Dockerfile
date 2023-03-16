FROM python:3.10.7 as base
MAINTAINER Vitaly Vasilyuk
USER root

RUN mkdir -m 777 app && \
    pip install --upgrade pip && \
    pip install --no-cache-dir cython thriftpy2

WORKDIR /app
CMD [ "python", "/app/server.py" ]