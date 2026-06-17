# On VPS use Python 3.11 or 3.12 recommended

PRD-compliant shared notes web app with Google OAuth, real-time updates, AI formatting, search, and PWA.

## Stack

- **Frontend:** React + Vite + TypeScript + Tailwind + TipTap
- **Backend:** FastAPI + PostgreSQL + Meilisearch
- **Auth:** Google OAuth 2.0 (admin: `asifaliarif2526@gmail.com`)

## Local Development

### 1. Start databases

```bash
docker compose up -d
```

### 2. Backend

```bash
cd backend
cp .env.example .env
python -m venv venv
# Windows: venv\Scripts\activate
# Linux: source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Environment Variables

See `backend/.env.example`. Required for production:

- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI` → `https://YOUR_TUNNEL/api/auth/callback`
- `FRONTEND_URL` → `https://YOUR_TUNNEL`
- `SECRET_KEY` / `ENCRYPTION_KEY`

## VPS Deployment

1. Clone repo to `/var/www/madani-muzakarah`
2. Copy and edit `backend/.env`
3. Run `bash deploy/deploy.sh`
4. Set up Cloudflare named tunnel (see `deploy/cloudflared.yml`)
5. Add OAuth redirect URI in Google Cloud Console

## Features

- Google login only (no anonymous access)
- Shared real-time notes with FAB (+)
- Categories (multi-select), archive, trash (admin)
- TipTap editor: Bold, QR (Quran), AR (Arabic)
- AI auto-formatting (Gemini/OpenAI) via admin settings
- Meilisearch: word, phrase, exact, broad, multi-field
- Download/share: PNG, PDF, WhatsApp-formatted text
- **تحریر از:** author field on every note + export footer
- PWA install prompt
- Fatwaworld-inspired UI (#084981 / #d39e37)
