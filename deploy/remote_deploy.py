#!/usr/bin/env python3
"""Remote VPS deployment script."""
import os
import secrets
import sys
import time
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / "Secret keys"

VPS_HOST = "177.7.47.167"
VPS_USER = "root"
APP_DIR = "/var/www/madani-muzakarah"


def read_secrets():
    gh_file = SECRETS / "Github & VPS Access.txt"
    api_file = SECRETS / "Api Key.txt"
    text = gh_file.read_text(encoding="utf-8")
    vps_pass = ""
    gh_token = ""
    for line in text.splitlines():
        if line.startswith("Root password:"):
            vps_pass = line.split(":", 1)[1].strip()
        if line.startswith("GitHub token:"):
            gh_token = line.split(":", 1)[1].strip()
    gemini_key = api_file.read_text(encoding="utf-8").strip()
    return vps_pass, gh_token, gemini_key


def ssh_connect(password: str) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VPS_HOST, username=VPS_USER, password=password, timeout=30)
    return client


def run(client, cmd: str, timeout=600) -> tuple[int, str, str]:
    print(f"\n>>> {cmd[:120]}...")
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    if out:
        print(out[-3000:] if len(out) > 3000 else out)
    if err and code != 0:
        print("STDERR:", err[-2000:])
    return code, out, err


def upload_tree(sftp, local: Path, remote: str, exclude: set):
  def _skip(p: Path) -> bool:
    parts = set(p.parts)
    if "venv" in parts or "node_modules" in parts or "Secret keys" in parts:
      return True
    if p.name in exclude:
      return True
    return False

  for item in local.rglob("*"):
    if _skip(item):
      continue
    rel = item.relative_to(local)
    rpath = f"{remote}/{rel.as_posix()}"
    if item.is_dir():
      try:
        sftp.stat(rpath)
      except OSError:
        sftp.mkdir(rpath)
    else:
      parent = "/".join(rpath.split("/")[:-1])
      try:
        sftp.stat(parent)
      except OSError:
        run_ssh_mkdir(sftp, parent)
      sftp.put(str(item), rpath)


def run_ssh_mkdir(sftp, path: str):
    parts = path.strip("/").split("/")
    cur = ""
    for p in parts:
        cur += "/" + p
        try:
            sftp.stat(cur)
        except OSError:
            sftp.mkdir(cur)


def main():
    vps_pass, gh_token, gemini_key = read_secrets()
    secret_key = secrets.token_urlsafe(48)
    from cryptography.fernet import Fernet
    enc_key = Fernet.generate_key().decode()

    client = ssh_connect(vps_pass)
    sftp = client.open_sftp()

    run(client, f"mkdir -p {APP_DIR}")

    print("Uploading project files...")
    upload_tree(sftp, ROOT, APP_DIR, exclude={".git", "__pycache__", ".env"})
    sftp.close()

    # Check for existing Google OAuth on server
    code, out, _ = run(client, "find /var/www /root /home -maxdepth 4 -name '.env' 2>/dev/null | head -20")
    run(client, "grep -r 'GOOGLE_CLIENT_ID' /var/www /root 2>/dev/null | head -5 || true")

    # Install deps
    bootstrap = f"""
set -e
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq git nginx postgresql postgresql-contrib curl ca-certificates python3-venv python3-pip

# Node.js 20
if ! command -v node &>/dev/null; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y -qq nodejs
fi

# Meilisearch
if ! command -v meilisearch &>/dev/null; then
  curl -L https://install.meilisearch.com | sh
  mv meilisearch /usr/local/bin/ 2>/dev/null || cp meilisearch /usr/local/bin/
fi
mkdir -p /var/lib/meilisearch
chown www-data:www-data /var/lib/meilisearch 2>/dev/null || true

# cloudflared
if ! command -v cloudflared &>/dev/null; then
  curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
  chmod +x /usr/local/bin/cloudflared
fi

# PostgreSQL
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='muzakarah'" | grep -q 1 || \\
  sudo -u postgres psql -c "CREATE USER muzakarah WITH PASSWORD 'muzakarah';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='muzakarah_db'" | grep -q 1 || \\
  sudo -u postgres psql -c "CREATE DATABASE muzakarah_db OWNER muzakarah;"

echo "Bootstrap done"
"""
    run(client, bootstrap, timeout=900)

    client.close()
    print("Phase 1 complete")


if __name__ == "__main__":
    main()
