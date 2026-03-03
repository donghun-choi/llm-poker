# LLM Poker Bot

Play a 6-max Texas Hold'em demo versus AI personalities. Backend is FastAPI, frontend is React + Vite. One command launch via Docker Compose.

## Prerequisites
- Python 3.11+
- Node 20+
- Docker (for compose)

## Quick start
```bash
docker compose up --build
```
Backend: http://localhost:8000
Frontend: http://localhost:3000

## Environment
Copy `.env.example` to `.env` and set keys:
```
LLM_PROVIDER=openai  # or ollama
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OLLAMA_MODEL=llama3.1:8b
```

## Local dev
Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Tests
```bash
python -m pytest backend/tests -q
```

## Project structure
- `backend/` – FastAPI, poker engine, LLM layer
- `frontend/` – React UI, Tailwind, WebSocket client
- `docker-compose.yml` – one-command launch
