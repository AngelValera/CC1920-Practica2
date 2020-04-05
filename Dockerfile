# Sistema operativo base
FROM python:3.6

RUN mkdir /PrimerServicio
WORKDIR /PrimerServicio
COPY requirements.txt /PrimerServicio/
RUN pip install -r requirements.txt
ADD API /PrimerServicio/API