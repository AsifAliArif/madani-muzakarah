#!/usr/bin/env python3
"""Upload latest code to VPS, rebuild frontend, restart services."""
from __future__ import annotations

import sys
import tarfile
import tempfile
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / "Secret keys"
VPS_HOST = "177.7.47.167"
VPS_user = "root"
APP_DIR = "/var/www/madani-muzakarah"
EXCLUDE_DIRS = {"venv", "node_modules", "Secret keys", ".git", "__pycache__", "dist"}
EXCLUDE_FILES = {".env"}


def read_vps_password() -> str:
    text = (SECRETS / "Github & VPS Access.txt").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("Root password:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("VPS password not found")


def make_tarball() -> Path:
    tmp = Path(tempfile.gettempdir()) / "madani-muzakarah-update.tar.gz"
    with tarfile.open(tmp, "w:gz") as tar:
        for path in ROOT.rglob("*"):
            if any(part in EXCLUDE_DIRS for part in path.parts):
                continue
            if path.name in EXCLUDE_FILES:
                continue
            if path.is_file():
                arc = path.relative_to(ROOT)
                tar.add(path, arcname=str(arc).replace("\\", "/"))
    return tmp


def run(client: paramiko.SSHClient, cmd: str, timeout: int = 1200) -> tuple[int, str]:
    print(f"\n>>> {cmd[:200]}")
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    combined = (out + "\n" + err).strip()
    if combined:
        print(combined[-6000:])
    return code, combined


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    password = read_vps_password()

    print("Creating tarball...")
    tarball = make_tarball()
    print(f"Tarball: {tarball} ({tarball.stat().st_size // 1024} KB)")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VPS_HOST, username=VPS_user, password=password, timeout=30)

    sftp = client.open_sftp()
    print("Uploading...")
    sftp.put(str(tarball), "/tmp/madani-muzakarah-update.tar.gz")
    sftp.close()
    tarball.unlink(missing_ok=True)

    backend_env = (Path(APP_DIR) / "backend" / ".env").as_posix()
    steps = f"""
set -e
mkdir -p {APP_DIR}
ENV_FILE="{backend_env}"
if [ -f "$ENV_FILE" ]; then cp "$ENV_FILE" /tmp/madani-env-backup; fi
cd {APP_DIR}
tar -xzf /tmp/madani-muzakarah-update.tar.gz
rm -f /tmp/madani-muzakarah-update.tar.gz
if [ -f /tmp/madani-env-backup ]; then cp /tmp/madani-env-backup "$ENV_FILE"; rm -f /tmp/madani-env-backup; fi

cd {APP_DIR}/frontend
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
