FROM vitvitale/yaf_base_x86:3.10.7_001 as base
MAINTAINER Vitaly Vasilyuk
USER root

# Copy YAF sources ...
COPY yaf /app/yaffat
COPY requirements.txt /app/
COPY run.sh /app/

RUN pip install --no-cache-dir -r /app/requirements.txt
RUN chmod +x /app/run.sh

WORKDIR /app
ENTRYPOINT ["/app/run.sh"]