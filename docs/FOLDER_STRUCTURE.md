# 📂 HealthMate Advanced v2.0 - Complete Folder Structure

## Project Root Structure

```
healthmate-advanced/
├── 📄 README.md                          ← START HERE
├── 📄 .env.example                       ← Copy to .env and add API keys
├── 📄 .gitignore
├── 📄 requirements.txt                   ← Python dependencies
├── 📄 netlify.toml                       ← Netlify deployment config
├── 📄 docker-compose.yml                 ← Docker orchestration
├── 📄 Dockerfile.backend                 ← Backend container
├── 📄 Dockerfile.frontend                ← Frontend container
│
├── 📁 backend/                           [FASTAPI SERVER]
│   ├── 📄 __init__.py
│   ├── 📄 main.py                        [MAIN: API server + endpoints]
│   ├── 📄 llm_integration.py             [NEW: Grok + Gemini integration]
│   ├── 📄 triage_based_model.py          [NEW: Diagnostic questions]
│   ├── 📄 triage_engine.py               [ORIGINAL: Conversation flow]
│   ├── 📄 rag_system.py                  [ORIGINAL: Knowledge retrieval]
│   └── 📄 risk_scorer.py                 [ORIGINAL: Risk calculation]
│
├── 📁 frontend/                          [REACT APP FOR NETLIFY]
│   ├── 📄 package.json                   [Node dependencies]
│   ├── 📄 .gitignore
│   │
│   ├── 📁 src/                           [SOURCE CODE]
│   │   ├── 📄 index.jsx                  [React entry point]
│   │   ├── 📄 index.css                  [Global styles]
│   │   ├── 📄 App.jsx                    [Main app component]
│   │   ├── 📄 App.css                    [App styles]
│   │   │
│   │   └── 📁 components/                [REACT COMPONENTS]
│   │       ├── 📄 ChatInterface.jsx      [Chat UI component]
│   │       └── 📄 ChatInterface.css      [Chat styles]
│   │
│   ├── 📁 public/                        [STATIC FILES]
│   │   └── 📄 index.html                 [HTML template]
│   │
│   └── 📁 build/                         [AUTO-GENERATED AFTER npm run build]
│       └── (created by build process)
│
├── 📁 docs/                              [DOCUMENTATION]
│   ├── 📄 SETUP.md                       [Installation guide]
│   ├── 📄 ARCHITECTURE.md                [System design]
│   ├── 📄 DEPLOYMENT.md                  [Deployment guide]
│   └── 📄 API_REFERENCE.md               [API documentation]
│
└── 📁 config/                            [OPTIONAL: Configuration]
    ├── 📄 logging.yaml
    └── 📄 constants.py
```

---

## Backend Structure Explanation

### `backend/main.py`
**Purpose:** FastAPI server & REST API endpoints  
**Key Functions:**
- Session management
- Conversation processing
- Advanced analysis orchestration
- Health checks
- Error handling

**Endpoints:**
- `POST /api/session/start` - Start new conversation
- `POST /api/conversation` - Process user message
- `POST /api/advanced-analysis/{session_id}` - Get Grok + Gemini analysis
- `GET /api/triage-result/{session_id}` - Get assessment result

### `backend/llm_integration.py` (NEW)
**Purpose:** Grok AI + Gemini API integration  
**Classes:**
- `GrokAnalyzer` - Advanced symptom analysis using Grok
- `GeminiReportGenerator` - Professional report generation using Gemini
- `TriageAnalysisPipeline` - Orchestrates both APIs

### `backend/triage_based_model.py` (NEW)
**Purpose:** Structured diagnostic questioning  
**Classes:**
- `TriageBasedAssessment` - Generates questions, evaluates answers

**Features:**
- Question trees for different symptoms
- Pattern matching for conditions
- Confidence-based assessment
- Red flag detection

### `backend/triage_engine.py` (ORIGINAL)
**Purpose:** Conversation management  
**Classes:**
- `TriageEngine` - 9-stage Q&A conversation
- `PatientProfile` - Patient data structure

### `backend/rag_system.py` (ORIGINAL)
**Purpose:** Medical knowledge retrieval  
**Classes:**
- `MedicalKnowledgeBase` - 10 curated documents
- `RAGSystem` - Retrieval system

### `backend/risk_scorer.py` (ORIGINAL)
**Purpose:** Risk calculation  
**Classes:**
- `RiskScorer` - Weighted scoring algorithm
- `SeverityAnalyzer` - Edge case analysis

---

## Frontend Structure Explanation

### `frontend/package.json`
**Purpose:** Node.js dependencies and scripts  
**Key Scripts:**
- `npm start` - Development server
- `npm run build` - Production build
- `npm test` - Tests

### `frontend/src/App.jsx`
**Purpose:** Main React app component  
**Contains:**
- Header with app title
- ChatInterface component
- Footer with disclaimer

### `frontend/src/components/ChatInterface.jsx`
**Purpose:** Main chat interface component  
**Features:**
- Session management
- Message display
- Input handling
- API integration
- Results display
- Report download

### `frontend/public/index.html`
**Purpose:** HTML template for React  
**Contains:**
- Root div for React
- Meta tags
- Favicon reference

---

## Configuration Files Explanation

### `.env.example`
**Purpose:** Template for environment variables  
**Usage:** `cp .env.example .env` then edit with your API keys  
**Variables:**
- `GROK_API_KEY` - From XAI Console
- `GEMINI_API_KEY` - From Google AI Studio
- `REACT_APP_API_URL` - Backend URL
- `API_HOST`, `API_PORT` - Server config

