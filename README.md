# django-backend-template

A batteries-included seed for **Django + Django REST Framework** backends. It
distills the common stack across my projects into one starting point — auth,
API docs, file storage, caching, background tasks, and a themed admin are all
wired up — plus a **code generator** that scaffolds a full REST API from a model
you write.

Mark this repo as a **GitHub template**, then click **Use this template** to
start each new project with everything already in place.

---

## Table of contents

1. [Features](#features)
2. [Tech stack](#tech-stack)
3. [Requirements](#requirements)
4. [Quick start](#quick-start)
5. [Project structure](#project-structure)
6. [Configuration — environment keys](#configuration--environment-keys)
7. [Optional integrations & graceful degradation](#optional-integrations--graceful-degradation)
8. [Defaults reference](#defaults-reference)
9. [Management commands](#management-commands)
10. [The scaffolding workflow](#the-scaffolding-workflow)
11. [User model & profile image](#user-model--profile-image)
12. [Authentication & API usage](#authentication--api-usage)
13. [File uploads & storage](#file-uploads--storage)
14. [API documentation](#api-documentation)
15. [Deployment](#deployment)
16. [Making this a GitHub template](#making-this-a-github-template)

---

## Features

- **Django 5 + DRF** with a clean `config/` + `apps/` layout and a single,
  conditional `settings.py`.
- **Custom user model** (`accounts.User`) extending `AbstractUser` — ready to
  edit per project, with `phone`, `display_name`, an uploaded `avatar`, and a
  `profile_image_url` link out of the box.
- **JWT authentication** (djangorestframework-simplejwt): register, login,
  refresh, logout (blacklist), and current-user endpoints, with refresh-token
  rotation.
- **Auto-generated OpenAPI docs** (drf-spectacular): Swagger UI + ReDoc.
- **Pagination, filtering, search, and ordering** enabled DRF-wide.
- **Code generator**: `newapp` + `setup_model` scaffold an app and a full
  CRUD API (serializer, viewset, router, admin, migrations) from your model.
- **Jazzmin** admin theme.
- **Neon / Postgres** via `DATABASE_URL` (Postgres required — no sqlite).
- **Optional, opt-in integrations**: Sentry, Backblaze B2 storage, Redis cache,
  Celery — each activates only when configured and no-ops otherwise.
- **Production hardening** (HSTS, secure cookies, SSL redirect) auto-enabled
  when `DEBUG=False`.
- WhiteNoise static serving, CORS, gunicorn, and a `Procfile`.

## Tech stack

| Area | Choice |
|---|---|
| Framework | Django 5.2, DRF 3.16 |
| Auth | JWT (simplejwt) |
| Docs | drf-spectacular (OpenAPI 3) |
| Admin | Jazzmin |
| DB | Postgres (Neon) via `dj-database-url` — required, no sqlite |
| Files | Local, or Backblaze B2 via django-storages (S3 API) |
| Cache | Local-memory, or Redis via django-redis |
| Tasks | Celery (optional) |
| Errors | Sentry (optional) |
| Static | WhiteNoise |
| Server | gunicorn |

## Requirements

- Python 3.11+ (3.12 recommended)
- pip / venv
- A Postgres/Neon `DATABASE_URL` — **required in every environment** (no sqlite fallback; use a Neon branch for local dev)

---

## Quick start

```bash
# 1. After "Use this template" on GitHub, clone your new repo, then:
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure. Copy the example and set SECRET_KEY and DATABASE_URL
#    (your Postgres/Neon URL) — both are required. A Neon branch works for
#    local dev. Other keys are optional.
cp .env.example .env

# 3. Create the database schema and an admin user.
python manage.py migrate
python manage.py createsuperuser

# 4. Run.
python manage.py runserver
```

Then open:

- Swagger UI → <http://127.0.0.1:8000/api/docs/>
- ReDoc → <http://127.0.0.1:8000/api/docs/redoc/>
- Admin → <http://127.0.0.1:8000/admin/>
- Login → `POST http://127.0.0.1:8000/api/v1/auth/login/` with `{username, password}`

---

## Project structure

```
config/
  settings.py     single, env-driven settings with conditional optional blocks
  urls.py         routes + auto-discovery of scaffolded app routers
  celery.py       optional Celery app (safe if Celery/Redis absent)
  wsgi.py/asgi.py
apps/
  core/
    models.py             TimeStampedModel base class
    pagination.py         StandardPagination (envelope + page_size control)
    permissions.py        reusable permission classes
    storage.py            storage helpers (work with local or B2)
    sentry.py             safe capture helpers (no-op when Sentry off)
    scaffold.py           helpers shared by the generators
    management/commands/
      newapp.py            create + register a new local app
      setup_model.py       generate serializer/viewset/router/admin from a model
  accounts/
    models.py             custom User
    serializers.py        register / login / user serializers
    views.py              JWT auth endpoints
    urls.py               /api/v1/auth/*
    admin.py
manage.py
requirements.txt
Procfile
.env.example
```

New apps you create with `newapp` land under `apps/` and are auto-mounted under
`/api/v1/` — you never edit `config/urls.py`.

---

## Configuration — environment keys

All configuration is via environment variables, loaded from `.env` in
development. Copy `.env.example` to `.env` and set what you need. **Every key is
optional except `SECRET_KEY` in production** — the backend boots on defaults.

### Core

| Key | Required | Default | Notes |
|---|---|---|---|
| `SECRET_KEY` | **Yes (prod)** | insecure dev key | Long random string. Generate with `python -c "import secrets;print(secrets.token_urlsafe(50))"`. |
| `DEBUG` | No | `True` | Set `False` in production (enables security hardening). |
| `ALLOWED_HOSTS` | No | `*` (dev) | Comma-separated hostnames in prod, e.g. `api.example.com`. |
| `CSRF_TRUSTED_ORIGINS` | No | empty | Comma-separated, e.g. `https://app.example.com`. |
| `USE_X_FORWARDED_PROTO` | No | `True` in prod | Trust `X-Forwarded-Proto` behind a proxy/load balancer. |
| `LANGUAGE_CODE` | No | `en-us` | |
| `TIME_ZONE` | No | `UTC` | |
| `LOG_LEVEL` | No | `INFO` | Root logger level. |

### Database

| Key | Required | Default | Notes |
|---|---|---|---|
| `DATABASE_URL` | **Yes** | — | Postgres/Neon URL, e.g. `postgres://user:pass@host/db?sslmode=require`. The app won't start without it. **No sqlite fallback.** |
| `DB_CONN_MAX_AGE` | No | `600` | Persistent connection lifetime (seconds). |
| `DB_SSL_REQUIRE` | No | `False` | Force SSL to the DB. |

### Auth / JWT

| Key | Required | Default | Notes |
|---|---|---|---|
| `ACCESS_TOKEN_LIFETIME_MINUTES` | No | `60` | Access token TTL. |
| `REFRESH_TOKEN_LIFETIME_DAYS` | No | `30` | Refresh token TTL. Refresh rotates and old tokens are blacklisted. |

### CORS

| Key | Required | Default | Notes |
|---|---|---|---|
| `CORS_ALLOW_ALL_ORIGINS` | No | `True` in dev | Set `False` in prod and use the allow-list below. |
| `CORS_ALLOWED_ORIGINS` | No | empty | Comma-separated origins, e.g. `https://app.example.com,http://localhost:5173`. |
| `CORS_ALLOW_CREDENTIALS` | No | `True` | |

### Pagination & throttling

| Key | Required | Default | Notes |
|---|---|---|---|
| `PAGE_SIZE` | No | `30` | Default results per page (clients may override with `?page_size=`, capped at 100). |
| `THROTTLE_ANON` | No | `60/min` | Anonymous rate limit. |
| `THROTTLE_USER` | No | `240/min` | Authenticated rate limit. |

### API metadata (shown in Swagger)

| Key | Required | Default |
|---|---|---|
| `API_TITLE` | No | `Backend API` |
| `API_DESCRIPTION` | No | template blurb |
| `API_VERSION` | No | `1.0.0` |

### Admin branding

| Key | Default |
|---|---|
| `ADMIN_SITE_TITLE` | `Backend Admin` |
| `ADMIN_SITE_HEADER` | `Backend Admin` |
| `ADMIN_SITE_BRAND` | `Backend` |
| `ADMIN_WELCOME` | `Welcome` |
| `ADMIN_COPYRIGHT` | empty |
| `ADMIN_THEME` | `flatly` |

### Optional integration keys

**Sentry** (error tracking) — activates when `SENTRY_DSN` is set.

| Key | Default | How to obtain |
|---|---|---|
| `SENTRY_DSN` | empty | sentry.io → your project → Settings → Client Keys (DSN). |
| `SENTRY_ENVIRONMENT` | `production`/`development` | Logical env label. |
| `SENTRY_RELEASE` | empty | Optional release/version tag. |
| `SENTRY_TRACES_SAMPLE_RATE` | `0.1` | Performance-trace sampling (0–1). |
| `SENTRY_PROFILES_SAMPLE_RATE` | `0.1` | Profiling sampling (0–1). |
| `SENTRY_SEND_PII` | `False` | Send request/user PII to Sentry. |

**Backblaze B2** (file storage, S3-compatible) — activates when **all four** of
`B2_KEY_ID`, `B2_APPLICATION_KEY`, `B2_BUCKET_NAME`, `B2_ENDPOINT_URL` are set.

| Key | Default | How to obtain |
|---|---|---|
| `B2_KEY_ID` | empty | B2 console → Application Keys → keyID. |
| `B2_APPLICATION_KEY` | empty | The secret shown when you create the key (once). |
| `B2_BUCKET_NAME` | empty | B2 console → Buckets. |
| `B2_ENDPOINT_URL` | empty | Bucket's S3 endpoint, e.g. `https://s3.eu-central-003.backblazeb2.com`. |
| `B2_REGION` | empty | Region part of the endpoint, e.g. `eu-central-003`. |
| `B2_DEFAULT_ACL` | `public-read` | Set `private` for signed-URL-only access. |
| `B2_QUERYSTRING_AUTH` | `False` | `True` to sign every URL (needed for private buckets). |

**Redis** (cache) — activates when `REDIS_URL` is set.

| Key | Default | Notes |
|---|---|---|
| `REDIS_URL` | empty | e.g. `redis://default:pass@host:6379/0`. |
| `CACHE_TTL` | `86400` | Default cache entry lifetime (seconds). |

**Celery** (background tasks) — activates when a broker is available.

| Key | Default | Notes |
|---|---|---|
| `CELERY_BROKER_URL` | falls back to `REDIS_URL` | Broker/result backend. |
| `CELERY_TASK_ALWAYS_EAGER` | `False` | `True` runs tasks inline (handy in dev / no worker). |

### How to add keys

1. **Local dev:** put them in `.env` (git-ignored). Restart `runserver`.
2. **Production:** set them as real environment variables in your host's
   dashboard (Railway/Render/Fly/etc.) — do **not** commit `.env`.

---

## Optional integrations & graceful degradation

The whole point of this template: **the backend runs with none of the optional
services configured**, and each one turns on only when its keys are present.

| Integration | Enable with | If not configured |
|---|---|---|
| Sentry | `SENTRY_DSN` | Error tracking simply off. |
| Backblaze B2 | `B2_*` (all four) | Files saved to the local filesystem (`/media`). |
| Redis | `REDIS_URL` | In-memory cache; a Redis outage never returns a 500 (`IGNORE_EXCEPTIONS`). |
| Celery | `CELERY_BROKER_URL` or `REDIS_URL` | Tasks run eagerly / are skipped; nothing crashes. |

---

## Defaults reference

| Setting | Default |
|---|---|
| Access token lifetime | 60 minutes |
| Refresh token lifetime | 30 days (rotates, blacklists old) |
| Page size | 30 (max 100 via `?page_size=`) |
| Anon throttle | 60/min |
| User throttle | 240/min |
| Cache TTL | 86400 s (24 h) |
| DB connection max age | 600 s |
| Time zone | UTC |
| B2 ACL | public-read |
| Default storage | local filesystem (B2 when configured) |
| Default cache | local-memory (Redis when configured) |

Pagination response envelope:

```json
{
  "count": 128,
  "total_pages": 5,
  "current_page": 1,
  "page_size": 30,
  "next": "http://.../api/v1/products/?page=2",
  "previous": null,
  "results": [ /* ... */ ]
}
```

---

## Management commands

### Custom generators

#### `newapp` — create a new, fully-wired app

```bash
python manage.py newapp <name>
# example
python manage.py newapp catalog
```

Creates `apps/<name>/` (models, serializers, views, urls, admin — each with the
scaffold anchors), registers `apps.<name>` in `INSTALLED_APPS`, and — via URL
auto-discovery — mounts it under `/api/v1/`. No edits to `config/` required.

#### `setup_model` — generate a full CRUD API from a model

```bash
python manage.py setup_model <app> <Model> [--no-migrations]
# example
python manage.py setup_model catalog Product
```

Given a model you already wrote, it generates and wires:

- a `ModelSerializer` (auto read-only `id`/timestamps),
- a `ModelViewSet` (auth + pagination + search + ordering),
- a router registration → `/api/v1/<models>/`,
- an admin registration with sensible `list_display`, `search_fields`,
  `list_filter`,

then runs `makemigrations` (skip with `--no-migrations`).

It is **idempotent**: existing classes are left untouched, so re-running is
safe. Generated code is inserted at `# <scaffold:...>` anchors, so your
hand-written code coexists in the same files. Field lists are inferred from the
model — after adding fields, delete a generated block if you want it refreshed.

### Common Django / DRF commands

```bash
python manage.py migrate                 # apply migrations
python manage.py makemigrations          # create migrations after model changes
python manage.py createsuperuser         # make an admin user
python manage.py runserver               # dev server
python manage.py collectstatic --noinput # gather static for prod (WhiteNoise)
python manage.py spectacular --file schema.yml   # export the OpenAPI schema
python manage.py shell                   # interactive shell
python manage.py test                    # run tests
```

### Background worker (only if Celery configured)

```bash
celery -A config worker -l info
```

---

## The scaffolding workflow

End-to-end: from "I need a new resource" to a live, documented API.

```bash
# 1. Create the app
python manage.py newapp catalog
```

```python
# 2. Write your model in apps/catalog/models.py
from django.db import models
from apps.core.models import TimeStampedModel


class Product(TimeStampedModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.BooleanField(default=True)

    def __str__(self):
        return self.name
```

```bash
# 3. Generate the API + migrations, then apply
python manage.py setup_model catalog Product
python manage.py migrate
```

You now have, with zero edits to `config/`:

- `GET/POST /api/v1/products/` and `GET/PUT/PATCH/DELETE /api/v1/products/{id}/`
- Pagination, `?search=`, and `?ordering=` support
- The model registered in the admin
- Full Swagger/ReDoc documentation for the new endpoints

Add another model to the same app and run `setup_model catalog <Other>` again —
the generator appends, never overwrites.

---

## User model & profile image

The custom user lives in `apps/accounts/models.py` and extends `AbstractUser`
(username-based login). Out of the box it adds:

| Field | Type | Purpose |
|---|---|---|
| `phone` | CharField | Optional phone number (indexed). |
| `display_name` | CharField | Friendly name. |
| `avatar` | ImageField | **Uploaded** profile image (goes to B2 when configured, else local). |
| `profile_image_url` | URLField | **External** profile image link (e.g. an OAuth/CDN avatar). |
| `updated_at` | DateTime | Auto-updated timestamp. |

### Setting the profile image

Two independent options — use either or both:

- **External link** — set `profile_image_url` (a string URL). Best when the
  image already lives on a CDN or comes from a social login.
- **Uploaded file** — send a file to `avatar` (multipart). The template stores
  it locally by default, or on Backblaze B2 once the `B2_*` keys are set.

Both are exposed on the user serializer, so they're available on
`GET/PATCH /api/v1/auth/me/` and returned in the login response. See examples
below.

### Customizing the user

Edit `apps/accounts/models.py` freely — add columns, add a custom manager, or
switch `USERNAME_FIELD` to `email`/`phone`. `AUTH_USER_MODEL` already points
here, so changes are cheap. After editing, run
`python manage.py makemigrations accounts && python manage.py migrate`.

---

## Authentication & API usage

All auth endpoints are under `/api/v1/auth/`.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/auth/register/` | Create an account |
| POST | `/api/v1/auth/login/` | Get access + refresh tokens (and the user) |
| POST | `/api/v1/auth/refresh/` | Exchange a refresh token for a new access token |
| POST | `/api/v1/auth/logout/` | Blacklist a refresh token |
| GET/PATCH | `/api/v1/auth/me/` | Read or update the current user |

### Register

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"hamza","email":"h@example.com","password":"supersecret",
       "display_name":"Hamza","profile_image_url":"https://cdn.example.com/me.png"}'
```

### Login

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"hamza","password":"supersecret"}'
# → {"access":"<jwt>","refresh":"<jwt>","user":{...}}
```

### Authenticated request

```bash
curl http://127.0.0.1:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer <access>"
```

### Update the profile image (external link)

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer <access>" \
  -H "Content-Type: application/json" \
  -d '{"profile_image_url":"https://cdn.example.com/new.png"}'
```

### Upload an avatar file

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer <access>" \
  -F "avatar=@/path/to/photo.jpg"
```

### Refresh / logout

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh/ \
  -H "Content-Type: application/json" -d '{"refresh":"<refresh>"}'

curl -X POST http://127.0.0.1:8000/api/v1/auth/logout/ \
  -H "Authorization: Bearer <access>" \
  -H "Content-Type: application/json" -d '{"refresh":"<refresh>"}'
```

---

## File uploads & storage

`avatar` and any `ImageField`/`FileField` on your scaffolded models use Django's
default storage:

- **No B2 configured** → files are written to `/media` and served locally in
  development.
- **B2 configured** (`B2_*` keys) → files are transparently uploaded to
  Backblaze B2 over the S3 API, with clean public URLs (`AWS_QUERYSTRING_AUTH`
  off by default).

Helpers in `apps/core/storage.py` (`save_bytes`, `file_url`, `delete_file`,
`presigned_url`) work against whichever backend is active, so your code doesn't
change between local and B2.

---

## API documentation

Powered by drf-spectacular and always in sync with your code:

- Swagger UI → `/api/docs/`
- ReDoc → `/api/docs/redoc/`
- Raw OpenAPI schema → `/api/schema/`

Every scaffolded endpoint is documented automatically. Export the schema for
client codegen with `python manage.py spectacular --file schema.yml`.

---

## Deployment

1. Set real environment variables on your host (never commit `.env`):
   `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `DATABASE_URL` (Neon), plus any
   optional keys you use.
2. With `DEBUG=False`, security hardening turns on automatically (SSL redirect,
   HSTS, secure cookies).
3. The `Procfile` provides:
   - `web` → `gunicorn config.wsgi`
   - `release` → `python manage.py migrate` (run on deploy)
   - `worker` → `celery -A config worker` (only if you use Celery)
4. Static files are handled by WhiteNoise; run `collectstatic` in your build.

---

## Making this a GitHub template

Push the repo, then on GitHub:
**Settings → General → check "Template repository."**
After that, **Use this template → Create a new repository** seeds a fresh
project from this seed.

```bash
git branch -M main
git remote add origin git@github.com:<you>/django-backend-template.git
git push -u origin main
```

---

## License

Released under the [MIT License](LICENSE) © 2026 Hamza Sabri. You're free to
use, modify, and distribute it with attribution.
