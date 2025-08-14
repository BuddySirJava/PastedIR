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

WORKDIR ${APP_HOME}

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
  locales \
  # Headless browser dependencies
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libdbus-glib-1-2

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/
ENV PATH="/root/.local/bin/:$PATH"
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

# Copy dependency files and install dependencies
# This layer is cached and only re-run when dependency files change
COPY pyproject.toml uv.lock ./
RUN uv sync -U --compile-bytecode --no-cache --no-editable && \
    uv pip install --system gunicorn gevent

# Create non-root user
RUN addgroup --system django \
  && adduser --system --ingroup django django

# Copy entrypoint and startup scripts
COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY --chown=django:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY --chown=django:django ./compose/development/django/start-dev /start-dev
RUN sed -i 's/\r$//g' /start-dev
RUN chmod +x /start-dev

# Copy the rest of the application code
COPY --chown=django:django . ${APP_HOME}

# make django owner of the WORKDIR directory as well.
RUN chown -R django:django ${APP_HOME}

USER django

ENTRYPOINT ["/entrypoint"]
