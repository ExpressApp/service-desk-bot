FROM registry.ccsteam.ru/bots-cicd-images/python:3.10.13-alpine

ENV PYTHONUNBUFFERED 1
ENV UVICORN_CMD_ARGS ""

EXPOSE 8000

# Install system-wide dependencies
RUN apk update \
    && apk add --no-cache --clean-protected git curl gcc python3-dev \
    && rm -rf /var/cache/apk/*

# Create user for app
ENV APP_USER=appuser
RUN adduser -D $APP_USER
WORKDIR /home/$APP_USER
USER $APP_USER

# Use venv directly via PATH
ENV VENV_PATH=/home/$APP_USER/.venv/bin
ENV USER_PATH=/home/$APP_USER/.local/bin
ENV PATH="$VENV_PATH:$USER_PATH:$PATH"

RUN pip install --user --no-cache-dir poetry==1.2.2 && \
  poetry config virtualenvs.in-project true

COPY poetry.lock pyproject.toml ./


RUN poetry install --only main


COPY alembic.ini .
COPY app app
RUN mkdir ./attachments

ARG CI_COMMIT_SHA=""
ENV GIT_COMMIT_SHA=${CI_COMMIT_SHA}

CMD alembic upgrade head && \
   gunicorn "app.main:get_application()" --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0
