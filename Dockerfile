# Sistema operativo base
FROM python:3.6

RUN mkdir /SegundoServicio
WORKDIR /SegundoServicio
COPY requirements.txt /SegundoServicio/
RUN apt-get update && pip install --upgrade pip && pip install --requirement requirements.txt
COPY API/* /SegundoServicio/
