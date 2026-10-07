#!/usr/bin/env sh
# Розгортання на чистому VPS (Ubuntu/Debian): sh install.sh
set -e
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi
cd "$(dirname "$0")"
[ -f .env ] || { cp .env.example .env; echo "Заповніть deploy/.env (DOMAIN, ADMIN_TOKEN, ключі Binance) і запустіть знову"; exit 1; }
docker compose up -d --build
echo "Готово. Біржа: https://$(grep ^DOMAIN= .env | cut -d= -f2)  адмінка: /admin.html"
