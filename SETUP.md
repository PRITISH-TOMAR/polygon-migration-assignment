# Local Setup

How to get the Polygon Migration Tool running on your own machine, in order.

We need **Python 3.8+**, **Docker Desktop** (for PostgreSQL and Redis) / Docker in linux, **Git**.

---

## 1. Pull the code

```bash
git clone https://github.com/PRITISH-TOMAR/polygon-migration-assignment
cd polygon-migration-assignment
git checkout main
```

If you have SSH keys set up on GitHub, you can clone over SSH instead:

```bash
git clone git@github.com:PRITISH-TOMAR/polygon-migration-assignment.git
```

Work on `main` — it has the storage factory and the migration fixes. The other
branches (`original-starter`, `original-with-migration`, `feature/aws-s3-storage`,
`fix/upload-before-delete`) are kept for comparison.

Two folder levels are easy to mix up:

```
polygon-migration-assignment/      <- repo root, requirement.txt lives here
└── PolygonMigration/              <- Django project, manage.py and .env live here
```

---

## 2. Create a virtual environment

From the **repo root**:

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Your prompt should now start with `(venv)`. Keep it active for every step below.

---

## 3. Install dependencies

```bash
pip install -r requirement.txt
```

Note the filename — it's `requirement.txt`, singular, and it sits in the repo
root, not inside `PolygonMigration/`.

---

## 4. Start PostgreSQL and Redis with Docker

The compose file reads its values from `.env`, so create that first:

```bash
cd PolygonMigration
cp .env.example .env        # Windows: copy .env.example .env
```

Then bring the containers up **from the `PolygonMigration/` folder**, next to
`.env`:

```bash
docker compose up -d
```

That gives you `postgres:15` on port 5432 and `redis:7` on port 6379, with the
database stored in a named volume so it survives restarts. Check they're healthy:

```bash
docker compose ps
```

Useful later: `docker compose stop` to pause, `docker compose down` to remove the
containers, `docker compose down -v` to also wipe the database.

If port 5432 or 6379 is already taken on your machine, change `DB_PORT` or
`REDIS_PORT` in `.env` — compose and Django both read them from there.

---

## 5. Fill in the environment variables

Open `PolygonMigration/.env`. The defaults copied from `.env.example` already
match the Docker containers, so you mainly need to add a Django secret key, your
Polygon credentials, and one storage provider.

**Django:**

```env
SECRET_KEY=paste-a-generated-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

Generate the key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Database and Redis** — leave as copied if you're using Docker:

```env
DB_NAME=polygon_migration
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_SSL=False
```

**Polygon API** — get these from Polygon itself: log in to
<https://polygon.codeforces.com/>, open Settings, find the API section and
generate a key.

```env
POLYGON_API_KEY=your-polygon-api-key
POLYGON_API_SECRET=your-polygon-api-secret
```

Django **will not start** without both of these — `settings.py` raises an error
on purpose rather than letting you run half-configured.

**Cloud storage** — pick one provider and fill in only its block.

For AWS S3:

```env
STORAGE_PROVIDER=s3
AWS_S3_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

For Azure Blob Storage:

```env
STORAGE_PROVIDER=azure
AZURE_STORAGE_ACCOUNT_URL=https://youraccount.blob.core.windows.net
AZURE_CONTAINER_NAME=testcases
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_USERNAME=your-azure-username
AZURE_PASSWORD=your-azure-password
```

---

## 6. Run migrations, create a superuser, start the server

All three from inside `PolygonMigration/`, with the venv active and Docker
running:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

A note on `createsuperuser`: this project uses a custom user model that logs in
by **email**, and it asks for a handful of extra fields (first name, last name,
username, contact number, college, graduation year, gender). Answer them all —
you'll log in with the email and password.

---

## 7. Open it

- App: <http://localhost:8000/>
- Admin panel: <http://localhost:8000/admin>

---
