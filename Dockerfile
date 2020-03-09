FROM python:3.8-alpine

WORKDIR /usr/src/app

# 安装依赖
COPY requirements.txt ./
RUN apk add --no-cache postgresql-dev
RUN set -e; \
	apk add --no-cache --virtual .build-deps \
		gcc \
		libc-dev \
		linux-headers \
	; \
	pip install --no-cache-dir -r requirements.txt; \
	apk del .build-deps;

# 复制网站
COPY . .

# UWSGI
ENV UWSGI_WSGI_FILE=home/wsgi.py
ENV UWSGI_SOCKET=:8000 UWSGI_MASTER=1 UWSGI_PROCESSES=2 UWSGI_ENABLE_THREADS=1 UWSGI_UID=500 UWSGI_GID=500

CMD [ "uwsgi", "--show-config" ]
