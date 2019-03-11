
### BASE CONTAINER #######################################################

FROM ubuntu:16.04

### PACKAGE MANAGER ######################################################

RUN apt-get clean && apt-get update && apt-get install -y locales
RUN locale-gen fr_FR.UTF-8

RUN apt-get update && apt-get install -yq \
python3 \
python3-pip \
wget \
unzip \
chromium-browser \
cron

### PYTHON REQUIREMENTS ###################################################

RUN pip3 install --upgrade pip

RUN python3 -m pip install numpy

ADD requirements.txt requirements.txt
RUN python3 -m pip install -r "requirements.txt"

### CHROMEDRIVER ##########################################################

RUN wget http://launchpadlibrarian.net/361669488/chromium-chromedriver_65.0.3325.181-0ubuntu0.14.04.1_armhf.deb -P /opt/
RUN dpkg -x /opt/chromium-chromedriver_65.0.3325.181-0ubuntu0.14.04.1_armhf.deb /opt/chromedriver/
RUN mv /opt/chromedriver/usr/lib/chromium-browser/* /opt/chromedriver/
RUN chmod 777 -R /opt/chromedriver/

### PYTHON SCRIPT #########################################################

WORKDIR /opt/

ADD scrapper.py scrapper.py
ADD main.py main.py
ADD mail.py mail.py
ADD config.ini config.ini

### CRON JOB ##############################################################

#RUN crontab -l > cron
RUN echo '0 23 * * * python3 /opt/main.py /opt/config.ini' >> cron
RUN crontab cron

RUN echo '#!/bin/sh' >> start.sh
RUN echo 'touch /etc/crontab /etc/cron.*/*' >> start.sh
RUN echo 'service cron start' >> start.sh
RUN echo '/bin/sh' >> start.sh

### START SCRIPT ##########################################################

CMD ["/opt/start.sh"]