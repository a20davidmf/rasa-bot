FROM python:3.8.10 as BASE

RUN apt-get update \
    && apt-get --assume-yes --no-install-recommends install \
    build-essential \
    curl \
    git \
    jq \
    libgomp1 \
    vim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

RUN pip install rasa==2.8.1

RUN pip install protobuf==3.20

ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD config.yml config.yml
ADD domain.yml domain.yml
ADD credentials.yml credentials.yml
ADD endpoints.yml endpoints.yml