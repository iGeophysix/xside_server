# syntax=docker/dockerfile:1
FROM python:3.10.1

RUN apt-get update -y && apt-get upgrade -y

# Ставим зависимости GDAL, PROJ
RUN apt-get install -y gdal-bin libgdal-dev python3-gdal binutils libproj-dev

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/





