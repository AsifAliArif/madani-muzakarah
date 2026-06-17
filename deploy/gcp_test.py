import paramiko, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)

script = r'''
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SA = "/opt/fatawa-v2/secrets/google-service-account.json"
creds = service_account.Credentials.from_service_account_file(
    SA, scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
creds.refresh(Request())
token = creds.token

import urllib.request
import urllib.error

def get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, r.read().decode()[:3000]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:2000]

for url in [
    "https://cloudresourcemanager.googleapis.com/v1/projects/first-project-492120",
    "https://iap.googleapis.com/v1/projects/first-project-492120/brands",
    "https://serviceusage.googleapis.com/v1/projects/first-project-492120/services?filter=state:ENABLED",
]:
    print("URL", url)
    print(get(url))
    print("---")
'''
sftp = c.open_sftp()
with sftp.file("/tmp/gcp_test.py", "w") as f:
    f.write(script)
sftp.close()
_, o, e = c.exec_command("/opt/fatawa-v2/venv/bin/python /tmp/gcp_test.py", timeout=60)
print(o.read().decode())
print(e.read().decode())
c.close()
