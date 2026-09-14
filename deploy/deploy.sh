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

mkdir -p "${APP_DIR}" "${APP_DIR}/data" "${APP_DIR}/media"
mkdir -p /var/www/certbot 2>/dev/null || true
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
    "sessionId": "d4a8e9",
    "hypothesisId": os.environ.get("AGENT_DBG_HID"),
    "location": "deploy/deploy.sh",
    "message": os.environ.get("AGENT_DBG_MSG"),
    "data": data,
    "timestamp": int(time.time() * 1000),
    "runId": os.environ.get("DEPLOY_SHA", "unknown"),
}
line = json.dumps(payload)
print(line, flush=True)
for path in (
    "/home/unique/Documents/projects/production/irAbs174/.cursor/debug-d4a8e9.log",
    "/tmp/debug-d4a8e9.log",
):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as fh:
            fh.write(line + "\n")
    except Exception:
        pass
req = urllib.request.Request(
    "http://127.0.0.1:7651/ingest/e4b0b26a-9ef5-4ce1-9790-8c950143cea0",
    data=line.encode(),
    headers={"Content-Type": "application/json", "X-Debug-Session-Id": "d4a8e9"},
    method="POST",
)
try:
    urllib.request.urlopen(req, timeout=1)
except Exception:
    pass
PY
}
_on_err() {
  _agent_log "script failed" "B" "{\"line\":$1}"
}
trap '_on_err ${LINENO}' ERR
export P="$(curl -sS -o /dev/null -w "http=%{http_code} time=%{time_total} ip=%{remote_ip}" --max-time 8 https://pypi.org/simple/pip/ 2>&1 || true)"
export A="$(curl -sS -o /dev/null -w "http=%{http_code} time=%{time_total} ip=%{remote_ip}" --max-time 8 https://mirrors.aliyun.com/pypi/simple/pip/ 2>&1 || true)"
export W="$(find "${APP_DIR}/wheels" -maxdepth 1 -name '*.whl' 2>/dev/null | wc -l | tr -d ' ')"
export I="${PIP_INDEX_URL:-unset}"
export V="${APP_DIR}/.venv"
_agent_log "pre-pip diagnostics" "B" "$(python3 -c 'import json,os; print(json.dumps({"pypi":os.environ.get("P"),"aliyun":os.environ.get("A"),"wheels":os.environ.get("W"),"pip_index_url":os.environ.get("I"),"venv":os.environ.get("V")}))')"
# #endregion

export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_INDEX_URL="${PIP_INDEX_URL:-https://mirrors.aliyun.com/pypi/simple/}"
export PIP_TRUSTED_HOST="${PIP_TRUSTED_HOST:-mirrors.aliyun.com}"
VENV_PIP="${APP_DIR}/.venv/bin/pip"
WHEELS_DIR="${APP_DIR}/wheels"

# #region agent log
_agent_log "pip install start" "B" "$(python3 -c 'import json,os; print(json.dumps({"pip_index_url":os.environ.get("PIP_INDEX_URL"),"trusted_host":os.environ.get("PIP_TRUSTED_HOST")}))')"
# #endregion
"${APP_DIR}/.venv/bin/pip" install --upgrade pip
"${APP_DIR}/.venv/bin/pip" install -r "${APP_DIR}/requirements.txt"
export D="$("${APP_DIR}/.venv/bin/python" -c "import django; print(django.get_version())" 2>&1 || true)"
# #region agent log
_agent_log "pip install done" "B" "$(python3 -c 'import json,os; print(json.dumps({"django":os.environ.get("D"),"pip_index_url":os.environ.get("PIP_INDEX_URL")}))')"
# #endregion

if grep -q 'DJANGO_SECRET_KEY=change-me' "${APP_DIR}/.env" 2>/dev/null; then
  KEY="$("${APP_DIR}/.venv/bin/python" -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")"
  sed -i "s/DJANGO_SECRET_KEY=change-me/DJANGO_SECRET_KEY=${KEY}/" "${APP_DIR}/.env"
fi

# #region agent log
_agent_log "about to migrate" "B" "$(python3 -c 'import json,os; print(json.dumps({"django":os.environ.get("D","")}))')"
# #endregion

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
