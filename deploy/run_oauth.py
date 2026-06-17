import paramiko
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)

script = open(r"d:\Muzakara Content Database\madani-muzakarah\deploy\create_oauth.py", encoding="utf-8").read()
sftp = c.open_sftp()
with sftp.file("/tmp/create_oauth.py", "w") as f:
    f.write(script)
sftp.close()

_, o, e = c.exec_command(f"/var/www/madani-muzakarah/backend/venv/bin/python /tmp/create_oauth.py", timeout=120)
print(o.read().decode("utf-8", errors="replace"))
print(e.read().decode("utf-8", errors="replace"))

_, o, _ = c.exec_command("cat /tmp/oauth_result.json 2>/dev/null; systemctl restart madani-fastapi")
print(o.read().decode())

c.close()
