#!/usr/bin/env sh
# =============================================================================
# django-backend-template installer
#
#   curl -fsSL https://raw.githubusercontent.com/hamza-sabri/django-backend-template/main/install.sh | sh
#   curl -fsSL https://raw.githubusercontent.com/hamza-sabri/django-backend-template/main/install.sh | sh -s my-api
#
# Downloads the template into a new folder (default: ./my-backend) with a fresh
# git history. No GitHub account or `gh` CLI required — just curl + tar.
# =============================================================================
set -e

TARBALL="https://github.com/hamza-sabri/django-backend-template/archive/refs/heads/main.tar.gz"
NAME="${1:-my-backend}"

if [ -e "$NAME" ]; then
  echo "✗ ./$NAME already exists. Pick another name:  ... | sh -s <name>"
  exit 1
fi

command -v curl >/dev/null 2>&1 || { echo "✗ curl is required."; exit 1; }
command -v tar  >/dev/null 2>&1 || { echo "✗ tar is required."; exit 1; }

echo "▶ Downloading django-backend-template into ./$NAME ..."
tmp="$(mktemp -d)"
curl -fsSL "$TARBALL" | tar -xz -C "$tmp"
mv "$tmp"/django-backend-template-* "$NAME"
rm -rf "$tmp"

cd "$NAME"
rm -rf .git
git init -q >/dev/null 2>&1 || true

cat <<EOF

✓ Created ./$NAME from django-backend-template

Next:
  cd $NAME
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  python manage.py init        # writes .env (+ a local Postgres if you skip -d)
  python manage.py migrate && python manage.py runserver
EOF
