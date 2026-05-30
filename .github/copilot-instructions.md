# Copilot Instructions

## Build, test, and lint commands

- First-time database setup is documented at the repo root and runs from the repository root:
  ```sh
  chmod +x scripts/admin.sh
  ./scripts/admin.sh db create
  ./scripts/admin.sh db create-test
  ```
- Build the local backend image from the repo root:
  ```sh
  docker compose build backend
  ```
- Build the Railway/release backend image from the repo root:
  ```sh
  docker build -f backend/Dockerfile.release --target backend-release-app backend
  ```
- Start the local app stack that is currently wired up:
  ```sh
  docker compose up -d pg_database backend nginx
  ```
- Run the backend test suite locally from `backend/`:
  ```sh
  cd backend && uv run pytest
  ```
- Run a single test from `backend/`:
  ```sh
  cd backend && uv run pytest models/_tests/market/test_db.py -k test_market_db
  ```
- Run the containerized backend suite from the repo root:
  ```sh
  ./scripts/admin.sh test backend
  ```
- Formatting check from `backend/`:
  ```sh
  cd backend && uv run black --check .
  ```
- Flake8 is installed, but avoid `flake8 .` because it traverses `.venv`. Scope it to the source tree instead:
  ```sh
  cd backend && uv run flake8 api config constants db models scripts utils _factories _mocks conftest.py
  ```

## High-level architecture

- The repo is centered on a Docker Compose stack: `nginx` reverse proxy, `backend` FastAPI app, and `pg_database` Postgres. `nginx-reverse-proxy/conf/aoam.conf` proxies `/api` to `backend:3000`. The frontend is not wired yet.
- The Python backend lives in `backend/` and is packaged as several top-level modules (`api`, `config`, `db`, `models`, `scripts`, `utils`, `_factories`, `_mocks`). Imports use those module roots directly (`from db...`, `from models...`), not `from backend...`.
- `api.app.main:app` is the application entrypoint for both local Docker and Railway. It currently wires logging, trusted-host middleware, process-time middleware, and `/api/health-check`.
- Configuration flows through `config/env_vars.py` and `EnvVarManager`, which build a shared pydantic config object from environment variables. Database access goes through the singleton `DBSessionManager`, and the FastAPI DB dependency in `api/dependencies/db_session.py` owns commit/rollback/close.
- SQLAlchemy models inherit from `db.base_db.BaseDB`, which auto-derives plural table names and provides shared naming conventions, and most tables also mix in `models.mixins.TimestampsDB`.
- Alembic metadata is assembled by importing model modules in `backend/db/migrations/env.py`. Initial database bootstrap in `backend/scripts/db/initialize.py` does `BaseDB.metadata.create_all(engine)` and then stamps Alembic `head`.
- Tests are database-first and currently live under `backend/models/_tests`. `backend/conftest.py` switches the session to `test_aoam_property_plan`, upgrades the test DB to Alembic head at session start, and wraps each test in a transaction that is rolled back after the test.

## Key conventions

- When adding or renaming a model/table, update the model itself **and** the import lists in both `backend/db/migrations/env.py` and `backend/scripts/db/initialize.py`. If a model is not imported there, it will be missing from migration/init metadata.
- Table names are generated from class names in `BaseDB.__tablename__`: snake_case, `_db` stripped, then pluralized. Follow that pattern instead of hardcoding table names unless a migration requires an explicit compatibility override.
- Shared timestamp columns come from `models.mixins.TimestampsDB`; test factories mirror that behavior via `_factories/mixins/db.py`.
- The test suite relies on factory-boy factories in `_factories/*/db.py` and fixed timestamps from `_mocks/temporal.py`. If you add a required column or change nullability, update factories and affected tests together.
- Prefer `EnvVarManager().env_vars` for configuration reads so code uses the same defaults and type coercion as the rest of the backend.
- `scripts/admin.sh` is the main repo-level operations entrypoint for database create/init/drop flows, Alembic upgrade/downgrade, backend tests, and image publishing. It assumes the Docker Compose service names defined in `docker-compose.yml`.
- Non-production logging is set up through `utils/logging/init.py` with `rich.logging.RichHandler` and the custom `ExtendedLogger`; production switches to a standard stream handler.
