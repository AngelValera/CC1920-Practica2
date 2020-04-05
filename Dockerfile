# Sistema operativo base
FROM python:3.6

RUN mkdir /PrimerServicio
RUN mkdir /PrimerServicio/Models
WORKDIR /PrimerServicio
COPY requirements.txt /PrimerServicio/
RUN apt-get update && pip install --upgrade pip && pip install --requirement requirements.txt
COPY API/* /PrimerServicio/
COPY API/Models/* /PrimerServicio/Models/ 