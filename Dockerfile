FROM python:3.11.3-alpine3.18

### install packages
RUN apk update && \
    apk add curl bash && \
    apk add --virtual build-deps gcc musl-dev && \
    rm -rf /var/cache/apk/*

### Install Python dependencies
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

COPY . /app/

RUN addgroup inspector && adduser -SG inspector inspector
RUN chown -R inspector:inspector /app
RUN chown -R inspector:inspector /usr/local/lib/python3.11/site-packages

USER inspector
