#!/bin/sh
# macOS: подвійний клік у Finder. Linux: sh start-beta.command
cd "$(dirname "$0")"
if ! command -v node >/dev/null 2>&1; then
  echo "Node.js не встановлено. Завантажте LTS-версію з https://nodejs.org і запустіть знову."
  exit 1
fi
exec node beta.js
