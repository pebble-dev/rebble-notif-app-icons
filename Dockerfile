FROM python:3.6-alpine
RUN apk add --update build-base
RUN apk add --update zlib-dev libjpeg-turbo-dev
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD flask run -h $HOST
