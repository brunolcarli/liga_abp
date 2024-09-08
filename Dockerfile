# FROM ubuntu:23.04
# # FROM 3.11-bullseye

# RUN apt-get update && \
#     apt-get install --no-install-recommends -y gcc && \
#     apt-get clean && rm -rf /var/lib/apt/lists/* \
#     apt-get install make \
#     apt-get install wget \
#     apt-get install tar




FROM debian:bullseye

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get -y install build-essential \
        zlib1g-dev \
        libncurses5-dev \
        libgdbm-dev \ 
        libnss3-dev \
        libssl-dev \
        libreadline-dev \
        libffi-dev \
        libsqlite3-dev \
        libbz2-dev \
        wget \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get purge -y imagemagick imagemagick-6-common 

RUN cd /usr/src \
    && wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz \
    && tar -xzf Python-3.11.0.tgz \
    && cd Python-3.11.0 \
    && ./configure --enable-optimizations \
    && make altinstall

RUN update-alternatives --install /usr/bin/python python /usr/local/bin/python3.11 1

RUN apt-get update && apt-get install -y python3-pip

RUN mkdir /app
WORKDIR /app

COPY config/requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV NAME liga_abp
