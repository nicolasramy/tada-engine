FROM python:3-alpine

RUN mkdir /app
WORKDIR /app

VOLUME /app

ADD . /app

# Extra repositories
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories \
    && echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories

RUN apk update && apk upgrade

RUN apk add -f build-base python3-dev leveldb-dev czmq-dev

RUN python setup.py install
