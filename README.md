# Anupriyo Mandal's Policy Intelligence Engine

A RAG-powered policy intelligence engine with FastAPI + pgvector backend and a Vite + React frontend.

## Features
- Upload PDFs / text docs
- Chunk + embed + store in Postgres (pgvector)
- Query with grounded answers
- Source viewer + confidence score

## Local Setup

### 1) Backend

Create `backend/.env`:
```
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql+psycopg2://localhost:5432/rag_policy
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4.1-mini
EMBEDDING_DIMENSION=1536
CHUNK_SIZE=800
CHUNK_OVERLAP=100
TOP_K=6
```

Install and run:
```
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 2) Frontend

```
cd frontend
npm install
npm run dev
```

Frontend will default to `http://localhost:8000`. To change it, set:
```
VITE_API_URL=https://your-backend-domain
```

## Deploy: Railway (Backend + Postgres)

1. Create a Railway project and add a Postgres service.
2. Deploy the backend from this repo with root directory `backend`.
3. Set env vars in Railway:
   - `OPENAI_API_KEY`
   - `DATABASE_URL` (from Railway Postgres)
   - Optional: `EMBEDDING_MODEL`, `CHAT_MODEL`, `EMBEDDING_DIMENSION`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `TOP_K`
4. Start command (already in `backend/railway.toml`):
   - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Deploy: Vercel (Frontend)

1. Create a Vercel project from this repo with root directory `frontend`.
2. Set environment variable:
   - `VITE_API_URL=https://<your-railway-backend-url>`
3. Deploy. (Config in `frontend/vercel.json`)

## CORS

If you deploy the frontend, add your Vercel domain to `ALLOWED_ORIGINS` in `backend/app/config.py`.

## Notes
- This project uses pgvector. Your Postgres must have the `vector` extension installed.
- The backend auto-creates tables on startup.
