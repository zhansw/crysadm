FROM daocloud.io/python:3.3-onbuild
MAINTAINER Jinrui Wang <306090773@qq.com>

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app

EXPOSE 3000

CMD [ "python","crysadm.py"]