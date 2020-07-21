FROM python:3.8-alpine

WORKDIR /usr/src/app

# 安装依赖
COPY poetry.lock pyproject.toml ./
RUN apk add --no-cache postgresql-dev
RUN set -e; \
	apk add --no-cache --virtual .build-deps \
		gcc \
		libc-dev \
		linux-headers \
    curl \
    tzdata \
	; \
  cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime; \
  echo "Asia/Shanghai" >  /etc/timezone; \
	curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python; \
  $HOME/.poetry/bin/poetry config virtualenvs.create false && \
  $HOME/.poetry/bin/poetry install --no-dev; \
  pip install uwsgi; \
	apk del .build-deps;

# 复制网站
COPY . .

# UWSGI
ENV UWSGI_WSGI_FILE=home/wsgi.py
ENV UWSGI_SOCKET=:8000 UWSGI_HTTP=:8001 UWSGI_MASTER=1 UWSGI_PROCESSES=2 UWSGI_ENABLE_THREADS=1 UWSGI_UID=500 UWSGI_GID=500

CMD [ "uwsgi", "--show-config" ]
