FROM python:3.8-alpine

WORKDIR /usr/src/app

# 安装依赖
COPY requirements.txt ./
RUN set -e; \
	apk add --no-cache --virtual .build-deps \
		gcc \
		libc-dev \
		linux-headers \
	; \
	pip install -r requirements.txt; \
	apk del .build-deps;

# 复制网站
COPY . .

# UWSGI
ENV UWSGI_WSGI_FILE=home/wsgi.py
ENV UWSGI_SOCKET=:8000 UWSGI_MASTER=1

CMD [ "uwsgi", "--show-config" ]
