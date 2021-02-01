FROM python:3
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN apt-get update && apt-get install -y \
	nano \
	cron \
	wkhtmltopdf
RUN pip3 install --no-cache-dir -r requirements.txt

ADD crontab /etc/cron.d/icms-cron
RUN chmod 0644 /etc/cron.d/icms-cron
RUN crontab /etc/cron.d/icms-cron
RUN touch /var/log/icms_crawler.log

VOLUME /icms_crawler
WORKDIR /icms_crawler
CMD cron && tail -f /var/log/icms_crawler.log
