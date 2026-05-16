# ARG venv=/opt/.venv

FROM python:3.12-bullseye AS install-base
# RUN apt-get update
# RUN apt-get install --no-install-recommends -y libssl-dev build-essential vim nano \
COPY --from=ghcr.io/astral-sh/uv:0.11.4 /uv /uvx /bin/


FROM install-base AS install-dev
COPY ./pytest.ini ./pyproject.toml ./uv.lock ./
RUN uv sync --locked
RUN useradd --uid 2000 aoam_app
RUN chown -R aoam_app:aoam_app /opt/.venv


FROM install-base AS dev-base
WORKDIR /opt/aoam-property-plan/backend
# ENV VIRTUAL_ENV=$venv
ENV PYTHONUNBUFFERED=1
ENV FORCE_COLOR=1
RUN mkdir -p /var/log/aoam-property-plan
RUN useradd --uid 2000 aoam_app
RUN mkdir -p /opt/.venv
RUN chown -R aoam_app:aoam_app /opt/.venv
USER aoam_app
ARG venv
WORKDIR /opt/aoam-property-plan/backend
ENV PATH="$venv/bin:$PATH"
ENV PYTHONPATH="/opt/aoam-property-plan/backend/api/:$PYTHONPATH"
COPY --from=install-dev /opt/.venv /opt/.venv


FROM dev-base AS server-dev
ARG HOST
ARG PORT
ENV PYTHONUNBUFFERED=1
ENV FORCE_COLOR=1
# TODO: figure out why $HOST and $PORT aren't getting interpolated correctly
EXPOSE 3000
ENTRYPOINT [ "uvicorn", "backend.api.app:app" ]
CMD [ "--host", "0.0.0.0", "--port", "3000", "--reload" ]


FROM dev-base AS server-migrations
ARG HOST
ARG PORT
ENV PYTHONUNBUFFERED=1
ENV FORCE_COLOR=1
ENTRYPOINT [ "alembic" ]


FROM dev-base AS server-scripts
ARG HOST
ARG PORT
ENV PYTHONUNBUFFERED=1
ENV FORCE_COLOR=1
ENTRYPOINT [ "python" ]


FROM dev-base AS server-test
ARG HOST
ARG PORT
ENV PYTHONUNBUFFERED=1
ENV FORCE_COLOR=1
ENTRYPOINT [ "uv", "run", "pytest" ]
CMD [ "-s", "--import-mode=append" ]


FROM dev-base AS scraper-dev
ENV PATH="$venv/bin:$PATH"
ENV PYTHONPATH="/opt/aoam-property-plan/backend/api/:$PYTHONPATH"
USER root
WORKDIR /opt/aoam-property-plan/backend
ENTRYPOINT [ "python3", "nlp_ssa/scraper/main.py" ]


FROM install-base AS install-release
COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --locked
RUN useradd --uid 2000 aoam_app
RUN chown -R aoam_app:aoam_app /opt/.venv


FROM python:3.12-bullseye AS release-base
RUN apt-get update
RUN apt-get install --no-install-recommends -y libssl-dev vim nano
RUN useradd --uid 2000 aoam_app
RUN mkdir -p /var/log/aoam-property-plan/backend
RUN chown -R aoam_app:aoam_app /var/log/aoam-property-plan/backend
USER aoam_app
ARG venv
WORKDIR /opt/aoam-property-plan/backend
ENV PATH="$venv/bin:$PATH"
ENV PYTHONPATH="backend/:$PYTHONPATH"
COPY --from=install-release /opt/.venv /opt/.venv
COPY --from=install-release /opt/aoam-property-plan/backend/ ./
COPY backend/scraper ./backend/scraper
COPY backend/alembic.ini ./

# Maybe server-api? api-server?
FROM release-base AS server
ARG HOST
ARG PORT
ENTRYPOINT [ "uvicorn", "api.app:app" ]
CMD [ "--host", "$HOST", "--port", "$PORT"]
# ^ may need to change this command
