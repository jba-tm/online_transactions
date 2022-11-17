FROM kartoza/postgis:13.0

COPY ./initialize.sh /docker-entrypoint-initdb.d/
