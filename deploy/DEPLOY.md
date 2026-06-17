# VPS Deployment Guide — مدنی مذاکرہ ڈیٹا بیس

## Prerequisites

- Hostinger VPS (Ubuntu) with SSH access
- Free Cloudflare account
- Google Cloud Console project

## Step 1: Clone and configure

```bash
sudo mkdir -p /var/www/madani-muzakarah
sudo chown $USER:$USER /var/www/madani-muzakarah
git clone YOUR_REPO_URL /var/www/madani-muzakarah
cd /var/www/madani-muzakarah/backend
cp .env.example .env
nano .env
```

Set these in `.env`:
- `SECRET_KEY` — random 64-char string
- `ENCRYPTION_KEY` — run: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
- `ADMIN_EMAIL=asifaliarif2526@gmail.com`

## Step 2: Deploy services

```bash
bash deploy/deploy.sh
```

## Step 3: Cloudflare Named Tunnel (stable HTTPS URL)

```bash
cloudflared tunnel login
cloudflared tunnel create muzakarah-tunnel
cloudflared tunnel route dns muzakarah-tunnel muzakarah.YOUR_DOMAIN.com
# OR use the free cfargotunnel.com hostname shown after create

sudo mkdir -p /etc/cloudflared
sudo cp deploy/cloudflared.yml /etc/cloudflared/config.yml
# Edit hostname in config.yml
sudo cloudflared service install
sudo systemctl enable --now cloudflared
```

Copy the tunnel URL (e.g. `https://muzakarah-xxxxx.cfargotunnel.com`) and update `.env`:

```
FRONTEND_URL=https://muzakarah-xxxxx.cfargotunnel.com
GOOGLE_REDIRECT_URI=https://muzakarah-xxxxx.cfargotunnel.com/api/auth/callback
CORS_ORIGINS=https://muzakarah-xxxxx.cfargotunnel.com
```

Restart FastAPI: `sudo systemctl restart madani-fastapi`

## Step 4: Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
2. Create OAuth 2.0 Client ID (Web application)
3. Authorized redirect URIs: `https://YOUR_TUNNEL_URL/api/auth/callback`
4. Copy Client ID and Secret to `.env`

## Step 5: Verify

- Open your tunnel URL
- Login with Google (`asifaliarif2526@gmail.com` becomes admin automatically)
- Create a test note with "تحریر از" field
- Test download/share

## Services

| Service | Command |
|---------|---------|
| FastAPI logs | `journalctl -u madani-fastapi -f` |
| Meilisearch | `journalctl -u madani-meilisearch -f` |
| Tunnel | `journalctl -u cloudflared -f` |
| Restart all | `sudo systemctl restart madani-fastapi madani-meilisearch nginx cloudflared` |
