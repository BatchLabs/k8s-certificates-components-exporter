FROM fedora:30

WORKDIR /app
LABEL MAINTAINER="Arnaud B. <arnaud.bawol@batch.com>"

COPY . .

RUN mkdir /log \
  && dnf upgrade -y \
  && pip3 install -r requirements.txt


ENTRYPOINT [ "/app/monitor.py" ]