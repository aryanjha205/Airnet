# Airnet ✈️

> **Realtime rooms, chat and voice-ready communication.**

Airnet is a production-oriented realtime communication MVP built with FastAPI, SQLAlchemy, Neon PostgreSQL, Vite and native WebSockets.

## ✅ Implemented

- JWT access + refresh authentication
- Secure bcrypt password hashing
- User profile endpoint
- Room creation, listing, joining and leaving
- Persistent message history with pagination
- Realtime room chat over WebSockets
- Presence event broadcasting
- WebRTC signaling endpoint for offer/answer/ICE payloads
- Responsive dark UI built with Vite + vanilla JavaScript/CSS
- PostgreSQL migration SQL and environment templates
- Automatic development-table initialization for the API

## Stack

**Frontend:** Vite + Vanilla JavaScript + CSS  
**Backend:** Python + FastAPI + SQLAlchemy 2 async  
**Database:** Neon PostgreSQL  
**Realtime:** WebSockets  
**Voice:** WebRTC signaling (`/ws/signal/{room_id}`)

## Structure

```text
Airnet/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   └── models.py
│   ├── alembic/001_initial.sql
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/main.js
│   ├── src/style.css
│   ├── .env.example
│   ├── index.html
│   └── package.json
├── implementation.md
└── README.md
```

## Run locally

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux
uvicorn app.main:app --reload
```

Set `DATABASE_URL` in `.env` to your Neon PostgreSQL connection string and replace `JWT_SECRET` with a long random value.

### Frontend

```bash
cd frontend
npm install
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux
npm run dev
```

Open the Vite URL, create an account, create a room, and start chatting.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Register |
| POST | `/auth/login` | Login |
| POST | `/auth/refresh` | Refresh JWT |
| GET | `/users/me` | Current user |
| GET | `/rooms` | User rooms |
| POST | `/rooms` | Create room |
| POST | `/rooms/{id}/join` | Join room |
| GET | `/rooms/{id}/messages` | Message history |
| DELETE | `/rooms/{id}/leave` | Leave room |
| GET | `/health` | Health check |

WebSockets: `/ws/rooms/{room_id}` for chat/presence and `/ws/signal/{room_id}` for WebRTC signaling.

## Security

Never commit `.env` or production credentials. For deployment use HTTPS/WSS, a strong JWT secret, strict CORS origins, rate limiting, and a managed/self-hosted TURN server for reliable WebRTC connectivity.

## License

Add the project's chosen license before public distribution.
