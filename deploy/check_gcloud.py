import paramiko, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)
for cmd in [
    "which gcloud; gcloud --version 2>/dev/null | head -1",
    "cat /tmp/gcloud_auth.log 2>/dev/null | tail -20",
    "ps aux | grep gcloud | grep -v grep",
]:
    print("===", cmd)
    _, o, _ = c.exec_command(cmd, timeout=30)
    print(o.read().decode())
c.close()
