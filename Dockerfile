ARG python
FROM python:${python}-slim-bullseye as base
MAINTAINER Vitalii Vasiliuk
USER root

# Install Docker CLI & java jre for Allure command line tool ...
COPY --from=docker:dind /usr/local/bin/docker /usr/local/bin/docker
COPY --from=openjdk:8-jre-slim /usr/local/openjdk-8 /usr/local/openjdk-8
ENV JAVA_HOME /usr/local/openjdk-8
RUN update-alternatives --install /usr/bin/java java /usr/local/openjdk-8/bin/java 1

# Placement of auxiliary tools ...
RUN mkdir -m 777 app
COPY _base/allure-2.13.9 /app/allure-2.13.9
COPY _base/migrations_tools /app/migrations_tools

RUN apt update \
    && apt -y install build-essential \
    && apt-get -y install manpages-dev \
    && apt-get -y install docker-compose \
    && chmod -R 777 /app/migrations_tools \
    && mkdir -m 777 app/test_model \
    && chmod +x /app/run.sh

CMD [ "python", "-V" ]


#########################  ARM64 & AMD64  ############################
FROM base as yaf_runner

# Build YAF core ...
COPY yaf /app/yaf
COPY requirements.txt /app/
COPY run.sh /app/

RUN pip install --upgrade pip \
    && pip install --no-cache-dir cython==0.29.36 \
    && pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app
ENTRYPOINT ["/app/run.sh"]