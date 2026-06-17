import sys
import paramiko

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)

cmds = [
    "systemctl is-active nginx madani-fastapi madani-meilisearch",
    "ss -tlnp | grep -E ':80|:8000|:7700'",
    "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1/",
    "curl -s http://127.0.0.1/api/health",
    "cat /etc/nginx/sites-enabled/madani-muzakarah",
    "nginx -t 2>&1",
    "journalctl -u nginx -n 20 --no-pager",
    "journalctl -u madani-fastapi -n 15 --no-pager",
    "ps aux | grep cloudflared | grep -v grep",
]

for cmd in cmds:
    print("===", cmd)
    _, o, e = c.exec_command(cmd, timeout=30)
    print(o.read().decode("utf-8", errors="replace"))
    err = e.read().decode()
    if err:
        print("ERR", err)

c.close()
