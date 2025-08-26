# MORVO Agent - Multi-Service Architecture

A refactored version of the MORVO agent with a clean multi-service architecture to fix onboarding loops and improve maintainability.

## Architecture Overview

The application is split into three independent FastAPI services:

1. **Agent Core** (Port 9000) - Main chat interface with onboarding gate
2. **Memory API** (Port 8000) - SQLite-based memory storage and retrieval
3. **Supabase Proxy** (Port 8001) - Facade for profile management

## Services

### Agent Core (`agent/`)
- **Main endpoint**: `POST /chat` - Handles user messages with onboarding gate
- **Health check**: `GET /healthz`
- **Features**: 
  - Onboarding gate (name, role, goal required)
  - Memory integration
  - Supabase profile management

### Memory API (`memory_api/`)
- **Endpoints**:
  - `GET /healthz` - Health check
  - `POST /recall` - Retrieve user memories
  - `POST /remember` - Store new memories
  - `POST /search_doc` - Document search (stub)
- **Storage**: SQLite database (`mem.db`)

### Supabase Proxy (`supabase_proxy/`)
- **Endpoints**:
  - `GET /healthz` - Health check
  - `GET /profiles/{user_id}` - Get user profile
  - `PATCH /profiles/{user_id}` - Update user profile
- **Features**: Profile upsert operations

## Environment Setup

1. Copy the environment file:
```bash
cp env.example .env
```

2. Fill in your Supabase credentials:
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
DEFAULT_LANG=ar
```

## Running Locally

### Individual Services

```bash
# Memory API
uvicorn memory_api.app:app --port 8000 --reload

# Supabase Proxy
uvicorn supabase_proxy.app:app --port 8001 --reload

# Agent Core
uvicorn agent.app:app --port 9000 --reload
```

### Docker Compose

```bash
docker-compose up --build
```

## Testing

### Quick Test Commands

```bash
# Health checks
curl http://localhost:9000/healthz
curl http://localhost:8000/healthz
curl http://localhost:8001/healthz

# Onboarding flow test
curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u_123","message":"السلام عليكم"}'

curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u_123","message":"ويأم"}'

curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u_123","message":"Head of Marketing"}'

curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u_123","message":"زيادة الوعي"}'
```

## Onboarding Flow

The agent implements a strict onboarding gate:

1. **Name** - User's first name (minimum 2 characters)
2. **Role** - Current position/role
3. **Goal** - Primary marketing objective

Until all three fields are complete, the agent will:
- Ask exactly ONE question per turn
- Save responses immediately
- Short-circuit normal chat logic
- Return completion message when done

## Memory Integration

- Onboarding progress is logged with `tags: ["onboarding"]`
- Normal chat queries are logged with `tags: ["trace"]`
- Memory recall retrieves the 5 most recent memories per user

## Development

### Project Structure
```
mona_agent/
├── agent/                 # Main chat service
│   ├── app.py
│   ├── onboarding.py
│   └── routers/
│       └── chat.py
├── memory_api/           # Memory storage service
│   ├── app.py
│   └── store.py
├── supabase_proxy/       # Profile management service
│   └── app.py
├── common/               # Shared resources
│   ├── schema.py
│   ├── prompts/
│   └── tools/
├── docker-compose.yml
└── requirements.txt
```

### Key Features

- **Onboarding Gate**: Prevents normal chat until profile is complete
- **Memory Persistence**: SQLite-based memory storage
- **Profile Management**: Supabase integration via proxy
- **Service Isolation**: Independent services with HTTP communication
- **Docker Support**: Full containerization with Docker Compose

## Migration Notes

- Original files (`agent.py`, `onboarding_graph.py`, `memory_store.py`) are preserved for reference
- New services handle all runtime operations
- Common resources moved to `common/` directory
- Import paths updated throughout the codebase
