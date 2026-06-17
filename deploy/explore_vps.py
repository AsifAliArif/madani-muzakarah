import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)

cmds = [
    "uname -a",
    "free -h",
    "which python3 node nginx cloudflared meilisearch 2>/dev/null; python3 --version; node --version 2>/dev/null || echo no-node",
    "ls -la /var/www 2>/dev/null || echo no-www",
    "grep -r GOOGLE_CLIENT /var/www /root 2>/dev/null | head -15 || true",
    "systemctl list-units --type=service --state=running 2>/dev/null | head -30",
    "ls -la /etc/cloudflared 2>/dev/null || echo no-cloudflared-config",
    "cat /root/.cloudflared/*.json 2>/dev/null | head -5 || true",
]

for cmd in cmds:
    print("===", cmd[:100])
    _, o, e = c.exec_command(cmd, timeout=60)
    print(o.read().decode()[:3000])
    err = e.read().decode()
    if err:
        print("ERR", err[:300])

c.close()
