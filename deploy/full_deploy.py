#!/usr/bin/env python3
"""Full end-to-end VPS deployment."""
from __future__ import annotations

import base64
import json
import os
import secrets
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

import paramiko
from cryptography.fernet import Fernet

ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / "Secret keys"
VPS_HOST = "177.7.47.167"
VPS_USER = "root"
APP_DIR = "/var/www/madani-muzakarah"

EXCLUDE_DIRS = {"venv", "node_modules", "Secret keys", ".git", "__pycache__", "dist"}
EXCLUDE_FILES = {".env"}


def read_secrets():
    text = (SECRETS / "Github & VPS Access.txt").read_text(encoding="utf-8")
    vps_pass = gh_token = ""
    for line in text.splitlines():
        if line.startswith("Root password:"):
            vps_pass = line.split(":", 1)[1].strip()
        if line.startswith("GitHub token:"):
            gh_token = line.split(":", 1)[1].strip()
    gemini = (SECRETS / "Api Key.txt").read_text(encoding="utf-8").strip()
    return vps_pass, gh_token, gemini


def make_tarball() -> Path:
    tmp = Path(tempfile.gettempdir()) / "madani-muzakarah-deploy.tar.gz"
    with tarfile.open(tmp, "w:gz") as tar:
        for path in ROOT.rglob("*"):
            if any(part in EXCLUDE_DIRS for part in path.parts):
                continue
            if path.name in EXCLUDE_FILES:
                continue
            if path.is_file():
                arc = path.relative_to(ROOT.parent)
                tar.add(path, arcname=str(arc).replace("\\", "/"))
    return tmp


def run_remote(client, cmd: str, timeout=1200) -> tuple[int, str]:
    print(f"\n>>> {cmd[:150]}")
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    combined = (out + "\n" + err).strip()
    if combined:
        print(combined[-4000:])
    return code, combined


