# define an alias for the specific python version used in this file.
FROM docker.io/python:3.12-slim-bookworm AS python

# Python build stage
FROM python AS python-build-stage

ARG BUILD_ENVIRONMENT=development

# Python 'run' stage
FROM python AS python-run-stage

ARG BUILD_ENVIRONMENT=development
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV BUILD_ENV=${BUILD_ENVIRONMENT}

ADD . /app
WORKDIR ${APP_HOME}

RUN addgroup --system django \
  && adduser --system --ingroup django django

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg dependencies
  libpq-dev \
  # uv dep
  curl \
  ca-certificates \
  gettext \
  locales

# install dep
ENV UV_INSTALL_DIR="/root/.local/bin/"
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/
ENV PATH="/root/.local/bin/:$PATH"
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync -U --compile-bytecode --no-cache --no-editable

COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

# Don't create media and staticfiles directories - they'll be mounted as volumes

# Copy production startup scripts
COPY --chown=django:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# copy application code to WORKDIR
COPY --chown=django:django . ${APP_HOME}

# Copy development startup script (after app code is copied)
COPY --chown=django:django ./compose/development/django/start-dev /start-dev
RUN sed -i 's/\r$//g' /start-dev
RUN chmod +x /start-dev

# make django owner of the WORKDIR directory as well.
RUN chown -R django:django ${APP_HOME}

USER django

ENTRYPOINT ["/entrypoint"] 