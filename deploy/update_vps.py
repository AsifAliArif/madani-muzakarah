#!/usr/bin/env python3
"""Pull latest code on VPS, rebuild frontend, restart services."""
from __future__ import annotations

import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / "Secret keys"
VPS_HOST = "177.7.47.167"
VPS_user = "root"
APP_DIR = "/var/www/madani-muzakarah"


def read_vps_password() -> str:
    text = (SECRETS / "Github & VPS Access.txt").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("Root password:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("VPS password not found")


def run(client: paramiko.SSHClient, cmd: str, timeout: int = 900) -> tuple[int, str]:
    print(f"\n>>> {cmd[:200]}")
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    combined = (out + "\n" + err).strip()
    if combined:
        print(combined[-5000:])
    return code, combined


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    password = read_vps_password()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VPS_HOST, username=VPS_user, password=password, timeout=30)

    steps = f"""
set -e
cd {APP_DIR}

if [ -d .git ]; then
  git fetch origin
  git reset --hard origin/master
else
  echo "ERROR: {APP_DIR} is not a git repo"
  exit 1
fi

cd frontend
npm ci --silent 2>/dev/null || npm install --silent
npm run build

cd {APP_DIR}/backend
if [ -d venv ]; then
  ./venv/bin/pip install -q -r requirements.txt
fi

systemctl restart madani-meilisearch
systemctl restart madani-fastapi
systemctl restart nginx
systemctl restart cloudflared-muzakarah 2>/dev/null || true

sleep 2
echo "=== Service status ==="
systemctl is-active madani-fastapi madani-meilisearch nginx || true
curl -s http://127.0.0.1:8000/api/health || true
echo ""
echo "=== Deploy complete ==="
"""

    code, _ = run(client, steps, timeout=1200)
    client.close()
    return 0 if code == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
