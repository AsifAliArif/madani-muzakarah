#!/usr/bin/env python3
"""Upload OAuth credentials from local Secret keys/oauth.json to VPS .env"""
import json
import re
import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
OAUTH_FILE = ROOT / "Secret keys" / "oauth.json"
SECRETS = (ROOT / "Secret keys" / "Github & VPS Access.txt").read_text()
vps_pass = [l.split(":", 1)[1].strip() for l in SECRETS.splitlines() if l.startswith("Root password:")][0]

if not OAUTH_FILE.exists():
    print("Missing Secret keys/oauth.json with client_id and client_secret")
    sys.exit(1)

data = json.loads(OAUTH_FILE.read_text())
client_id = data["client_id"]
client_secret = data["client_secret"]
APP = "/var/www/madani-muzakarah/backend"

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password=vps_pass, timeout=30)
_, o, _ = c.exec_command(f"cat {APP}/.env")
text = o.read().decode()
text = re.sub(r"GOOGLE_CLIENT_ID=.*", f"GOOGLE_CLIENT_ID={client_id}", text)
text = re.sub(r"GOOGLE_CLIENT_SECRET=.*", f"GOOGLE_CLIENT_SECRET={client_secret}", text)
sftp = c.open_sftp()
with sftp.file(f"{APP}/.env", "w") as f:
    f.write(text)
sftp.close()
c.exec_command("systemctl restart madani-fastapi")
print("OAuth credentials applied")
c.close()
