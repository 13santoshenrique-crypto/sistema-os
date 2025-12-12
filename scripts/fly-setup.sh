#!/usr/bin/env bash
set -e

if ! command -v flyctl >/dev/null 2>&1; then
  echo "flyctl not found. Install from https://fly.io/docs/hands-on/installing/"
  exit 1
fi

APP_NAME=""
while [ $# -gt 0 ]; do
  case "$1" in
    --app)
      APP_NAME="$2"; shift 2;;
    -h|--help)
      echo "Usage: $0 [--app app-name]"; exit 0;;
    *)
      echo "Unknown option: $1"; exit 1;;
  esac
done

echo "Launching Fly app..."
if [ -n "$APP_NAME" ]; then
  flyctl apps create "$APP_NAME" || true
  flyctl init --name "$APP_NAME" || true
else
  flyctl launch --no-deploy || true
fi

echo "Setting secrets..."
# Set common secrets if present in environment
if [ -n "$DATABASE_URL" ]; then
  flyctl secrets set DATABASE_URL="$DATABASE_URL" --app ${APP_NAME:-$(flyctl info --format json 2>/dev/null | jq -r .Name || echo '')} || true
fi
if [ -n "$DJANGO_SECRET_KEY" ]; then
  flyctl secrets set DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" --app ${APP_NAME:-$(flyctl info --format json 2>/dev/null | jq -r .Name || echo '')} || true
fi
if [ -n "$SUPABASE_URL" ]; then
  flyctl secrets set SUPABASE_URL="$SUPABASE_URL" --app ${APP_NAME:-$(flyctl info --format json 2>/dev/null | jq -r .Name || echo '')} || true
fi
if [ -n "$SUPABASE_KEY" ]; then
  flyctl secrets set SUPABASE_KEY="$SUPABASE_KEY" --app ${APP_NAME:-$(flyctl info --format json 2>/dev/null | jq -r .Name || echo '')} || true
fi

echo "Deploying..."
flyctl deploy --app ${APP_NAME:-} || true

echo "Done. Remember to set any other secrets (AWS_* or storage parameters) if needed."
