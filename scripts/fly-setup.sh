#!/usr/bin/env bash
set -e

if ! command -v flyctl >/dev/null 2>&1; then
  echo "flyctl not found. Install from https://fly.io/docs/hands-on/installing/"
  exit 1
fi

APP_NAME=${1:-}
if [ -z "$APP_NAME" ]; then
  read -p "Fly app name (leave empty to auto-generate): " APP_NAME
fi

echo "Launching Fly app..."
if [ -n "$APP_NAME" ]; then
  flyctl apps create "$APP_NAME" || true
  flyctl init --name "$APP_NAME" || true
else
  flyctl launch --no-deploy || true
fi

echo "Setting secrets..."
if [ -n "$DATABASE_URL" ]; then
  flyctl secrets set DATABASE_URL="$DATABASE_URL"
fi
if [ -n "$DJANGO_SECRET_KEY" ]; then
  flyctl secrets set DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY"
fi
if [ -n "$SUPABASE_URL" ]; then
  flyctl secrets set SUPABASE_URL="$SUPABASE_URL"
fi
if [ -n "$SUPABASE_KEY" ]; then
  flyctl secrets set SUPABASE_KEY="$SUPABASE_KEY"
fi

echo "Deploying..."
flyctl deploy

echo "Done. Remember to set any other secrets (AWS_* or storage parameters) if needed."
