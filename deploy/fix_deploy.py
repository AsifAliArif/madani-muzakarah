import json
import re
import sys
import time

import paramiko

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)

APP = "/var/www/madani-muzakarah"


def run(cmd, t=120):
    print(">>>", cmd[:120])
    _, o, e = c.exec_command(cmd, timeout=t)
    out = o.read().decode("utf-8", errors="replace")
    err = e.read().decode("utf-8", errors="replace")
    code = o.channel.recv_exit_status()
    text = (out + err).strip()
    if text:
        print(text[-3000:])
    return code, text


# Fix meilisearch - binary path
run("which meilisearch; ls -la /usr/local/bin/meilisearch 2>/dev/null")
run("""
cat > /etc/systemd/system/madani-meilisearch.service << 'EOF'
[Unit]
Description=Meilisearch for Madani Muzakarah
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/meilisearch --db-path /var/lib/meilisearch --master-key masterKey --http-addr 127.0.0.1:7700
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl restart madani-meilisearch
sleep 2
systemctl status madani-meilisearch --no-pager | head -15
""")

# Fix fastapi www-data user - may not have access, use root
run("""
sed -i 's/User=www-data/User=root/' /etc/systemd/system/madani-fastapi.service
systemctl daemon-reload
systemctl restart madani-fastapi
sleep 2
systemctl is-active madani-fastapi
curl -s http://127.0.0.1:8000/api/health
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1/
""")

# Cloudflared tunnel
run("systemctl stop cloudflared-muzakarah 2>/dev/null; pkill cloudflared 2>/dev/null; sleep 1; true")
run("rm -f /var/log/cloudflared-muzakarah.log")
run("nohup /usr/local/bin/cloudflared tunnel --no-autoupdate --url http://127.0.0.1:80 > /var/log/cloudflared-muzakarah.log 2>&1 &")

tunnel_url = ""
for i in range(15):
    time.sleep(2)
    _, out = run("cat /var/log/cloudflared-muzakarah.log 2>/dev/null | tail -30")
    m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", out)
    if m:
        tunnel_url = m.group(0)
        break

print(f"\nTUNNEL: {tunnel_url}")

if tunnel_url:
    cb = f"{tunnel_url}/api/auth/callback"
    run(f"""
python3 << 'PY'
from pathlib import Path
p = Path('{APP}/backend/.env')
text = p.read_text()
text = text.replace('GOOGLE_REDIRECT_URI=PLACEHOLDER', 'GOOGLE_REDIRECT_URI={cb}')
text = text.replace('FRONTEND_URL=PLACEHOLDER', 'FRONTEND_URL={tunnel_url}')
text = text.replace('CORS_ORIGINS=PLACEHOLDER', 'CORS_ORIGINS={tunnel_url}')
p.write_text(text)
print('env updated')
PY
systemctl restart madani-fastapi
""")

    result = {"tunnel_url": tunnel_url, "callback": cb}
    Path(__file__).parent.joinpath("deployment_result.json").write_text(json.dumps(result, indent=2))

c.close()
