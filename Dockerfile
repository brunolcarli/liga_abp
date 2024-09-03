FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install --no-install-recommends -y gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/* \
    apt-get install make

RUN apt-get update && apt-get install -y python3-pip

RUN mkdir /app
WORKDIR /app

COPY config/requirements/requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV NAME liga_abp
