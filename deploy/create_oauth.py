#!/usr/bin/env python3
import json
import sys

SA_PATH = "/opt/fatawa-v2/secrets/google-service-account.json"
PROJECT = "first-project-492120"
TUNNEL = "https://eyes-hearing-scientific-halloween.trycloudflare.com"
CALLBACK = f"{TUNNEL}/api/auth/callback"
APP_DIR = "/var/www/madani-muzakarah/backend"


def creds():
    from google.oauth2 import service_account
    return service_account.Credentials.from_service_account_file(
        SA_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )


def enable_api(service_name):
    from googleapiclient.discovery import build
    su = build("serviceusage", "v1", credentials=creds(), cache_discovery=False)
    name = f"projects/{PROJECT}/services/{service_name}"
    try:
        su.services().enable(name=name).execute()
        print(f"Enabled {service_name}")
    except Exception as e:
        print(f"Enable {service_name}:", e)


def main():
    import subprocess
    subprocess.run([f"{APP_DIR}/venv/bin/pip", "install", "-q", "google-auth", "google-api-python-client"], check=True)

    enable_api("iap.googleapis.com")
    enable_api("oauth2.googleapis.com")

    from googleapiclient.discovery import build
    import time
    time.sleep(5)

    iap = build("iap", "v1", credentials=creds(), cache_discovery=False)
    parent = f"projects/{PROJECT}"

    brands = iap.projects().brands().list(parent=parent).execute()
    brand_list = brands.get("brands", [])
    print("Brands count:", len(brand_list))

    brand_name = brand_list[0]["name"] if brand_list else None
    if not brand_name:
        brand = iap.projects().brands().create(
            parent=parent,
            body={
                "applicationTitle": "Madani Muzakarah Database",
                "supportEmail": "asifaliarif2526@gmail.com",
            },
        ).execute()
        brand_name = brand["name"]
        print("Created brand:", brand_name)

    clients = iap.brands().identityAwareProxyClients().list(parent=brand_name).execute()
    client_list = clients.get("identityAwareProxyClients", [])

    oauth_client_id = client_secret = None
    for cl in client_list:
        if "muzakarah" in cl.get("displayName", "").lower():
            oauth_client_id = cl["name"].split("/")[-1]
            secret_resp = iap.brands().identityAwareProxyClients().getSecret(name=cl["name"]).execute()
            client_secret = secret_resp.get("secret")
            break

    if not oauth_client_id:
        new_client = iap.brands().identityAwareProxyClients().create(
            parent=brand_name,
            body={"displayName": "madani-muzakarah-web"},
        ).execute()
        oauth_client_id = new_client["name"].split("/")[-1]
        secret_resp = iap.brands().identityAwareProxyClients().getSecret(name=new_client["name"]).execute()
        client_secret = secret_resp.get("secret")

    full_client_id = f"{oauth_client_id}.apps.googleusercontent.com"
    print("CLIENT_ID:", full_client_id)

    from pathlib import Path
    import re
    env_path = Path(f"{APP_DIR}/.env")
    text = env_path.read_text()
    text = re.sub(r"GOOGLE_CLIENT_ID=.*", f"GOOGLE_CLIENT_ID={full_client_id}", text)
    text = re.sub(r"GOOGLE_CLIENT_SECRET=.*", f"GOOGLE_CLIENT_SECRET={client_secret}", text)
    env_path.write_text(text)

    Path("/tmp/oauth_result.json").write_text(json.dumps({
        "oauth_client_id": full_client_id,
        "tunnel": TUNNEL,
        "callback": CALLBACK,
    }))
    print("SUCCESS")


if __name__ == "__main__":
    main()
