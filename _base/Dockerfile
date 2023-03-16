FROM python:3.10.7-slim-bullseye as base
MAINTAINER Vitaly Vasilyuk
USER root

# Install Docker CLI & java jre for Allure command line tool ...
COPY --from=docker:dind /usr/local/bin/docker /usr/local/bin/docker
COPY --from=openjdk:8-jre-slim /usr/local/openjdk-8 /usr/local/openjdk-8
ENV JAVA_HOME /usr/local/openjdk-8
RUN update-alternatives --install /usr/bin/java java /usr/local/openjdk-8/bin/java 1

# Build YAFFAT core ...
RUN mkdir -m 777 app

COPY base_req.txt /app/base_req.txt
COPY allure-2.13.9 /app/allure-2.13.9
COPY migrations_tools /app/migrations_tools

RUN apt update \
    && apt -y install build-essential \
    && apt-get -y install manpages-dev \
    && pip install --upgrade pip \
    && pip install --no-cache-dir cython docker-compose \
    && pip install --no-cache-dir -r /app/base_req.txt \
    && chmod -R 777 /app/migrations_tools \
    && mkdir -m 777 app/test_model

CMD [ "python", "-V" ]