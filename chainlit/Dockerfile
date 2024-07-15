FROM python:3.9-slim

WORKDIR /chainlit

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8000

# HEALTHCHECK CMD curl --fail -I http://localhost:8000/

ENTRYPOINT ["chainlit", "run", "demo.py", "-w"]