#!/usr/bin/env bash
set -e

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is not installed. Please install and authenticate first." >&2
  exit 1
fi

REPO=${1:-$(git remote get-url origin | sed -E 's#.*github.com[:/](.*)\.git#\1#')} 
if [ -z "$REPO" ]; then
  echo "Could not determine repo. Pass it as the first argument: owner/repo" >&2
  exit 1
fi

echo "Using repo: $REPO"

SECRETS=(FLY_API_TOKEN DATABASE_URL DJANGO_SECRET_KEY SUPABASE_URL SUPABASE_KEY AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_STORAGE_BUCKET_NAME AWS_S3_ENDPOINT_URL)
for s in "${SECRETS[@]}"; do
  val=${!s}
  if [ -n "$val" ]; then
    echo "Setting secret $s..."
    echo -n "$val" | gh secret set "$s" -R "$REPO"
  fi
done

echo "Secrets set for $REPO"
