FROM python:3.13.5-slim
COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /bin/uv

# 设置时区
ENV TZ=Asia/Shanghai

WORKDIR /app

# Django
ENV APP_MODULE=home.asgi:application
ENV PRODUCTION_SERVER=true

# Gunicorn 配置
COPY ./docker/gunicorn_conf.py /gunicorn_conf.py
COPY ./docker/start.sh /start.sh
RUN chmod +x /start.sh

# 安装依赖
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen --compile-bytecode

# 复制网站
COPY manage.py prestart.sh /app/
COPY home /app/home/

CMD ["uv", "run", "--no-dev", "/start.sh"]
