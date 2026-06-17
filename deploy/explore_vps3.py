import paramiko
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)

cmds = [
    "ps aux | grep -E 'streamlit|python|uvicorn' | grep -v grep",
    "find / -maxdepth 5 -type d -name 'streamlit*' 2>/dev/null | head -10",
    "find /home /opt /srv /root -maxdepth 4 -name '*.py' 2>/dev/null | head -30",
    "grep -r 'client_id\\|GOOGLE\\|oauth' /home /opt /srv 2>/dev/null | head -20",
]

for cmd in cmds:
    print("===", cmd)
    _, o, _ = c.exec_command(cmd, timeout=120)
    print(o.read().decode("utf-8", errors="replace")[:5000])

c.close()
