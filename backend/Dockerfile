FROM python:3.12-bullseye AS install-base
RUN apt-get update
RUN apt-get install --no-install-recommends -y libssl-dev build-essential vim nano
COPY --from=ghcr.io/astral-sh/uv:0.11.4 /uv /uvx /bin/


FROM install-base AS install-dev
WORKDIR /opt/aoam-property-plan/backend
COPY ./api \
    ./config \
    ./constants \
    ./db \
    ./models \
    ./scripts \
    ./utils \
    ./.python-version \
    ./alembic.ini \
    ./gunicorn_config.py \
    ./pyproject.toml \
    ./pytest.ini \
    ./uv.lock \
    ./
# COPY ./.python-version ./alembic.ini ./gunicorn_config.py ./pyproject.toml ./pytest.ini ./uv.lock ./
RUN uv venv --python 3.12
RUN uv sync --locked
# RUN useradd --uid 2000 aoam_app
# RUN chown -R aoam_app:aoam_app ./.venv
# RUN chown -R aoam_app:aoam_app /home/aoam_app/.cache/uv


FROM install-dev AS dev-base
WORKDIR /opt/aoam-property-plan/backend
ENV PYTHONUNBUFFERED=1
ENV FORCE_COLOR=1
RUN mkdir -p /var/log/aoam-property-plan
# RUN useradd --uid 2000 aoam_app
# RUN mkdir -p /opt/.venv
# RUN chown -R aoam_app:aoam_app /opt/.venv
# USER aoam_app
WORKDIR /opt/aoam-property-plan/backend
ENV PATH="/opt/aoam-property-plan/backend/.venv/bin:$PATH"
ENV PYTHONPATH="/opt/aoam-property-plan/backend/:$PYTHONPATH"



FROM dev-base AS backend-dev
ARG HOST
ARG PORT
ENV PYTHONUNBUFFERED=1
ENV FORCE_COLOR=1
# TODO: figure out why $HOST and $PORT aren't getting interpolated correctly
EXPOSE 3000
ENTRYPOINT [ "uvicorn", "api.app.main:app" ]
CMD [ "--host", "0.0.0.0", "--port", "3000", "--reload" ]


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
# RUN useradd --uid 2000 aoam_app
# RUN chown -R aoam_app:aoam_app ./.venv
# RUN chown -R aoam_app:aoam_app /home/aoam_app/.cache/uv
ENTRYPOINT [ "uv", "run", "pytest" ]
CMD [ "-s", "--import-mode=append" ]


FROM dev-base AS scraper-dev
ENV PATH="/opt/aoam-property-plan/backend/.venv/bin:$PATH"
ENV PYTHONPATH="/opt/aoam-property-plan/backend/:$PYTHONPATH"
USER root
WORKDIR /opt/aoam-property-plan/backend
ENTRYPOINT [ "python3", "scraper/main.py" ]


FROM install-base AS install-release
WORKDIR /opt/aoam-property-plan/backend
COPY ./pyproject.toml ./uv.lock ./
RUN uv venv --python 3.12
RUN uv sync --locked
RUN useradd --uid 2000 aoam_app
RUN chown -R aoam_app:aoam_app /opt/aoam-property-plan/backend/.venv


FROM python:3.12-bullseye AS release-base
RUN apt-get update
RUN apt-get install --no-install-recommends -y libssl-dev vim nano
RUN useradd --uid 2000 aoam_app
RUN mkdir -p /var/log/aoam-property-plan/backend
RUN chown -R aoam_app:aoam_app /var/log/aoam-property-plan/backend
USER aoam_app
ARG venv
WORKDIR /opt/aoam-property-plan/backend
ENV PATH="/opt/aoam-property-plan/backend/.venv/bin:$PATH"
ENV PYTHONPATH="/opt/aoam-property-plan/backend/:$PYTHONPATH"
COPY --from=install-release /opt/.venv /opt/.venv
COPY --from=install-release /opt/aoam-property-plan/backend/ ./
COPY backend/scraper ./backend/scraper
COPY backend/alembic.ini ./

# Maybe backend-api? api-server?
FROM release-base AS backend
ARG HOST
ARG PORT
ENTRYPOINT [ "uvicorn", "api.app.main:app" ]
CMD [ "--host", "$HOST", "--port", "$PORT"]
# ^ may need to change this command
