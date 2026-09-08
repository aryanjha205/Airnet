# Airnet — Implementation Plan

A real-time voice/chat web app (inspired by Airtalk), built with:
- **Backend:** Python (FastAPI)
- **Database:** Neon (Serverless Postgres)
- **Frontend:** Vite + Vanilla CSS (no framework assumed — swap in React/Vue if needed)
- **Realtime:** WebSockets (FastAPI native) + optional WebRTC for voice

---

## 1. Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Frontend build | Vite | Fast dev server, HMR, simple prod bundling |
| Styling | Plain CSS (CSS variables + modules) | No Tailwind unless you want it — keep it lightweight |
| Backend | FastAPI (Python) | Async, native WebSocket support, auto OpenAPI docs |
| ORM | SQLAlchemy 2.0 (async) + Alembic | Migrations + type-safe queries |
| Database | Neon Postgres | Serverless, branch-per-environment, connection pooling via PgBouncer |
| Auth | JWT (access + refresh) via `python-jose` + `passlib[bcrypt]` | Simple email/password to start; OAuth later |
| Realtime chat | FastAPI WebSocket endpoints | Room-based pub/sub |
| Realtime voice (optional, phase 2) | WebRTC (peer-to-peer) + signaling over WebSocket | STUN/TURN server needed for NAT traversal (e.g. coturn) |
| Deployment | Frontend: Vercel/Netlify. Backend: Render/Fly.io/Railway. DB: Neon (already serverless) | |

---

## 2. Project Structure

```
airnet/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entrypoint
│   │   ├── config.py            # env vars, settings
│   │   ├── database.py          # Neon connection + session
│   │   ├── models/               # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── room.py
│   │   │   └── message.py
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── rooms.py
│   │   │   ├── messages.py
│   │   │   └── ws.py             # WebSocket handlers
│   │   ├── services/             # business logic
│   │   ├── auth/                 # JWT, password hashing
│   │   └── utils/
│   ├── alembic/                  # migrations
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── src/
│   │   ├── main.js
│   │   ├── api/                  # fetch wrappers
│   │   ├── ws/                   # websocket client
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── Login.js
│   │   │   ├── Rooms.js
│   │   │   └── Room.js
│   │   └── styles/
│   │       ├── variables.css
│   │       ├── base.css
│   │       └── components.css
│   └── package.json
│
└── README.md
```

---

## 3. Database Schema (Neon Postgres)

```sql
-- users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- rooms (chat/voice channels)
CREATE TABLE rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    is_private BOOLEAN DEFAULT false,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- room_members
CREATE TABLE room_members (
    room_id UUID REFERENCES rooms(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMPTZ DEFAULT now(),
    role VARCHAR(20) DEFAULT 'member', -- member, admin
    PRIMARY KEY (room_id, user_id)
);

-- messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID REFERENCES rooms(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- presence (optional: track who's online/in-call)
CREATE TABLE presence (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    room_id UUID REFERENCES rooms(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'online', -- online, in_call, away
    updated_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (user_id, room_id)
);
```

Indexes to add:
```sql
CREATE INDEX idx_messages_room_created ON messages(room_id, created_at DESC);
CREATE INDEX idx_room_members_user ON room_members(user_id);
```

---

## 4. API Endpoints (REST)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Get JWT tokens |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/users/me` | Current user profile |
| GET | `/rooms` | List rooms user belongs to |
| POST | `/rooms` | Create a room |
| POST | `/rooms/{id}/join` | Join a room |
| GET | `/rooms/{id}/messages` | Paginated message history |
| DELETE | `/rooms/{id}/leave` | Leave room |

## 5. WebSocket Endpoints

| Endpoint | Purpose |
|---|---|
| `/ws/rooms/{room_id}` | Join room's live channel — receive/send chat messages, presence updates |
| `/ws/signal/{room_id}` | WebRTC signaling (offer/answer/ICE candidates) — phase 2 for voice |

**Message envelope format (WebSocket):**
```json
{
  "type": "chat_message | presence | webrtc_offer | webrtc_answer | ice_candidate",
  "payload": { },
  "sender_id": "uuid",
  "timestamp": "iso8601"
}
```

---

## 6. Phased Build Plan

### Phase 1 — Foundation
- [ ] Set up Neon project, get connection string
- [ ] Scaffold FastAPI backend, connect to Neon via SQLAlchemy async engine
- [ ] Set up Alembic migrations, run schema above
- [ ] Scaffold Vite frontend (vanilla JS or pick a framework), set up CSS variables/theme
- [ ] Implement auth (register/login/JWT)

### Phase 2 — Text Chat Core
- [ ] Room CRUD + membership
- [ ] WebSocket chat endpoint with room-based broadcast
- [ ] Frontend: room list, chat UI, message history pagination
- [ ] Presence indicator (online/offline)

### Phase 3 — Voice (Airtalk parity)
- [ ] Set up TURN/STUN (coturn or a hosted service like Twilio STUN/TURN)
- [ ] WebRTC signaling over WebSocket
- [ ] Frontend: mic capture, peer connection handling, mute/deafen controls
- [ ] Multi-user voice room (mesh for small rooms, or SFU like mediasoup/LiveKit if scaling)

### Phase 4 — Polish
- [ ] Avatars, user settings
- [ ] Notifications (unread badges)
- [ ] Rate limiting, input validation, error boundaries
- [ ] Responsive CSS (mobile layout)
- [ ] Deploy: frontend → Vercel, backend → Railway/Fly.io, DB → Neon (prod branch)

---

## 7. Environment Variables

**backend/.env**
```
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<neon-host>/<db>?sslmode=require
JWT_SECRET=change_me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:5173
```

**frontend/.env**
```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## 8. Key Dependencies

**backend/requirements.txt**
```
fastapi
uvicorn[standard]
sqlalchemy[asyncio]
asyncpg
alembic
python-jose[cryptography]
passlib[bcrypt]
pydantic-settings
python-multipart
websockets
```

**frontend/package.json (core)**
```
vite
```
(Add a framework like `react`/`vue` here only if you decide not to go vanilla.)

---

## 9. Open Decisions to Confirm
- Vanilla JS or a frontend framework (React/Vue) on top of Vite?
- Voice from day one, or ship text-chat MVP first? (Recommended: text first)
- Mesh WebRTC (simple, fine for <6 people/room) vs SFU like LiveKit/mediasoup (needed for larger rooms)?
- Self-host TURN server or use a managed one (Twilio, Metered.ca)?
