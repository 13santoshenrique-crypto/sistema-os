#!/usr/bin/env bash
set -e

echo "Validating environment for deploy..."

check() {
  var="$1"; name="$2"; if [ -n "${!var}" ]; then echo "OK: $name set"; else echo "MISSING: $name"; fi
}

check GITHUB_TOKEN "GitHub token/GITHUB_TOKEN"
check FLY_API_TOKEN "Fly API token/FLY_API_TOKEN"
check DATABASE_URL "Database URL/DATABASE_URL"
check DJANGO_SECRET_KEY "Django secret/DJANGO_SECRET_KEY"

if command -v gh >/dev/null 2>&1; then
  echo "gh installed, checking auth status..."
  gh auth status || true
else
  echo "gh not installed"
fi

if command -v flyctl >/dev/null 2>&1; then
  echo "flyctl installed, checking auth status..."
  flyctl auth whoami || true
else
  echo "flyctl not installed"
fi

echo "Validate: run scripts/setup-github-secrets.sh --repo owner/repo --env .env.deploy and then scripts/fly-setup.sh --app myapp"
