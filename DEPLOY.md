# Deploy to Fly.io (quickstart)

This project is configured to be deployed to Fly.io using `Dockerfile`.

1) Create a Supabase project (or any Postgres) and copy the `DATABASE_URL`.

2) Create a Fly app and provide the needed secrets:

```bash
flyctl auth login
flyctl launch --image "" --name sistema-os
flyctl secrets set DATABASE_URL="postgres://..." DJANGO_SECRET_KEY="secret" DEBUG=False
flyctl deploy
```

3) Run migrations and collect static (via flyctl ssh):

```bash
flyctl ssh console --command "python manage.py migrate"
flyctl ssh console --command "python manage.py collectstatic --noinput"
```

4) Optional: configure `SUPABASE` storage for uploads and set credentials via `flyctl secrets set`.

GitHub Actions is configured to run tests and `flyctl deploy` on pushes to `main`.
