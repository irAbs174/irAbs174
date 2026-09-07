#!/usr/bin/env bash
# Deploy static site for damerchi.ir only.
# Safe: never touches other /var/www/* or other nginx site configs.
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/damerchi.ir}"
STAGE_DIR="${STAGE_DIR:-/tmp/damerchi-ci}"
RELEASE_ARCHIVE="${RELEASE_ARCHIVE:-${STAGE_DIR}/damerchi-release.tar.gz}"
NGINX_AVAILABLE="/etc/nginx/sites-available/damerchi.ir.conf"
NGINX_ENABLED="/etc/nginx/sites-enabled/damerchi.ir.conf"

if [[ ! -f "${RELEASE_ARCHIVE}" ]]; then
  echo "ERROR: release archive not found: ${RELEASE_ARCHIVE}" >&2
  exit 1
fi

mkdir -p "${APP_DIR}" /var/www/certbot
TMP_EXTRACT="$(mktemp -d /tmp/damerchi-extract.XXXXXX)"
trap 'rm -rf "${TMP_EXTRACT}"' EXIT

tar -xzf "${RELEASE_ARCHIVE}" -C "${TMP_EXTRACT}"

# Sync only this site's web root (no --delete outside APP_DIR)
rsync -a --delete \
  --exclude '.git/' \
  --exclude '.github/' \
  --exclude 'deploy/' \
  --exclude 'social_networks.txt' \
  --exclude 'README.md' \
  --exclude '_config.yml' \
  "${TMP_EXTRACT}/" "${APP_DIR}/"

# Install/refresh nginx vhost for damerchi.ir only when present in release
if [[ -f "${TMP_EXTRACT}/deploy/nginx/damerchi.ir.conf" ]]; then
  # Prefer HTTPS template if cert already exists
  if [[ -f /etc/letsencrypt/live/damerchi.ir/fullchain.pem ]]; then
    if [[ -f "${TMP_EXTRACT}/deploy/nginx/damerchi.ir.ssl.conf" ]]; then
      install -m 0644 "${TMP_EXTRACT}/deploy/nginx/damerchi.ir.ssl.conf" "${NGINX_AVAILABLE}"
    else
      install -m 0644 "${TMP_EXTRACT}/deploy/nginx/damerchi.ir.conf" "${NGINX_AVAILABLE}"
    fi
  else
    install -m 0644 "${TMP_EXTRACT}/deploy/nginx/damerchi.ir.conf" "${NGINX_AVAILABLE}"
  fi
  ln -sfn "${NGINX_AVAILABLE}" "${NGINX_ENABLED}"
fi

nginx -t
systemctl reload nginx

echo "Deployed damerchi.ir from ${DEPLOY_SHA:-unknown} to ${APP_DIR}"
