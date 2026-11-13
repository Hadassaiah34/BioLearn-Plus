# BioLearn Plus API

REST API with SQLite persistence, student registration/login, administrator role, lesson CRUD/import, learner progress and quiz-attempt recording.

## Run locally
1. `cd backend`
2. `python -m venv .venv` then activate it
3. `pip install -r requirements.txt`
4. Set environment variables using `.env.example` values (never use the sample passwords in deployment).
5. `uvicorn main:app --reload`
6. API docs: `/docs`; health: `/health`

## Admin bootstrap
Set `BIOLEARN_ADMIN_USERNAME` and `BIOLEARN_ADMIN_PASSWORD` before first launch. The admin is created once if the username does not exist. Set `BIOLEARN_SECRET` to a unique, long random value.

## API routes
- `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- `GET /lessons?grade=SS1&theme=...&q=...`, `GET /lessons/{id}`
- Admin bearer token: `POST /admin/lessons`, `PUT /admin/lessons/{id}`, `DELETE /admin/lessons/{id}`, `POST /admin/import`, `GET /admin/summary`
- Student bearer token: `POST /progress`, `GET /progress`, `POST /quiz-attempts`

SQLite is suitable for a small prototype/deployment with a persistent volume. For scaled production, use PostgreSQL, migrations, stronger account recovery/rate-limiting, HTTPS, audit logging, and managed secrets. This sample implements signed expiring bearer tokens and PBKDF2 password hashes; review security before handling real student data.
