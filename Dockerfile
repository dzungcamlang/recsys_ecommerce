FROM ubuntu
RUN apt-get update && apt-get install -y \
    software-properties-common
RUN apt-get update && apt-get install -y \
    python3.7 \
    python3-pip
RUN python3.7 -m pip install pip
RUN apt-get update && apt-get install -y \
    python3-distutils \
    python3-setuptools
RUN apt-get install -y wget
RUN apt-get install unzip
RUN wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-386.zip
RUN unzip ngrok-stable-linux-386.zip -d /usr/local/bin
RUN apt-get install -y python-dev python3.7-dev \
     build-essential libssl-dev libffi-dev \
     libxml2-dev libxslt1-dev zlib1g-dev \
     python-pip
RUN mkdir /recsys_website
ADD ./requirements.txt /recsys_website/requirements.txt
RUN python3.7 -m pip install -r /recsys_website/requirements.txt
ADD ./recsys /recsys_website/recsys
ADD ./site_src /recsys_website/site_src
WORKDIR /recsys_website
