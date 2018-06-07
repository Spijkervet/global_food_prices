FROM ubuntu:latest
MAINTAINER Janne Spijkervet "janne.spijkervet@hotmail.com"
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential libmysqlclient-dev
# COPY . /app
ADD . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["app.py"]
