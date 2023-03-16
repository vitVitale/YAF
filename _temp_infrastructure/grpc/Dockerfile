FROM python:3.10.7 as base
MAINTAINER Vitaly Vasilyuk
USER root

RUN mkdir -m 777 app

COPY requirements.txt /app/

RUN pip install --upgrade pip \
    && pip install --no-cache-dir cython \
    && pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app
CMD [ "python", "/app/server.py" ]