import paramiko, sys, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)
_, o, _ = c.exec_command("cat /opt/fatawa-v2/.env")
text = o.read().decode()
# Print only keys not values for security in logs, but capture oauth locally
keys = [line.split("=")[0] for line in text.splitlines() if "=" in line and not line.startswith("#")]
print("ENV keys:", keys)
for line in text.splitlines():
    if any(k in line.upper() for k in ["GOOGLE", "OAUTH", "CLIENT", "GOCSPX"]):
        print("MATCH:", line[:80] + ("..." if len(line)>80 else ""))
c.close()
