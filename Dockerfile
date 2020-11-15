
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

### CRON JOB ##############################################################

RUN echo '*/10 * * * * cd /opt && python3 -m scraper.main > /var/log/cron.log 2>&1' >> /etc/cron.d/hello-cron
RUN chmod a+x /etc/cron.d/hello-cron
RUN crontab /etc/cron.d/hello-cron

### PYTHON SCRIPT #########################################################

WORKDIR /opt/

ADD scraper scraper

ADD entrypoint entrypoint
RUN chmod a+x entrypoint

### START SCRIPT ##########################################################

ENTRYPOINT ["/opt/entrypoint"]
