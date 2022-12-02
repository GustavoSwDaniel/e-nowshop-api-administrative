FROM python:3.8


ENV LANG=C.UTF-8 \
  # python:
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  # poetry:
  POETRY_VERSION=1.1.10 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_HOME="/opt/poetry" \
  POETRY_CACHE_DIR='/var/cache/pypoetry'


RUN apt-get -y update && \
    apt-get install -y --no-install-recommends make wget gcc python3-dev libzbar0 && \
    rm -rf /var/lib/apt/lists/* && \
    pip install "poetry==$POETRY_VERSION" && poetry --version


WORKDIR /src

COPY ./src /src

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi

RUN rm -rf "$POETRY_CACHE_DIR"

EXPOSE 8083

CMD [ "python", "app.py" ]
