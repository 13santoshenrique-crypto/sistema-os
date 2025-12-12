#!/usr/bin/env bash
set -e

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is not installed. Please install and authenticate first." >&2
  exit 1
fi

usage() {
  echo "Usage: $0 [--repo owner/repo] [--env .env.file]" >&2
  exit 1
}

REPO=""
ENV_FILE=".env"
while [ $# -gt 0 ]; do
  case "$1" in
    --repo)
      REPO="$2"; shift 2;;
    --env)
      ENV_FILE="$2"; shift 2;;
    -h|--help)
      usage;;
    *)
      usage;;
  esac
done

if [ -z "$REPO" ]; then
  REPO=$(git remote get-url origin 2>/dev/null | sed -E 's#.*github.com[:/](.*)\.git#\1#') || true
fi
if [ -z "$REPO" ]; then
  echo "Could not determine repo. Pass it as --repo owner/repo" >&2
  exit 1
fi

echo "Using repo: $REPO"

if [ -f "$ENV_FILE" ]; then
  echo "Loading environment variables from $ENV_FILE"
  # shellcheck disable=SC1090
  set -a
  . "$ENV_FILE"
  set +a
fi

SECRETS=(FLY_API_TOKEN DATABASE_URL DJANGO_SECRET_KEY SUPABASE_URL SUPABASE_KEY AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_STORAGE_BUCKET_NAME AWS_S3_ENDPOINT_URL)
for s in "${SECRETS[@]}"; do
  val=${!s}
  if [ -n "$val" ]; then
    echo "Setting secret $s..."
    printf "%s" "$val" | gh secret set "$s" -R "$REPO" || true
  else
    echo "Skipping $s (empty)"
  fi
done

echo "Secrets set for $REPO"
