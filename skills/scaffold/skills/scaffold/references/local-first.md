# Local-First Development

## Principle

Every cloud-deployed service must be fully runnable on a developer's machine with a single command. This is an architectural constraint that produces better systems, not just a developer convenience.

## Why This Matters

The speed of the change → test → validate loop determines development velocity. Cloud deployment: minutes to hours. Local execution: seconds. Over the life of a project, this difference is enormous.

Local-first also forces good architecture. If a service can only run when connected to managed Postgres, a specific Redis cluster, and a proprietary object store, its components are too tightly coupled. Designing for local operation naturally produces the abstractions that also make the system testable, portable, and easier to reason about.

## Requirements

### 1. Dependency abstraction
Every external dependency must be replaceable with a local equivalent via a thin interface layer.

**Storage backends:**
```python
# settings.py
STORAGE_BACKEND = os.environ.get("STORAGE_BACKEND", "local")  # local | minio | b2

# storage.py
class StorageBackend(Protocol):
    async def put(self, key: str, data: bytes) -> None: ...
    async def get(self, key: str) -> bytes | None: ...
    async def delete(self, key: str) -> None: ...

class LocalStorage(StorageBackend):
    """Writes to filesystem. For local development."""
    def __init__(self, base_dir: str = "./devdata/blobs"): ...

class MinioStorage(StorageBackend):
    """S3-compatible. For local development with closer-to-prod behavior."""
    ...

class B2Storage(StorageBackend):
    """Backblaze B2. For staging/production."""
    ...
```

Same principle applies to databases (local Postgres via Docker), caches (local Redis via Docker), queues, and any external API. Same interface, same key structure, same error semantics.

### 2. Single-command startup
Provide `docker-compose.yml` that brings up all dependencies:

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: myapp
      POSTGRES_PASSWORD: dev
    ports: ["5432:5432"]

  redis:
    image: redis:7
    ports: ["6379:6379"]

  minio:  # Optional: S3/B2 emulator
    image: minio/minio
    command: server /data
    ports: ["9000:9000"]
```

Plus a Makefile:
```makefile
dev:          ## Start all dependencies, run migrations, start the service
	docker compose up -d
	uv run alembic upgrade head
	uv run python -m myapp.api

test:         ## Run integration tests against local dependencies
	docker compose up -d
	uv run pytest

test-unit:    ## Run unit tests (no external dependencies)
	uv run pytest tests/unit

seed:         ## Populate local environment with test data
	uv run python scripts/seed.py

migrate:      ## Run database migrations
	uv run alembic upgrade head

lint:         ## Run linter and type checker
	uv run ruff check .
	uv run ruff format --check .
```

A new developer should go from `git clone` to a running system in under two minutes.

### 3. Seed data
Provide a seed script that populates the local environment with realistic test data. Developers should be able to exercise the full API immediately, not spend time crafting test payloads.

### 4. Test parity
Integration tests run against the same local dependencies that `make dev` starts. Tests should never require cloud credentials, network access, or shared environments. The CI pipeline runs the same docker-compose setup.

### 5. Configuration via environment variables
The service reads all connection strings, feature flags, and behavioral settings from environment variables. Local `.env` files configure the local setup. No code changes to switch between local and cloud.

```bash
# .env.local
DATABASE_URL=postgresql://postgres:dev@localhost:5432/myapp
REDIS_URL=redis://localhost:6379
STORAGE_BACKEND=local
LOCAL_BLOB_DIR=./devdata/blobs
LOG_LEVEL=debug
```

```bash
# .env.production
DATABASE_URL=postgresql://...@ubicloud-host:5432/myapp
REDIS_URL=redis://redis-host:6379
STORAGE_BACKEND=b2
B2_KEY_ID=...
B2_APP_KEY=...
B2_BUCKET_NAME=myapp-prod
LOG_LEVEL=info
OTEL_EXPORTER_OTLP_ENDPOINT=https://...
```

## Review Checklist

When reviewing any spec or setting up any project, verify:
- Can I run this locally with no cloud accounts?
- Is there a single-command startup?
- Does every external dependency have a local substitute?
- Are integration tests runnable against local dependencies?
- Is there seed data?
- Is the local setup maintained as a first-class artifact?

If the answer to any of these is no, something in the design needs an abstraction layer. Flag it as a design gap, not a nice-to-have.
