FROM python:3.11 as requirements-stage

WORKDIR /tmp

RUN curl -sSL https://install.python-poetry.org | python -

ENV PATH="${PATH}:/root/.local/bin"

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-slim

# 设置时区
ENV TZ=Asia/Shanghai

# Gunicon 配置
COPY ./docker/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./docker/gunicorn_conf.py /gunicorn_conf.py

# 安装 uvicorn, gunicorn
# https://www.uvicorn.org/#quickstart
RUN apt-get update \
  && apt-get install -y --no-install-recommends gcc \
  && pip install --no-cache-dir --upgrade "uvicorn[standard]" gunicorn \
  && apt-get purge -y --auto-remove \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Django
ENV APP_MODULE home.asgi:application

# 安装依赖
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN rm requirements.txt

# 复制网站
COPY . .

CMD ["/start.sh"]
