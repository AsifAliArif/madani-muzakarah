#!/bin/bash
set -euo pipefail

APP_DIR="/var/www/madani-muzakarah"
DOMAIN="${1:-}"

echo "==> Madani Muzakarah Deployment"

# System packages
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip nginx postgresql postgresql-contrib

# PostgreSQL
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='muzakarah'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE USER muzakarah WITH PASSWORD 'muzakarah';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='muzakarah_db'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE DATABASE muzakarah_db OWNER muzakarah;"

# Meilisearch
if ! command -v meilisearch &>/dev/null; then
  curl -L https://install.meilisearch.com | sh
  sudo mv meilisearch /usr/local/bin/
fi
sudo mkdir -p /var/lib/meilisearch
sudo chown www-data:www-data /var/lib/meilisearch

# cloudflared
if ! command -v cloudflared &>/dev/null; then
  curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
  chmod +x cloudflared
  sudo mv cloudflared /usr/local/bin/
fi

# Backend
cd "$APP_DIR/backend"
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
if [ -f .env ]; then
  ./venv/bin/alembic upgrade head || true
fi

# Frontend
cd "$APP_DIR/frontend"
npm ci
npm run build

# Nginx
sudo cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/madani-muzakarah
sudo ln -sf /etc/nginx/sites-available/madani-muzakarah /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Systemd
sudo cp "$APP_DIR/deploy/systemd/"*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable madani-fastapi madani-meilisearch nginx
sudo systemctl restart madani-fastapi madani-meilisearch nginx

echo "==> Deployment complete!"
echo "Next: Configure Cloudflare tunnel and Google OAuth redirect URIs"
if [ -n "$DOMAIN" ]; then
  echo "Domain: https://$DOMAIN"
fi
