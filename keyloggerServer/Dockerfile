FROM python:2.7

RUN apt-get update \
	&& apt-get install -y haproxy nano net-tools iputils-ping procps netcat  \
	&& rm -rf /var/lib/apt/lists/*

COPY haproxy /tmp/haproxy

RUN mkdir -p /app
WORKDIR /app
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src .

EXPOSE 80
ENTRYPOINT ["python", "keylogger_server.py"]
