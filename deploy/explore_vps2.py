import paramiko
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)

cmds = [
    "ls -la /root",
    "find /root -maxdepth 3 -type f -name '*.env' 2>/dev/null",
    "find /root -maxdepth 4 -type f \\( -name '.env' -o -name 'credentials.json' -o -name 'client_secret*.json' \\) 2>/dev/null",
    "docker ps 2>/dev/null || echo no-docker",
    "ss -tlnp | head -20",
    "which nginx cloudflared 2>/dev/null || true",
]

for cmd in cmds:
    print("===", cmd)
    _, o, e = c.exec_command(cmd, timeout=60)
    print(o.read().decode("utf-8", errors="replace")[:4000])

c.close()
