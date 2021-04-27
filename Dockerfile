
### BASE CONTAINER #######################################################

FROM python:3.6-slim-buster

### PACKAGE MANAGER ######################################################

RUN apt-get clean && apt-get update && apt-get install -y locales
RUN locale-gen fr_FR.UTF-8

RUN apt-get update && apt-get install -yq \
wget \
unzip \
cron \
chromium \
chromium-driver

### PYTHON REQUIREMENTS ###################################################

ADD requirements.txt requirements.txt
RUN pip install -r "requirements.txt"

### PYTHON SCRIPT #########################################################

WORKDIR /opt/

ADD scraper scraper

ENTRYPOINT /usr/local/bin/python3