FROM python:3.11-slim

RUN apt update && apt upgrade -y
RUN apt install -y wkhtmltopdf

COPY main.py .
COPY src/ .
COPY requirements.txt .

RUN pip3 install -r requirements.txt

EXPOSE 8080