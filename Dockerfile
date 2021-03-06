FROM ubuntu:20.04

RUN apt update \
    && apt install --assume-yes python3-dev python3-pip

RUN useradd --create-home farapp
RUN mkdir /data/ \
    && chown farapp:farapp /data/
WORKDIR /home/farapp
USER farapp

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY app.py ./
COPY index.py ./
COPY apps/ ./apps/
COPY far_core/ ./far_core/

EXPOSE 8080/tcp

CMD PYTHONPATH=$(pwd) python3 index.py
