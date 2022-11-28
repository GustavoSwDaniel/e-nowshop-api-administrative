FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update && \
    apt-get install -y --no-install-recommends make wget gcc python3-dev libzbar0 && \
    rm -rf /var/lib/apt/lists/* && \
    pip install poetry && poetry --version

WORKDIR /backend

COPY src /backend/

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev


EXPOSE 8081