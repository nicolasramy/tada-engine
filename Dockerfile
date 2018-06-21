FROM python:3-alpine

RUN mkdir /app
WORKDIR /app

VOLUME /app

ADD . /app

RUN apk update && apk upgrade
RUN apk add -f alpine-sdk python3-dev libzmq

RUN python setup.py install

RUN apk del -r -f alpine-sdk python3-dev