### `requirements.txt`
**Purpose:** Python package dependencies  
**Packages:**
- FastAPI, Uvicorn (server)
- Requests (HTTP client)
- python-dotenv (environment)
- sentence-transformers, faiss (optional)

### `netlify.toml`
**Purpose:** Netlify deployment configuration  
**Specifies:**
- Build command
- Publish directory
- Redirect rules
- Headers configuration

### `docker-compose.yml`
**Purpose:** Docker container orchestration  
**Services:**
- `backend` - FastAPI server on port 8000
- `frontend` - React on port 3000
- Network configuration

### `Dockerfile.backend`
**Purpose:** Backend container image  
**Contains:**
- Python 3.10 base
- Dependencies installation
- Health checks

### `Dockerfile.frontend`
**Purpose:** Frontend container image  
**Contains:**
- Node.js base
- Build process
- Serving with nginx

---

## File Purposes Quick Reference

| File | Purpose | Modify? |
|------|---------|---------|
| `main.py` | API server | ✅ Yes - add endpoints |
| `llm_integration.py` | Grok + Gemini | ⚠️ Maybe - tune prompts |
| `triage_based_model.py` | Diagnostic Q&A | ✅ Yes - add questions |
| `triage_engine.py` | Conversation | ⚠️ Maybe - adjust flow |
| `rag_system.py` | Knowledge base | ✅ Yes - add documents |
| `risk_scorer.py` | Risk calculation | ⚠️ Maybe - adjust weights |
| `App.jsx` | Main app | ⚠️ Maybe - styling |
| `ChatInterface.jsx` | Chat UI | ✅ Yes - enhance UI |
| `.env` | Secrets | ✅ YES - add API keys |
| `requirements.txt` | Dependencies | ✅ Yes - add packages |
| `netlify.toml` | Deployment | ⚠️ Maybe - change dirs |

---

## Data Flow Through Files

### User sends message:
```
Frontend (ChatInterface.jsx)
  ↓ axios POST /api/conversation
Backend (main.py)
  ↓ passes to
TriageEngine (triage_engine.py)
  ↓ checks emergency
LLM Integration (llm_integration.py)
  ↓ if analysis needed
Triage Model (triage_based_model.py)
  ↓ generates assessment
Risk Scorer (risk_scorer.py)
  ↓ returns response
Backend (main.py)
  ↓ JSON response
Frontend (ChatInterface.jsx)
  ↓ displays
User sees message
```

---

## Where to Make Changes

### Want to add new symptoms?
→ Edit `backend/triage_based_model.py`  
→ Add to `HEADACHE_QUESTIONS` or similar

### Want to improve risk scoring?
→ Edit `backend/risk_scorer.py`  
→ Adjust weights and formulas

### Want to change UI?
→ Edit `frontend/src/components/ChatInterface.jsx`  
→ And `frontend/src/components/ChatInterface.css`

### Want to add medical knowledge?
→ Edit `backend/rag_system.py`  
→ Add to `KNOWLEDGE_DOCUMENTS`

### Want to customize Grok prompts?
→ Edit `backend/llm_integration.py`  
→ Modify prompts in `GrokAnalyzer.analyze_symptoms()`

### Want to change app styling?
→ Edit `frontend/src/App.css`  
→ Edit `frontend/src/App.jsx`

---

## Environment Variable Locations

### Backend uses (.env at project root):
```
backend/main.py:  os.getenv("GROK_API_KEY")
backend/main.py:  os.getenv("GEMINI_API_KEY")
```

### Frontend uses (.env in frontend/ directory):
```
frontend/src/components/ChatInterface.jsx: 
  process.env.REACT_APP_API_URL
```

---

## Build Output Structure

After `npm run build` in frontend:

```
frontend/build/
├── index.html
├── static/
│   ├── js/
│   │   ├── main.[hash].js
│   │   └── ...
│   └── css/
│       ├── main.[hash].css
│       └── ...
└── favicon.ico
```

This `build/` folder is what Netlify deploys.

---

## Deployment Structure

### Local Development:
```
Both services run separately
Backend: http://localhost:8000
Frontend: http://localhost:3000
```

### Docker Development:
```
Both in containers
Backend: http://localhost:8000
Frontend: http://localhost:3000
```

### Production (Netlify + Cloud Backend):
```
Frontend deployed to Netlify
Backend deployed to Heroku/Railway/AWS
Frontend calls: https://your-backend-domain.com
```

---

## File Sizes Reference

| File | Size | Importance |
|------|------|-----------|
| `main.py` | ~12 KB | Critical |
| `llm_integration.py` | ~8 KB | Critical |
| `triage_based_model.py` | ~10 KB | Critical |
| `ChatInterface.jsx` | ~9 KB | Critical |
| `requirements.txt` | <1 KB | Critical |
| `package.json` | ~1 KB | Critical |

---

## Common Issues by File

### If backend won't start:
→ Check `backend/main.py` imports  
→ Verify `requirements.txt` installed

### If frontend won't load:
→ Check `frontend/src/index.jsx`  
→ Check `frontend/public/index.html`

### If API calls fail:
→ Check `frontend/src/components/ChatInterface.jsx`  
→ Check `.env` API URL

### If analysis fails:
→ Check `.env` has API keys  
→ Check `backend/llm_integration.py` API calls

---

That's the complete structure! 🎉
