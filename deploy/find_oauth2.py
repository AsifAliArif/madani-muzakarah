import paramiko, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("177.7.47.167", username="root", password="5Tb8.JBB.v9ZG.n", timeout=30)
cmds = [
    "find /opt/fatawa-v2 -name 'secrets.toml' -o -name '.env' -o -name 'oauth*.json' 2>/dev/null | head -20",
    "grep -r 'GOCSPX\\|googleusercontent.com' /opt/fatawa-v2 --include='*.toml' --include='*.env' --include='*.yaml' --include='*.json' 2>/dev/null | grep -v service-account | head -15",
    "cat /opt/fatawa/.streamlit/secrets.toml 2>/dev/null | head -30",
    "cat /opt/fatawa-v2/.streamlit/secrets.toml 2>/dev/null | head -30",
]
for cmd in cmds:
    print("===", cmd[:90])
    _, o, _ = c.exec_command(cmd, timeout=45)
    print(o.read().decode("utf-8", errors="replace")[:2500])
c.close()
