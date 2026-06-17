import paramiko, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)
_, o, _ = c.exec_command("grep -r 'ADMIN_TOKEN\\|admin.token' /opt/fatawa-v2 --include='*.py' | head -5")
print(o.read().decode()[:1500])
c.close()
