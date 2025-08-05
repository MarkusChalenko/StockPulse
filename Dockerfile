FROM python:3.12.10-slim-bullseye

RUN apt-get update && apt-get install -y tzdata

ENV TZ="Europe/Moscow" \
    PYTHONPATH=src/ \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN python -m pip install --no-cache-dir poetry==2.1.3 \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root \
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY src ./src/
COPY .env .env

VOLUME /app

ENTRYPOINT ["python3", "src/main.py"]
