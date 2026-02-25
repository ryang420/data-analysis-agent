# AGENTS.md

## Cursor Cloud specific instructions

### Overview

This is a **Data Analysis Agent** — an AI chatbot for supermarket sales data analysis. It has two services:

- **Backend** (Python FastAPI + LangGraph agent, port 8000)
- **Frontend** (Vite + React chat UI, port 5173)

The agent uses LLM tool-calling to execute SQL queries against a PostgreSQL database with ~42,816 sales records.

### Prerequisites

- **PostgreSQL** must be running locally. Start with: `sudo pg_ctlcluster 16 main start`
- **`python` symlink** must exist (`sudo ln -sf /usr/bin/python3 /usr/bin/python`) because `backend/scripts/http_run.sh` invokes `python` not `python3`.
- Environment variables `PGDATABASE_URL` and `OPENAI_API_KEY` must be set (via `.env` in repo root or exported).
- `PATH` must include `/home/ubuntu/.local/bin` for pip-installed tools (pylint, pytest, uvicorn, etc.).

### Database Setup (one-time)

<<<<<<< HEAD
If the database has not been initialized yet:

```bash
sudo -u postgres psql -c "CREATE USER devuser WITH PASSWORD 'devpass' CREATEDB;"
sudo -u postgres psql -c "CREATE DATABASE salesdb OWNER devuser;"
# Set PGDATABASE_URL to your local PostgreSQL connection string
=======
If the database has not been initialized yet, create the PostgreSQL user and database to match `PGDATABASE_URL`, then create the table and import data:

```bash
# Parse user/password/db from the PGDATABASE_URL secret and create them locally
PG_USER=$(echo "$PGDATABASE_URL" | sed -n 's|postgresql://\([^:]*\):.*|\1|p')
PG_PASS=$(echo "$PGDATABASE_URL" | sed -n 's|postgresql://[^:]*:\([^@]*\)@.*|\1|p')
PG_DB=$(echo "$PGDATABASE_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')
sudo -u postgres psql -c "CREATE USER $PG_USER WITH PASSWORD '$PG_PASS' CREATEDB SUPERUSER;"
sudo -u postgres psql -c "CREATE DATABASE $PG_DB OWNER $PG_USER;"
>>>>>>> cursor/development-environment-setup-ad8f
psql "$PGDATABASE_URL" -f backend/scripts/create_sales_data_table.sql
PYTHONPATH=backend/src python3 backend/scripts/import_csv_to_db.py
```

### Running Services

See `README.md` for standard commands. Key notes:

- **Backend**: `bash backend/scripts/http_run.sh -p 8000` (starts uvicorn on port 8000)
- **Frontend**: `cd frontend && npx vite --host 0.0.0.0 --port 5173` (Vite dev server proxies API to backend)
- The backend falls back to in-memory `MemorySaver` if PostgreSQL is unavailable, but SQL query tools will fail without a live database.

### Lint & Test

- **Backend lint**: `cd backend && PYTHONPATH=src pylint src/ --rcfile /workspace/.pylintrc`
- **Frontend type check**: `cd frontend && npx tsc --noEmit`
<<<<<<< HEAD
- **Frontend lint**: `cd frontend && npx eslint .` (requires `eslint.config.js` which is currently missing from the repo)
=======
- **Frontend lint**: `cd frontend && npx eslint .`
>>>>>>> cursor/development-environment-setup-ad8f
- **Backend tests**: `cd backend && PYTHONPATH=src pytest` (no test files currently in the repo)

### Gotchas

- The `/v1/chat/completions` endpoint requires a `session_id` field in the request body (non-standard OpenAI extension).
- The `.pylintrc` at repo root sets `init-hook` to add `src` to `sys.path`.
<<<<<<< HEAD
- The frontend `eslint.config.js` file is missing; ESLint v9 will fail without it. TypeScript checking via `tsc --noEmit` works as an alternative.
=======
- Frontend TypeScript checking via `tsc --noEmit` is a useful complement to ESLint.
>>>>>>> cursor/development-environment-setup-ad8f
