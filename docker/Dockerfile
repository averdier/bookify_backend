FROM python:3.6
MAINTAINER Verdier Arthur <a.verdier@outlook.fr>

ADD ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

RUN mkdir /bookify

ADD ./app/ /bookify/app/
ADD ./*.py /bookify/
ADD ./docker/docker-entrypoint.sh /bookify

WORKDIR /bookify/

RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]



