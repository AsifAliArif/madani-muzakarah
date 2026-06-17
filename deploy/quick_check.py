import paramiko, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
c = paramiko.SSHClient()
c.set_missing_file_key_policy = None
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)
for cmd in [
    "which gcloud; gcloud --version 2>/dev/null | head -1",
    "ls -la /root/.config/gcloud 2>/dev/null | head -5",
    "find /opt/fatawa-v2 -maxdepth 2 -name '*.json' 2>/dev/null | head -10",
    "grep -r 'apps.googleusercontent' /opt/fatawa-v2/config /opt/fatawa-v2/.env /opt/fatawa-v2/*.env 2>/dev/null | head -5",
]:
    print("===", cmd)
    _, o, _ = c.exec_command(cmd, timeout=30)
    print(o.read().decode("utf-8", errors="replace")[:2000])
c.close()
