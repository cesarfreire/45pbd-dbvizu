FROM python:3.10-alpine3.18
LABEL maintainer="iceesar@live.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /app/requirements.txt
COPY ./core /app/core
COPY ./dbvizu /app/dbvizu
COPY ./templates /app/templates
COPY ./manage.py /app/manage.py
COPY ./scripts /app/scripts

WORKDIR /app
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip

RUN apk add --update --no-cache sqlite postgresql-client bind-tools net-tools graphviz graphviz-dev python3-dev && \
    apk add --update --no-cache --virtual .tmp-deps  \
        build-base postgresql-dev musl-dev linux-headers

RUN /py/bin/pip install -r /app/requirements.txt && \
    apk del .tmp-deps && \
    adduser --disabled-password --no-create-home app && \
    mkdir -p /vol/static && \
    mkdir -p /vol/media && \
    chown -R app:app /vol && \
    chmod -R +x /app/scripts && \
    chown -R app:app /app

ENV PATH="/app/scripts:/py/bin:$PATH"

USER app

CMD ["run.sh"]