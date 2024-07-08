FROM python:3.12-slim

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
COPY requirements.lock ./
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -r requirements.lock

# 复制网站
COPY . .

CMD ["/start.sh"]
