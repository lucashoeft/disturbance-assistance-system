FROM postgres:16

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y wget build-essential postgresql-server-dev-16

RUN wget https://github.com/pgvector/pgvector/archive/v0.7.0.tar.gz && \
    tar -xzvf v0.7.0.tar.gz && \
    cd pgvector-0.7.0 && \
    make && \
    make install

COPY ./init.sql /docker-entrypoint-initdb.d/