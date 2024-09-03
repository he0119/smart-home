FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.4.3 /uv /bin/uv

# 设置时区
ENV TZ=Asia/Shanghai

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

# Gunicon 配置
COPY ./docker/gunicorn_conf.py /gunicorn_conf.py
COPY ./docker/start.sh /start.sh
RUN chmod +x /start.sh

# 安装依赖
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --compile-bytecode

# 复制网站
COPY . .

CMD ["uv", "run", "/start.sh"]
