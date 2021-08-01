FROM python:3.9.1-buster AS reqs

# https://github.com/mkleehammer/pyodbc/wiki/Install
# https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15
# https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Linux
COPY requirements.txt requirements.txt
RUN \
curl -s -o microsoft.asc https://packages.microsoft.com/keys/microsoft.asc && \
curl -s -o mssql-release.list https://packages.microsoft.com/config/debian/10/prod.list && \
apt-get update -y && \
apt-get install -y g++ && \
apt-get install -y unixodbc-dev && \
pip install -r requirements.txt


FROM python:3.9.1-slim-buster

COPY ./server /srv/app
COPY --from=reqs /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=reqs /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# https://github.com/mkleehammer/pyodbc/wiki/Install
# https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15
# https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Linux
COPY --from=reqs microsoft.asc microsoft.asc
COPY --from=reqs mssql-release.list mssql-release.list
ENV ACCEPT_EULA=Y
RUN \
apt-get update -y && \
apt-get install -y gnupg2 && \
apt-key add microsoft.asc && \
rm microsoft.asc && \
mv mssql-release.list /etc/apt/sources.list.d/mssql-release.list && \
apt-get update -y && \
apt-get install -y unixodbc-bin && \
apt-get install -y msodbcsql17 && \
apt-get install -y libgssapi-krb5-2

ENV PYTHONUNBUFFERED=1

EXPOSE 8080
WORKDIR /srv/app/

ENTRYPOINT \
echo 'Waiting 20 seconds for database to be ready...' && \
sleep 20 && \
gunicorn --bind 0.0.0.0:8080 --timeout=30 --workers=1 ${FLASK_APP}
