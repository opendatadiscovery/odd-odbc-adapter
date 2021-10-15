FROM python:3.9.1-slim-buster as base
ENV POETRY_PATH=/opt/poetry \
    POETRY_VERSION=1.1.6
ENV PATH="$POETRY_PATH/bin:$VENV_PATH/bin:$PATH"

FROM base AS build

RUN apt-get update && \
    apt-get install -y -q build-essential \
    curl

RUN curl -s -o microsoft.asc https://packages.microsoft.com/keys/microsoft.asc && \
    curl -s -o mssql-release.list https://packages.microsoft.com/config/debian/10/prod.list
RUN apt-get update -y && \
    apt-get install -y g++ unixodbc-dev

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
RUN mv /root/.poetry $POETRY_PATH
RUN poetry config virtualenvs.create false
RUN poetry config experimental.new-installer false

COPY poetry.lock pyproject.toml ./
RUN poetry install --no-interaction --no-ansi --no-dev -vvv


FROM base as runtime

COPY --from=build microsoft.asc microsoft.asc
COPY --from=build mssql-release.list mssql-release.list

ENV ACCEPT_EULA=Y
RUN apt-get update -y && apt-get install -y gnupg2 \
    && apt-key add microsoft.asc && rm microsoft.asc && \
    mv mssql-release.list /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update -y && apt-get install -y unixodbc-bin
RUN apt-get install -y msodbcsql17
RUN apt-get install -y libgssapi-krb5-2

RUN useradd --create-home --shell /bin/bash app
USER app

# non-interactive env vars https://bugs.launchpad.net/ubuntu/+source/ansible/+bug/1833013
ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN=true
ENV UCF_FORCE_CONFOLD=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

WORKDIR /app
COPY . ./
COPY --from=build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=build /usr/local/bin/gunicorn /usr/local/bin/gunicorn

ENTRYPOINT \
echo 'Waiting 20 seconds for database to be ready...' && \
sleep 20 && \
gunicorn --bind 0.0.0.0:8080 --timeout=30 --workers=1 ${FLASK_APP}
