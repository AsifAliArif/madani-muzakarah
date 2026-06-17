import paramiko, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)

install = """
if ! command -v gcloud >/dev/null; then
  curl -sSL https://sdk.cloud.google.com | bash -s -- --disable-prompts --install-dir=/opt
  ln -sf /opt/google-cloud-sdk/bin/gcloud /usr/local/bin/gcloud
fi
gcloud --version | head -1
"""
print(run := c.exec_command(install)[1].read().decode())

# Start gcloud auth in background with no browser
auth_cmd = """
nohup bash -c 'echo | gcloud auth login --no-launch-browser asifaliarif2526@gmail.com 2>&1 | tee /tmp/gcloud_auth.log' &
sleep 3
cat /tmp/gcloud_auth.log
"""
_, o, _ = c.exec_command(auth_cmd, timeout=30)
print(o.read().decode())
c.close()
