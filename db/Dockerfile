FROM postgres:14.7-bullseye

EXPOSE 5432/tcp

WORKDIR /docker-entrypoint-initdb.d

ADD ./db/psql.sql /docker-entrypoint-initdb.d
