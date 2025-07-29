# define an alias for the specific python version used in this file.
FROM docker.io/python:3.12-slim-bookworm AS python

# Python build stage
FROM python AS python-build-stage

ARG BUILD_ENVIRONMENT=production

# Requirements are installed here to ensure they will be cached.



# Python 'run' stage
FROM python AS python-run-stage

ARG BUILD_ENVIRONMENT=production
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


# RUN sed -i '/fa_IR.UTF-8/s/^# //g' /etc/locale.gen && \
#  locale-gen

# ENV LANG fa_IR.UTF-8
# ENV LC_ALL fa_IR.UTF-8
# ENV LANGUAGE fa_IR.UTF-8

# install dep
ENV UV_INSTALL_DIR="/root/.local/bin/"
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/
ENV PATH="/root/.local/bin/:$PATH"
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync -U --compile-bytecode --no-cache --no-editable

COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

RUN mkdir /app/staticfiles
RUN chown django:django /app/staticfiles

RUN mkdir /app/media -p
RUN chown django:django /app/media

COPY --chown=django:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY --chown=django:django ./compose/production/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker


COPY --chown=django:django ./compose/production/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

# copy application code to WORKDIR
COPY --chown=django:django . ${APP_HOME}

# make django owner of the WORKDIR directory as well.
RUN chown -R django:django ${APP_HOME}

USER django


ENTRYPOINT ["/entrypoint"]
