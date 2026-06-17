import paramiko
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)
cmds = [
    "grep -r 'GOOGLE_CLIENT\\|client_secret\\|oauth.*google\\|GOCSPX' /opt/fatawa /opt/fatawa-v2 2>/dev/null | head -30",
    "find /opt -name 'client_secret*.json' -o -name 'google*credentials*' 2>/dev/null",
    "grep -r 'apps.googleusercontent.com' /opt 2>/dev/null | head -10",
]
for cmd in cmds:
    print("===", cmd[:80])
    _, o, _ = c.exec_command(cmd, timeout=60)
    print(o.read().decode("utf-8", errors="replace")[:3000])
c.close()
