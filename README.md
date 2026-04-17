# Allai

Proof-Oriented MVP v1 scaffold implementing constitutional closure gates.

## PostgreSQL schema and seed

```bash
REPO_ROOT="/path/to/Allai"
cd "$REPO_ROOT"
psql "$DATABASE_URL" -f "$REPO_ROOT/db/schema/sql/001_atomic_arabic_schema.sql"
psql "$DATABASE_URL" -f "$REPO_ROOT/db/seed/sql/001_atomic_arabic_seed.sql"
```

## Run tests

```bash
cd /home/runner/work/Allai/Allai
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py' -v
```
