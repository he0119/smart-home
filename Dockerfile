FROM python:3.9 as requirements-stage

WORKDIR /tmp

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN curl -sSL https://install.python-poetry.org -o install-poetry.py

RUN python install-poetry.py --yes

ENV PATH="${PATH}:/root/.local/bin"

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.9-slim-bullseye

WORKDIR /app

# 设置时区
ENV TZ=Asia/Shanghai

RUN apt-get update \
  && apt-get -y upgrade \
  && apt-get install -y --no-install-recommends uwsgi-plugin-python3 \
  && apt-get purge -y --auto-remove \
  && rm -rf /var/lib/apt/lists/*

# 安装依赖
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN rm requirements.txt

# 复制网站
COPY . .

# UWSGI
ENV UWSGI_WSGI_FILE=home/wsgi.py
ENV UWSGI_SOCKET=[::]:8000 UWSGI_MASTER=1 UWSGI_PROCESSES=2 UWSGI_ENABLE_THREADS=1 UWSGI_LIMIT_POST=52428800

CMD [ "uwsgi", "--show-config" ]
