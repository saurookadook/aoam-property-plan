FROM python:3.12-bullseye AS install-base
RUN apt-get update
RUN apt-get install --no-install-recommends -y libssl-dev build-essential vim nano
COPY --from=ghcr.io/astral-sh/uv:0.11.4 /uv /uvx /bin/


FROM install-base AS install-dev
WORKDIR /opt/aoam-property-plan/backend
COPY ./backend/_factories ./_factories
COPY ./backend/_mocks ./_mocks
COPY ./backend/api ./api
COPY ./backend/config ./config
COPY ./backend/constants ./constants
COPY ./backend/db ./db
COPY ./backend/models ./models
COPY ./backend/scripts ./scripts
COPY ./backend/utils ./utils
COPY ./backend/.python-version \
    ./backend/alembic.ini \
    ./backend/gunicorn_config.py \
    ./backend/pyproject.toml \
    ./backend/README.md \
    ./backend/pytest.ini \
    ./backend/uv.lock \
    ./
# COPY ./.python-version ./alembic.ini ./gunicorn_config.py ./pyproject.toml ./pytest.ini ./uv.lock ./
RUN uv venv --python 3.12
RUN uv sync --locked
# RUN useradd --uid 2000 aoam_app
# RUN chown -R aoam_app:aoam_app ./.venv
# RUN chown -R aoam_app:aoam_app /home/aoam_app/.cache/uv


FROM install-dev AS dev-base
ENV PYTHONUNBUFFERED=1
ENV FORCE_COLOR=1
RUN mkdir -p /var/log/aoam-property-plan
# RUN useradd --uid 2000 aoam_app
# RUN mkdir -p /opt/.venv
# RUN chown -R aoam_app:aoam_app /opt/.venv
# USER aoam_app
WORKDIR /opt/aoam-property-plan/backend
ENV PATH="/opt/aoam-property-plan/backend/.venv/bin:$PATH"
ENV PYTHONPATH="/opt/aoam-property-plan/backend"
ENV PYTHONPATH="/opt/aoam-property-plan/backend"



FROM dev-base AS backend-dev
ARG HOST
ARG PORT
ENV PYTHONUNBUFFERED=1
ENV FORCE_COLOR=1
# TODO: figure out why $HOST and $PORT aren't getting interpolated correctly
EXPOSE 3000
WORKDIR /opt/aoam-property-plan/backend
ENTRYPOINT [ "uvicorn", "api.app.main:app" ]
CMD [ \
  "--host", "0.0.0.0", \
  "--port", "3000", \
  "--reload" \
]


FROM dev-base AS backend-migrations
ARG HOST
ARG PORT
ENV PYTHONUNBUFFERED=1
ENV FORCE_COLOR=1
# RUN useradd --uid 2000 aoam_app
# RUN chown -R aoam_app:aoam_app ./.venv
# RUN chown -R aoam_app:aoam_app /home/aoam_app/.cache/uv
ENTRYPOINT [ "uv", "run", "alembic" ]


FROM dev-base AS backend-scripts
ARG HOST
ARG PORT
ENV PYTHONUNBUFFERED=1
ENV FORCE_COLOR=1
# RUN useradd --uid 2000 aoam_app
# RUN chown -R aoam_app:aoam_app ./.venv
# RUN chown -R aoam_app:aoam_app /home/aoam_app/.cache/uv
ENTRYPOINT [ "uv", "run", "python3" ]


FROM dev-base AS backend-test
ARG HOST
ARG PORT
ENV PYTHONUNBUFFERED=1
ENV FORCE_COLOR=1
WORKDIR /opt/aoam-property-plan
COPY _research ./_research
WORKDIR /opt/aoam-property-plan/backend
COPY ./backend/_factories ./_factories
COPY ./backend/_mocks ./_mocks
COPY ./backend/conftest.py \
    ./backend/pytest.ini \
    ./
# RUN useradd --uid 2000 aoam_app
# RUN chown -R aoam_app:aoam_app ./.venv
# RUN chown -R aoam_app:aoam_app /home/aoam_app/.cache/uv
ENTRYPOINT [ "uv", "run", "pytest" ]
CMD [ "-s", "--import-mode=append" ]


FROM dev-base AS scraper-dev
ENV PATH="/opt/aoam-property-plan/backend/.venv/bin:$PATH"
ENV PYTHONPATH="/opt/aoam-property-plan/backend"
ENV PYTHONPATH="/opt/aoam-property-plan/backend"
USER root
WORKDIR /opt/aoam-property-plan/backend
ENTRYPOINT [ "python3", "scraper/main.py" ]
