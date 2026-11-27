# A B Traders backend

FastAPI app behind thermalpaperlabels.com: the product list (`GET /products`) and enquiries (`POST /inquiries`),
stored in Supabase Postgres (`DATABASE_URL`), with an email to the owner for each enquiry.

## Settings (environment variables)

| Variable | What it does | Default |
|---|---|---|
| `DATABASE_URL` | The database | local SQLite `test.db` |
| `ADMIN_API_KEY` | Key for changing products (header `X-Admin-Key`). Unset: product changes are off. | unset |
| `ALLOWED_ORIGINS` | Sites a browser may call the API from, comma separated | thermalpaperlabels.com, www., localhost |
| `ALLOWED_ORIGIN_REGEX` | Pattern for preview sites | `https://roll-ready-custom*.vercel.app` |
| `INQUIRY_RATE_LIMIT`, `INQUIRY_RATE_WINDOW` | Enquiries allowed per visitor, per seconds | 5 per 600 |
| `GMAIL_SENDER`, `GMAIL_APP_PASSWORD`, `NOTIFY_EMAIL` | Enquiry email | unset: no email |
| `SQL_ECHO` | `1` logs every SQL query (local debugging only; it logs customer details) | off |

## Endpoints

- `GET /products`, `GET /products/{id or slug}`: public.
- `POST /products`, `PATCH /products/{id or slug}`, `DELETE /products/{id or slug}`: need `X-Admin-Key`.
- `POST /inquiries`: public, rate limited, field lengths checked.
- `GET /stats`, `GET /health`.

## Local run and tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
uvicorn backend.main:app --reload --port 8000
python -m pytest -q tests
python -m backend.scripts.seed_products   # local SQLite only; refuses a real database without --force-production
```
