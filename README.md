# Airnet ✈️

> **A real-time voice & chat platform for connecting people instantly.**

Airnet is a modern realtime communication app inspired by the simplicity of Airtalk. The project is designed around fast room-based communication, live presence, text chat, and a path toward peer-to-peer voice calling.

## 🚀 Highlights

- 💬 **Realtime chat** with WebSocket-based room communication
- 🎙️ **Voice calling roadmap** powered by WebRTC
- 👥 **Rooms & membership** for private or shared conversations
- 🟢 **Live presence** for online, away, and in-call states
- 🔐 **JWT authentication** with access and refresh tokens
- ⚡ **FastAPI backend** with async APIs and native WebSocket support
- 🗄️ **Neon PostgreSQL** for serverless relational storage
- 🎨 **Vite frontend** with lightweight CSS and a mobile-friendly design
- 📦 **Deployment-ready architecture** for Vercel/Netlify + Railway/Fly.io/Render

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vite + Vanilla JavaScript + CSS |
| Backend | Python + FastAPI |
| Database | Neon PostgreSQL |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Authentication | JWT + bcrypt |
| Realtime | FastAPI WebSockets |
| Voice | WebRTC + WebSocket signaling |
| Frontend Hosting | Vercel / Netlify |
| Backend Hosting | Railway / Fly.io / Render |

## 🏗️ Architecture

```text
┌───────────────────────┐
│       Vite Client     │
│  UI • Chat • Presence │
└──────────┬────────────┘
           │ HTTPS / WebSocket
           ▼
┌───────────────────────┐
│      FastAPI API      │
│ Auth • Rooms • Chat   │
│ Presence • Signaling  │
└──────────┬────────────┘
           │ Async SQL
           ▼
┌───────────────────────┐
│   Neon PostgreSQL     │
│ Users • Rooms • Msgs  │
│ Members • Presence    │
└───────────────────────┘

        WebRTC (planned)
   Peer-to-peer voice audio
```

## 📁 Project Structure

```text
airnet/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── auth/
│   │   └── utils/
│   ├── alembic/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── src/
│   │   ├── main.js
│   │   ├── api/
│   │   ├── ws/
│   │   ├── components/
│   │   ├── pages/
│   │   └── styles/
│   └── package.json
│
├── implementation.md
└── README.md
```

## 🔌 API Overview

### REST

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/auth/register` | Create an account |
| `POST` | `/auth/login` | Get JWT tokens |
| `POST` | `/auth/refresh` | Refresh an access token |
| `GET` | `/users/me` | Get the current user |
| `GET` | `/rooms` | List rooms |
| `POST` | `/rooms` | Create a room |
| `POST` | `/rooms/{id}/join` | Join a room |
| `GET` | `/rooms/{id}/messages` | Get message history |
| `DELETE` | `/rooms/{id}/leave` | Leave a room |

### WebSocket

```text
/ws/rooms/{room_id}
```

Realtime chat and presence events are exchanged through room connections.

For future voice support:

```text
/ws/signal/{room_id}
```

This endpoint is intended for WebRTC offer/answer and ICE candidate signaling.

## 🗃️ Core Data Model

Airnet is designed around these primary entities:

- **Users** — accounts, usernames, emails, avatars
- **Rooms** — conversation spaces, including private rooms
- **Room Members** — membership and roles
- **Messages** — persistent room chat history
- **Presence** — live online / away / in-call state

## 🛠️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/aryanjha205/Airnet.git
cd Airnet
```

### 2. Backend setup

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

**Windows**

```bash
.venv\Scripts\activate
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<neon-host>/<db>?sslmode=require
JWT_SECRET=change_me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:5173
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

### 3. Frontend setup

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 🧪 Development Roadmap

### Phase 1 — Foundation

- [ ] Neon database connection
- [ ] FastAPI project setup
- [ ] SQLAlchemy + Alembic
- [ ] Authentication with JWT
- [ ] Vite frontend shell

### Phase 2 — Realtime Chat

- [ ] Room creation and membership
- [ ] WebSocket room messaging
- [ ] Message history pagination
- [ ] Online/offline presence

### Phase 3 — Voice

- [ ] WebRTC signaling
- [ ] Microphone permissions and audio streams
- [ ] Mute / deafen controls
- [ ] STUN/TURN configuration
- [ ] Multi-user voice rooms

### Phase 4 — Production Polish

- [ ] Notifications and unread counts
- [ ] User settings and avatars
- [ ] Rate limiting and validation
- [ ] Responsive mobile UI
- [ ] Production deployment and monitoring

## 🔐 Environment & Security

Never commit real credentials or secrets to GitHub. Keep `.env` files local and configure production secrets through your hosting provider.

Recommended production hardening includes secure JWT secrets, HTTPS/WSS, strict CORS configuration, rate limiting, input validation, and a managed STUN/TURN strategy for WebRTC.

## 📖 Implementation Guide

For the detailed architecture, database schema, endpoint design, project structure, dependencies, and phased build plan, see [`implementation.md`](./implementation.md).

## 🌍 Deployment

A typical deployment can use:

```text
Frontend  → Vercel / Netlify
Backend   → Railway / Fly.io / Render
Database  → Neon PostgreSQL
Voice     → WebRTC + STUN/TURN
```

## 🤝 Contributing

Contributions are welcome. Fork the repository, create a feature branch, make your changes, and open a pull request with a clear description of what changed.

## 📄 License

Add the project's chosen license here before distributing Airnet publicly.

---

<p align="center">
  Built with ⚡ Python, FastAPI, Vite, WebSockets & Neon
</p>
