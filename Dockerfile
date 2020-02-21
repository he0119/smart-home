FROM python:3.8-alpine

WORKDIR /usr/src/app

# 安装依赖
RUN apk add --no-cache --virtual .build-deps gcc musl-dev
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apk del .build-deps

# 复制网站
COPY . .

# UWSGI
ENV UWSGI_WSGI_FILE=home/wsgi.py
ENV UWSGI_HTTP=:8000 UWSGI_MASTER=1

CMD [ "uwsgi", "--show-config" ]
