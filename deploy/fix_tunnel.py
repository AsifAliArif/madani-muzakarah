import sys
import paramiko

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)

run = lambda cmd: c.exec_command(cmd)[1].read().decode("utf-8", errors="replace")

# Persistent cloudflared via systemd
script = """
pkill -f 'cloudflared tunnel --url' 2>/dev/null || true
sleep 1
systemctl enable cloudflared-muzakarah
systemctl restart cloudflared-muzakarah
sleep 8
grep -o 'https://[a-z0-9-]*\\.trycloudflare\\.com' /var/log/cloudflared-muzakarah.log | tail -1
"""
print(run(script))

# Ensure cloudflared log path in systemd
fix = """
mkdir -p /var/log
touch /var/log/cloudflared-muzakarah.log
chmod 644 /var/log/cloudflared-muzakarah.log
systemctl restart cloudflared-muzakarah
sleep 10
grep -o 'https://[a-z0-9-]*\\.trycloudflare\\.com' /var/log/cloudflared-muzakarah.log | tail -1
curl -s http://127.0.0.1/api/health
"""
print(run(fix))
c.close()
