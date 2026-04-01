# UniverBot

AI Chatbot Builder SaaS Platform - Create, train, and deploy AI chatbots powered by your own knowledge base.

## Project Structure

```
univerbot/
├── frontend/                 # Next.js 14 Frontend
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   │   ├── dashboard/   # Dashboard pages
│   │   │   ├── login/       # Authentication
│   │   │   └── register/
│   │   ├── components/      # React components
│   │   │   ├── ui/          # ShadCN UI components
│   │   │   └── providers/   # Context providers
│   │   ├── lib/             # Utilities & Supabase client
│   │   ├── store/           # Zustand state management
│   │   └── types/           # TypeScript types
│   ├── public/
│   │   └── univerbot.js     # Embeddable chat widget
│   └── package.json
│
├── backend/                  # FastAPI Backend
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   │   ├── bot.py       # Bot CRUD & training
│   │   │   ├── chat.py      # Chat endpoints
│   │   │   └── health.py    # Health check
│   │   ├── core/            # Auth & middleware
│   │   ├── db/              # Supabase client
│   │   ├── models/          # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   │   ├── document_processor.py  # PDF/text chunking
│   │   │   ├── embeddings.py          # Gemini embeddings
│   │   │   ├── rag.py                 # Vector search
│   │   │   └── llm.py                 # LLM integration
│   │   ├── config.py
│   │   └── main.py
│   └── requirements.txt
│
└── database/
    └── schema.sql           # Supabase database schema
```

## Tech Stack

### Frontend

- **Next.js 14** (App Router, TypeScript)
- **TailwindCSS** with custom dark theme (#030617 background, #00E5FF cyan accent)
- **ShadCN UI** components
- **Zustand** for state management
- **React Query** for server state
- **Supabase Auth Helpers** for authentication

### Backend

- **FastAPI** (Python)
- **Supabase** (PostgreSQL + Auth + Storage)
- **Google Gemini** for embeddings and LLM
- **Groq LLaMA3** as optional fallback

### Database

- **Supabase Postgres** with pgvector extension
- **Vector embeddings** (768 dimensions for Gemini)
- **Row Level Security** policies

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Supabase account
- Google AI Studio API key (Gemini)
- (Optional) Groq API key

### 1. Setup Supabase

1. Create a new Supabase project
2. Run the SQL schema from `database/schema.sql` in the SQL Editor
3. Enable the `vector` extension in Database > Extensions
4. Copy your project URL, anon key, service role key, and JWT secret

### 2. Setup Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your Supabase credentials
npm run dev
```

### 3. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn app.main:app --reload
```

## Environment Variables

### Frontend (.env.local)

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
JWT_SECRET=your-jwt-secret
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key  # Optional
```

## API Endpoints

### Bot Management

- `POST /bot/create` - Create a new bot
- `GET /bot/list` - List user's bots
- `GET /bot/{id}` - Get bot details
- `PATCH /bot/{id}` - Update bot
- `DELETE /bot/{id}` - Delete bot
- `POST /bot/{id}/upload` - Upload training document
- `POST /bot/{id}/train` - Generate embeddings for documents

### Chat

- `POST /chat/{bot_id}` - Chat with bot (requires API key)
- `POST /chat/{bot_id}/preview` - Preview chat (requires auth)
- `GET /chat/{bot_id}/history/{session_id}` - Get chat history

## Embedding the Widget

Add this script to any website:

```html
<script
  src="https://cdn.univerbot.app/univerbot.js"
  data-bot-id="YOUR_BOT_ID"
  data-api-key="YOUR_BOT_API_KEY"
></script>
```

The widget will appear as a floating chat button in the bottom-right corner.

## Features

- ✅ User authentication (Supabase Auth)
- ✅ Bot creation and management
- ✅ Document upload (PDF, TXT, MD)
- ✅ RAG-based knowledge retrieval
- ✅ Gemini Flash for responses
- ✅ API key protection
- ✅ Embeddable chat widget
- ✅ Chat history
- ✅ Dark theme UI

## Deployment

### Frontend (Vercel)

```bash
vercel
```

### Backend (Railway)

```bash
railway up
```

## License

MIT
