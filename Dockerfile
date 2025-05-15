FROM python:3.10.13-alpine3.19

ENV PYTHONUNBUFFERED 1
ENV UVICORN_CMD_ARGS ""

EXPOSE 8000

# Install system-wide dependencies
RUN apk update \
    && apk add --no-cache --clean-protected git curl gcc python3-dev \
    && rm -rf /var/cache/apk/*

# Update unsecure package in global root scope
RUN pip install --no-cache-dir setuptools==70.0.0
COPY ./upgrade-packages.sh ./apk-packages.txt ./
RUN ./upgrade-packages.sh

# Create user for app
ENV APP_USER=appuser
RUN adduser -D $APP_USER
WORKDIR /home/$APP_USER
USER $APP_USER

# Use venv directly via PATH
ENV VENV_PATH=/home/$APP_USER/.venv/bin
ENV USER_PATH=/home/$APP_USER/.local/bin
ENV PATH="$VENV_PATH:$USER_PATH:$PATH"

RUN pip install --no-cache-dir poetry==2.1.2 && \
  poetry config virtualenvs.in-project true

COPY pyproject.toml ./

RUN poetry lock && poetry install --no-root --only main


COPY alembic.ini .
COPY app app
RUN mkdir ./attachments

ARG CI_COMMIT_SHA=""
ENV GIT_COMMIT_SHA=${CI_COMMIT_SHA}

CMD python -m http.server