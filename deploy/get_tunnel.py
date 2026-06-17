import re
import sys
import paramiko

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)

_, o, _ = c.exec_command("grep -o 'https://[a-z0-9-]*\\.trycloudflare\\.com' /var/log/cloudflared-muzakarah.log | head -1")
url = o.read().decode().strip()
print("URL:", url)

if not url:
    _, o, _ = c.exec_command("cat /var/log/cloudflared-muzakarah.log | grep -i trycloudflare")
    print(o.read().decode())

if url:
    cb = f"{url}/api/auth/callback"
    cmd = f"""
python3 -c "
from pathlib import Path
p = Path('/var/www/madani-muzakarah/backend/.env')
t = p.read_text()
t = t.replace('GOOGLE_REDIRECT_URI=PLACEHOLDER', 'GOOGLE_REDIRECT_URI={cb}')
t = t.replace('FRONTEND_URL=PLACEHOLDER', 'FRONTEND_URL={url}')
t = t.replace('CORS_ORIGINS=PLACEHOLDER', 'CORS_ORIGINS={url}')
p.write_text(t)
print('done')
"
systemctl restart madani-fastapi
curl -s {url}/api/health
"""
    _, o, e = c.exec_command(cmd)
    print(o.read().decode())
    print(e.read().decode())

    import json
    from pathlib import Path
    Path(__file__).parent.joinpath("deployment_result.json").write_text(
        json.dumps({"tunnel_url": url, "callback": cb}, indent=2)
    )

c.close()
