# Vercel deployment notes

## Why you saw `FUNCTION_INVOCATION_FAILED`

Two frequent causes fixed in code:

1. **Root folder `api/`** — Vercel treats **`api/**/*.py`** as Python serverless entrypoints. A FastAPI package named **`api/`** clashes with that. Routes now live under **`routers/`** (URL prefix is still **`/api/v1`**).

2. **DB DDL on startup** — `create_all()` on every cold start often fails against **`db.*.supabase.co:5432`** from serverless. On Vercel, automatic **`create_all` is skipped unless** you set **`ENABLE_VERCEL_SCHEMA_CREATE=1`**. Prefer **Supabase transaction pooler** `DATABASE_URL` and create tables via **`migrate.py`/Alembic**.

## Env vars on Vercel

- **`DATABASE_URL`** — Use the **pooler** URI from Supabase (often port **6543**). Add **`?sslmode=require`** when needed.

- **`SECRET_KEY`**, **`ALGORITHM`**, **`ACCESS_TOKEN_EXPIRE_MINUTES`**

- **`ENABLE_VERCEL_SCHEMA_CREATE=1`** — optional; enables `create_all` on cold starts (normally off).

## CORS

`main.py` currently allows **`http://localhost:3000`**. Add your deployed admin origin if requests are blocked by CORS.

## After merging

Commit, **`git push origin main`**, redeploy on Vercel. If errors remain, open **Deployments → Logs** and copy the Python traceback.
