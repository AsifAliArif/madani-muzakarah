import json
import sys
import paramiko

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)

_, o, _ = c.exec_command("cat /opt/fatawa-v2/secrets/google-service-account.json")
sa_text = o.read().decode()
sa = json.loads(sa_text)
print("project_id:", sa.get("project_id"))
print("client_email:", sa.get("client_email"))
print("has_private_key:", bool(sa.get("private_key")))

# Check for existing oauth client secrets in fatawa
_, o, _ = c.exec_command("grep -r 'client_id\\|client_secret\\|googleusercontent' /opt/fatawa-v2/secrets /opt/fatawa-v2/config 2>/dev/null | head -20")
print("grep:", o.read().decode()[:2000])

c.close()

# Save SA locally temp for API calls (in deploy folder, gitignored)
from pathlib import Path
p = Path(__file__).parent / ".sa_temp.json"
p.write_text(sa_text)
print("saved sa to", p)
