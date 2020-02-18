FROM python:3.8-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -i https://mirrors.cloud.tencent.com/pypi/simple -r requirements.txt
COPY . /code/