def encrypt_key(plain: str, secret_key: str) -> str:
    derived = __import__("hashlib").sha256(secret_key.encode()).digest()
    key = base64.urlsafe_b64encode(derived)
    return Fernet(key).encrypt(plain.encode()).decode()


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    vps_pass, gh_token, gemini_key = read_secrets()
    secret_key = secrets.token_urlsafe(48)
    enc_key = Fernet.generate_key().decode()

    print("Creating tarball...")
    tarball = make_tarball()
    print(f"Tarball: {tarball} ({tarball.stat().st_size // 1024} KB)")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VPS_HOST, username=VPS_USER, password=vps_pass, timeout=30)
    sftp = client.open_sftp()

    run_remote(client, f"mkdir -p {APP_DIR}")
    print("Uploading...")
    sftp.put(str(tarball), "/tmp/madani-muzakarah.tar.gz")
    sftp.close()

    gemini_enc = encrypt_key(gemini_key, secret_key)

    # Phase 1: install system packages
    run_remote(client, """
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq git nginx postgresql postgresql-contrib curl ca-certificates python3-venv python3-pip rsync

if ! command -v node >/dev/null; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y -qq nodejs
fi

if ! command -v meilisearch >/dev/null; then
  curl -L https://install.meilisearch.com | sh
  install -m 755 meilisearch /usr/local/bin/meilisearch
  rm -f meilisearch
fi
mkdir -p /var/lib/meilisearch
chown www-data:www-data /var/lib/meilisearch 2>/dev/null || true

if ! command -v cloudflared >/dev/null; then
  curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
  chmod +x /usr/local/bin/cloudflared
fi
""", timeout=900)

    # Extract app
    run_remote(client, f"""
cd /var/www
tar -xzf /tmp/madani-muzakarah.tar.gz
rm -f /tmp/madani-muzakarah.tar.gz
ls -la {APP_DIR}
""")

    # PostgreSQL
    run_remote(client, """
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='muzakarah'" | grep -q 1 || \\
  sudo -u postgres psql -c "CREATE USER muzakarah WITH PASSWORD 'muzakarah';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='muzakarah_db'" | grep -q 1 || \\
  sudo -u postgres psql -c "CREATE DATABASE muzakarah_db OWNER muzakarah;"
""")

    # Write .env placeholder - OAuth filled after tunnel URL known
    env_content = f"""DATABASE_URL=postgresql+psycopg://muzakarah:muzakarah@localhost:5432/muzakarah_db
SECRET_KEY={secret_key}
ENCRYPTION_KEY={enc_key}
GOOGLE_CLIENT_ID=PLACEHOLDER
GOOGLE_CLIENT_SECRET=PLACEHOLDER
GOOGLE_REDIRECT_URI=PLACEHOLDER
FRONTEND_URL=PLACEHOLDER
ADMIN_EMAIL=asifaliarif2526@gmail.com
MEILISEARCH_URL=http://127.0.0.1:7700
MEILISEARCH_API_KEY=masterKey
CORS_ORIGINS=PLACEHOLDER
GEMINI_KEY_ENCRYPTED={gemini_enc}
"""
    run_remote(client, f"cat > {APP_DIR}/backend/.env << 'ENVEOF'\n{env_content}ENVEOF")

    # Backend setup
    run_remote(client, f"""
cd {APP_DIR}/backend
python3 -m venv venv
./venv/bin/pip install -q -r requirements.txt
./venv/bin/python -c "from app.main import app; print('import ok')"
""", timeout=600)

    # Frontend build
    run_remote(client, f"""
cd {APP_DIR}/frontend
npm ci --silent 2>/dev/null || npm install --silent
npm run build
""", timeout=900)

    # Nginx
    run_remote(client, f"""
cp {APP_DIR}/deploy/nginx.conf /etc/nginx/sites-available/madani-muzakarah
ln -sf /etc/nginx/sites-available/madani-muzakarah /etc/nginx/sites-enabled/madani-muzakarah
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl enable nginx && systemctl restart nginx
""")

    # Systemd services
    run_remote(client, f"""
cp {APP_DIR}/deploy/systemd/madani-fastapi.service /etc/systemd/system/
cp {APP_DIR}/deploy/systemd/madani-meilisearch.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable madani-fastapi madani-meilisearch
systemctl restart madani-meilisearch
systemctl restart madani-fastapi
sleep 2
systemctl is-active madani-fastapi madani-meilisearch nginx
curl -s http://127.0.0.1:8000/api/health || true
""")

    # Start cloudflared quick tunnel and capture URL
    run_remote(client, """
pkill -f 'cloudflared tunnel --url' 2>/dev/null || true
nohup cloudflared tunnel --no-autoupdate --url http://127.0.0.1:80 > /var/log/cloudflared-muzakarah.log 2>&1 &
sleep 8
grep -o 'https://[a-z0-9-]*\\.trycloudflare\\.com' /var/log/cloudflared-muzakarah.log | head -1
""")

    code, out = run_remote(client, "grep -o 'https://[a-z0-9-]*\\.trycloudflare\\.com' /var/log/cloudflared-muzakarah.log | head -1")
    tunnel_url = ""
    for line in out.splitlines():
        if "trycloudflare.com" in line:
            tunnel_url = line.strip()
            break

    print(f"\nTUNNEL URL: {tunnel_url}")

    if tunnel_url:
        callback = f"{tunnel_url}/api/auth/callback"
        run_remote(client, f"""
sed -i 's|GOOGLE_CLIENT_ID=.*|GOOGLE_CLIENT_ID=PLACEHOLDER|' {APP_DIR}/backend/.env
sed -i 's|GOOGLE_REDIRECT_URI=.*|GOOGLE_REDIRECT_URI={callback}|' {APP_DIR}/backend/.env
sed -i 's|FRONTEND_URL=.*|FRONTEND_URL={tunnel_url}|' {APP_DIR}/backend/.env
sed -i 's|CORS_ORIGINS=.*|CORS_ORIGINS={tunnel_url}|' {APP_DIR}/backend/.env
""")

        # Bootstrap AI settings in DB
        run_remote(client, f"""
cat > {APP_DIR}/backend/bootstrap_ai.py << 'PYEOF'
from app.database import SessionLocal, engine, Base
from app.models.ai_settings import AISettings
from app.auth.security import encrypt_value
import os
Base.metadata.create_all(bind=engine)
db = SessionLocal()
s = db.query(AISettings).first()
if not s:
    s = AISettings()
    db.add(s)
key = os.environ.get("GEMINI_KEY", "")
s.llm_name = "gemini-1.5-flash"
if key:
    s.api_key_encrypted = encrypt_value(key)
db.commit()
print("AI bootstrapped")
PYEOF
cd {APP_DIR}/backend && GEMINI_KEY='{gemini_key}' ./venv/bin/python bootstrap_ai.py
""")

    # Cloudflared systemd for persistence
    run_remote(client, """
cat > /etc/systemd/system/cloudflared-muzakarah.service << 'EOF'
[Unit]
Description=Cloudflare Quick Tunnel for Madani Muzakarah
After=network.target nginx.service

[Service]
Type=simple
ExecStart=/usr/local/bin/cloudflared tunnel --no-autoupdate --url http://127.0.0.1:80
Restart=always
RestartSec=5
StandardOutput=append:/var/log/cloudflared-muzakarah.log
StandardError=append:/var/log/cloudflared-muzakarah.log

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable cloudflared-muzakarah
""")

  # Save tunnel URL locally for OAuth setup
    result_file = ROOT / "deploy" / "deployment_result.json"
    result_file.write_text(json.dumps({"tunnel_url": tunnel_url, "callback": f"{tunnel_url}/api/auth/callback" if tunnel_url else ""}, indent=2))

    client.close()
    print("\nDeployment phase complete.")
    print(f"Tunnel: {tunnel_url}")
    return tunnel_url


if __name__ == "__main__":
    main()
