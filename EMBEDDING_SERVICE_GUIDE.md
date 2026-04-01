# Embedding Service Integration Guide

## Architecture

The embedding service is now separated into a standalone microservice:

```
Main Backend (backend/)          Embedding Service (univerbot-embeddingmodel/)
├── FastAPI app                  ├── FastAPI app
├── Chat, Bot, RAG logic         ├── Sentence Transformers model
├── Supabase integration         ├── /embed endpoint
└── Calls embedding service  →   └── /embed/batch endpoint
```

## Setup Options

### Option 1: Deploy Embedding Service Separately (Recommended)

**Benefits:**

- Main backend is lightweight (~200MB RAM)
- Embedding service scales independently
- Can deploy main backend on smaller instances
- Update model without redeploying main app

**Steps:**

1. **Deploy Embedding Service** (choose one platform):

   **Koyeb (Free 512MB):**

   ```bash
   cd univerbot-embeddingmodel
   # Push to GitHub, then connect Koyeb
   # Set URL in main backend: EMBEDDING_SERVICE_URL=https://your-app.koyeb.app
   ```

   **Render:**

   ```bash
   cd univerbot-embeddingmodel
   # Connect to GitHub, Render auto-detects Docker
   ```

   **Fly.io:**

   ```bash
   cd univerbot-embeddingmodel
   fly launch
   fly deploy
   ```

2. **Update Main Backend Environment:**

   ```env
   # .env in backend/
   EMBEDDING_SERVICE_URL=https://your-embedding-service.koyeb.app
   EMBEDDING_PROVIDER=microservice
   EMBEDDING_DIMENSION=384
   ```

3. **Deploy Main Backend:**
   - Now only needs ~200MB RAM (Crawl4AI + app)
   - Fits on free tier platforms easily

### Option 2: Local Development (Both Services)

1. **Terminal 1 - Embedding Service:**

   ```bash
   cd univerbot-embeddingmodel
   pip install -r requirements.txt
   python -m app.main
   # Runs on http://localhost:8001
   ```

2. **Terminal 2 - Main Backend:**
   ```bash
   cd backend
   # In .env:
   # EMBEDDING_SERVICE_URL=http://localhost:8001
   # EMBEDDING_PROVIDER=microservice
   uvicorn app.main:app --reload
   # Runs on http://localhost:8000
   ```

### Option 3: Local Embedding (Legacy)

Keep embeddings in main backend (not recommended for production):

```env
# .env in backend/
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

Uncomment in `backend/requirements.txt`:

```
sentence-transformers>=2.2.2
torch>=2.0.0
```

## Testing the Embedding Service

```bash
# Health check
curl http://localhost:8001/health

# Single embedding
curl -X POST http://localhost:8001/embed \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'

# Batch embeddings
curl -X POST http://localhost:8001/embed/batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Hello", "World", "Test"]}'
```

## Environment Variables

### Main Backend (backend/.env)

```env
# ... existing vars ...

# Embedding Service
EMBEDDING_SERVICE_URL=http://localhost:8001  # or your deployed URL
EMBEDDING_PROVIDER=microservice  # "microservice" or "local"
EMBEDDING_DIMENSION=384
```

### Embedding Service (univerbot-embeddingmodel/.env)

```env
PORT=8001
PYTHONUNBUFFERED=1
```

## Deployment Recommendations

| Backend RAM | Strategy                        |
| ----------- | ------------------------------- |
| 200-300MB   | Deploy separately (recommended) |
| 500-700MB   | Deploy together (all-in-one)    |

**For 50 Free Users:**

- **Separated**: Main (200MB) + Embedding (150MB) = 350MB total across 2 services ✅
- **Together**: 670MB on single platform ❌ (harder to find free tier)

## Cost Analysis

### Free Tier (Separated Services)

- **Main Backend**: Koyeb/Render (512MB) - $0
- **Embedding Service**: Koyeb/Render (512MB) - $0
- **Total**: $0/month ✅

### Free Tier (Together)

- **Combined**: Google Cloud e2-micro (1GB) - $0
- **Limitation**: Only 1 free VM ⚠️

## Migration Checklist

- [x] Created `univerbot-embeddingmodel/` folder
- [x] FastAPI service with /embed endpoints
- [x] Dockerfile with pre-downloaded model
- [x] Updated main backend to call microservice
- [ ] Set EMBEDDING_SERVICE_URL in backend .env
- [ ] Deploy embedding service to Koyeb/Render
- [ ] Update EMBEDDING_SERVICE_URL with deployed URL
- [ ] Deploy main backend
- [ ] Test end-to-end flow

## Troubleshooting

**Connection Refused:**

- Check EMBEDDING_SERVICE_URL is correct
- Ensure embedding service is running
- Verify network connectivity

**Timeout Errors:**

- Increase httpx timeout (default 30s)
- Check embedding service logs
- Cold start may take 2-3 seconds

**Dimension Mismatch:**

- Ensure EMBEDDING_DIMENSION=384 in both services
- Run database migration: `migrate_to_384_dimensions.sql`
