FROM python:3-alpine

RUN adduser -D clickonly

WORKDIR /home/clickonly

RUN apk update && \
    apk add --virtual build-deps gcc python3-dev musl-dev && \
    apk add postgresql-dev && \
    pip3 install psycopg2 && \
    apk del build-deps

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN chown -R clickonly:clickonly ./
USER clickonly

EXPOSE 5000
