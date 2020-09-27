
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

ADD scrapper.py scrapper.py
ADD main.py main.py
ADD mail.py mail.py

### CRON JOB ##############################################################

#RUN crontab -l > cron
RUN echo '0 18 * * * python3 /opt/main.py /opt/config.ini' >> cron
RUN crontab cron

### START SCRIPT ##########################################################

ADD entrypoint entrypoint
RUN chmod +x entrypoint

ENTRYPOINT ["/entrypoint"]
