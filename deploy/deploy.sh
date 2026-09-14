#!/usr/bin/env bash
# Deploy Django app for damerchi.ir only.
# Safe: never touches other /var/www/* or other nginx site configs.
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/damerchi.ir}"
STAGE_DIR="${STAGE_DIR:-/tmp/damerchi-ci}"
RELEASE_ARCHIVE="${RELEASE_ARCHIVE:-${STAGE_DIR}/damerchi-release.tar.gz}"
NGINX_AVAILABLE="/etc/nginx/sites-available/damerchi.ir.conf"
NGINX_ENABLED="/etc/nginx/sites-enabled/damerchi.ir.conf"
SERVICE_UNIT="/etc/systemd/system/damerchi.service"

if [[ ! -f "${RELEASE_ARCHIVE}" ]]; then
  echo "ERROR: release archive not found: ${RELEASE_ARCHIVE}" >&2
  exit 1
fi

mkdir -p "${APP_DIR}" /var/www/certbot "${APP_DIR}/data" "${APP_DIR}/media"
TMP_EXTRACT="$(mktemp -d /tmp/damerchi-extract.XXXXXX)"
trap 'rm -rf "${TMP_EXTRACT}"' EXIT

tar -xzf "${RELEASE_ARCHIVE}" -C "${TMP_EXTRACT}"

rsync -a --delete \
  --exclude '.git/' \
  --exclude '.github/' \
  --exclude '.venv/' \
  --exclude 'data/' \
  --exclude 'media/' \
  --exclude 'staticfiles/' \
  --exclude '.env' \
  --exclude 'social_networks.txt' \
  --exclude 'README.md' \
  --exclude '_config.yml' \
  "${TMP_EXTRACT}/" "${APP_DIR}/"

if [[ ! -f "${APP_DIR}/.env" ]]; then
  if [[ -f "${APP_DIR}/.env.example" ]]; then
    cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
    sed -i 's/DJANGO_DEBUG=true/DJANGO_DEBUG=false/' "${APP_DIR}/.env" || true
  fi
fi

if [[ ! -d "${APP_DIR}/.venv" ]]; then
  python3 -m venv "${APP_DIR}/.venv"
fi

# #region agent log
_agent_log() {
  AGENT_DBG_MSG="$1" AGENT_DBG_HID="$2" AGENT_DBG_DATA="${3:-{}}" python3 - <<'PY' || true
import json, os, time, urllib.request
try:
    data = json.loads(os.environ.get("AGENT_DBG_DATA") or "{}")
except Exception:
    data = {"raw": os.environ.get("AGENT_DBG_DATA")}
payload = {
    "sessionId": "6b9f74",
    "hypothesisId": os.environ.get("AGENT_DBG_HID"),
    "location": "deploy/deploy.sh:pip",
    "message": os.environ.get("AGENT_DBG_MSG"),
    "data": data,
    "timestamp": int(time.time() * 1000),
    "runId": os.environ.get("DEPLOY_SHA", "unknown"),
}
line = json.dumps(payload)
print(line)
try:
    with open("/home/unique/Documents/projects/production/irAbs174/.cursor/debug-6b9f74.log", "a") as fh:
        fh.write(line + "\n")
except Exception:
    pass
req = urllib.request.Request(
    "http://127.0.0.1:7651/ingest/e4b0b26a-9ef5-4ce1-9790-8c950143cea0",
    data=line.encode(),
    headers={"Content-Type": "application/json", "X-Debug-Session-Id": "6b9f74"},
    method="POST",
)
try:
    urllib.request.urlopen(req, timeout=1)
except Exception:
    pass
PY
}
_pypi_probe="$(curl -sS -o /dev/null -w "http=%{http_code} time=%{time_total} ip=%{remote_ip}" --max-time 15 https://pypi.org/simple/pip/ 2>&1 || true)"
_pypi_dns="$(getent ahosts pypi.org 2>/dev/null | awk '{print $1}' | head -n 8 | tr '\n' ' ' || true)"
_wheel_count="$(find "${APP_DIR}/wheels" -maxdepth 1 -name '*.whl' 2>/dev/null | wc -l | tr -d ' ')"
_agent_log "pre-pip diagnostics" "A" "$(printf '%s' "{\"pypi_probe\":$(python3 -c 'import json,os; print(json.dumps(os.environ["P"]))' 2>/dev/null || echo '""')}")"
# #endregion

export PIP_DISABLE_PIP_VERSION_CHECK=1
VENV_PIP="${APP_DIR}/.venv/bin/pip"
WHEELS_DIR="${APP_DIR}/wheels"

if grep -q 'DJANGO_SECRET_KEY=change-me' "${APP_DIR}/.env" 2>/dev/null; then
  KEY="$("${APP_DIR}/.venv/bin/python" -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")"
  sed -i "s/DJANGO_SECRET_KEY=change-me/DJANGO_SECRET_KEY=${KEY}/" "${APP_DIR}/.env"
fi

"${APP_DIR}/.venv/bin/python" "${APP_DIR}/manage.py" migrate --noinput
"${APP_DIR}/.venv/bin/python" "${APP_DIR}/manage.py" compilemessages || true
"${APP_DIR}/.venv/bin/python" "${APP_DIR}/manage.py" collectstatic --noinput
"${APP_DIR}/.venv/bin/python" "${APP_DIR}/manage.py" seed_portfolio

chown -R www-data:www-data "${APP_DIR}/data" "${APP_DIR}/media" "${APP_DIR}/staticfiles" "${APP_DIR}/.venv"
if [[ -f "${APP_DIR}/.env" ]]; then
  chown www-data:www-data "${APP_DIR}/.env"
  chmod 640 "${APP_DIR}/.env"
fi

if [[ -f "${APP_DIR}/deploy/gunicorn/damerchi.service" ]]; then
  install -m 0644 "${APP_DIR}/deploy/gunicorn/damerchi.service" "${SERVICE_UNIT}"
  systemctl daemon-reload
  systemctl enable damerchi.service
  systemctl restart damerchi.service
fi

if [[ -f "${TMP_EXTRACT}/deploy/nginx/damerchi.ir.conf" ]]; then
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
