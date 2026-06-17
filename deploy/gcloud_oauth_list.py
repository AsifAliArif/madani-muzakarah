import paramiko, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)

cmds = [
    "gcloud auth activate-service-account --key-file=/opt/fatawa-v2/secrets/google-service-account.json 2>&1",
    "gcloud config set project first-project-492120 2>&1",
    "gcloud iam oauth-clients list --location=global 2>&1 | head -20",
    "gcloud alpha iap oauth-brands list --project=first-project-492120 2>&1",
    "gcloud services list --enabled --project=first-project-492120 2>&1 | grep -i oauth",
]
for cmd in cmds:
    print("===", cmd[:100])
    _, o, e = c.exec_command(cmd, timeout=60)
    print((o.read() + e.read()).decode("utf-8", errors="replace")[:2500])
c.close()
