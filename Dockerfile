FROM python:3.8-alpine

WORKDIR /usr/src/app

# 设置时区
RUN apk add --no-cache tzdata
ENV TZ=Asia/Shanghai

# 安装依赖
COPY poetry.lock pyproject.toml ./
RUN set -ex; \
  apk add --no-cache postgresql-libs; \
	apk add --no-cache --virtual .build-deps \
		gcc \
		libc-dev \
		linux-headers \
    postgresql-dev \
    curl \
	; \
	curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python; \
  $HOME/.poetry/bin/poetry config virtualenvs.create false; \
  $HOME/.poetry/bin/poetry install --no-dev; \
  rm -rf $HOME/.poetry; \
  pip install uwsgi; \
	apk del .build-deps;

# 复制网站
COPY . .

# UWSGI
ENV UWSGI_WSGI_FILE=home/wsgi.py
ENV UWSGI_SOCKET=:8000 UWSGI_HTTP=:8001 UWSGI_MASTER=1 UWSGI_PROCESSES=2 UWSGI_ENABLE_THREADS=1 UWSGI_UID=500 UWSGI_GID=500

CMD [ "uwsgi", "--show-config" ]
