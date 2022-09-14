FROM python:3.10 as requirements-stage

WORKDIR /tmp

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN curl -sSL https://install.python-poetry.org -o install-poetry.py

RUN python install-poetry.py --yes

ENV PATH="${PATH}:/root/.local/bin"

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10-slim

WORKDIR /app

# 设置时区
ENV TZ=Asia/Shanghai

# 安装依赖
# https://www.uvicorn.org/#quickstart
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt
RUN apt-get update \
  && apt-get -y upgrade \
  && apt-get install -y --no-install-recommends build-essential \
  && pip install --no-cache-dir --upgrade "uvicorn[standard]" gunicorn \
  && pip install --no-cache-dir --upgrade -r requirements.txt \
  && apt-get purge -y --auto-remove \
  && rm -rf /var/lib/apt/lists/*
RUN rm requirements.txt

# 复制网站
COPY . .

CMD ["gunicorn", "home.asgi:application", "-k", "uvicorn.workers.UvicornWorker""]
