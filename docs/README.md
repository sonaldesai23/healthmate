# 🩺 HealthMate Advanced v2.0.0

**Emergency Medical Triage System with AI Analysis**

## 🎯 What's New in v2.0.0

### Major Upgrades:

1. **Grok AI + Gemini Integration**
   - Grok AI for advanced symptom analysis
   - Gemini for professional report generation
   - More intelligent, less heuristic-based

2. **React Frontend (Netlify Ready)**
   - Replaced Streamlit with production React
   - Deploy to Netlify easily
   - Modern, responsive UI

3. **Triage-Based Diagnostic Model**
   - Structured questioning (not symptom lookup)
   - Assessment-based (not definitive diagnosis)
   - Similar to professional medical triage

---

## 📁 Project Structure

```
healthmate-advanced/
│
├── 📁 backend/                    [FastAPI Server]
│   ├── main.py                   [Updated with new endpoints]
│   ├── llm_integration.py        [NEW: Grok + Gemini APIs]
│   ├── triage_based_model.py     [NEW: Diagnostic questions]
│   ├── triage_engine.py          [Original - unchanged]
│   ├── rag_system.py             [Original - unchanged]
│   ├── risk_scorer.py            [Original - unchanged]
│   └── __init__.py
│
├── 📁 frontend/                   [React App for Netlify]
│   ├── 📁 src/
│   │   ├── App.jsx               [Main app component]
│   │   ├── App.css               [App styling]
│   │   ├── index.jsx             [React entry point]
│   │   ├── index.css             [Global styles]
│   │   └── 📁 components/
│   │       ├── ChatInterface.jsx [Chat UI component]
│   │       └── ChatInterface.css [Chat styling]
│   │
│   ├── 📁 public/
│   │   └── index.html            [HTML template]
│   │
│   ├── package.json              [Node dependencies]
│   └── .gitignore
│
├── 📁 docs/                       [Documentation]
│   ├── ARCHITECTURE.md           [System design]
│   ├── SETUP.md                  [Installation guide]
│   ├── DEPLOYMENT.md             [Deployment guide]
│   └── API_REFERENCE.md          [API endpoints]
│
├── 🔧 Configuration Files
│   ├── .env.example              [Environment template]
│   ├── requirements.txt          [Python dependencies]
│   ├── netlify.toml              [Netlify configuration]
│   ├── docker-compose.yml        [Docker setup]
│   ├── Dockerfile.backend        [Backend container]
│   └── Dockerfile.frontend       [Frontend container]
│
├── 📄 README.md                  [This file]
└── .gitignore                    [Git ignore rules]
```

---

## 🚀 Quick Start

### Option 1: Local Development (Recommended)

#### Backend Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env and add your API keys

# 4. Run backend server
python -m uvicorn backend.main:app --reload
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

#### Frontend Setup (New Terminal)

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install Node dependencies
npm install

# 3. Set environment variables
# Create .env in frontend directory:
REACT_APP_API_URL=http://localhost:8000

# 4. Start development server
npm start
# Frontend: http://localhost:3000
```

---

### Option 2: Docker (For Production)

```bash
# Build both services
docker-compose build

# Run everything
docker-compose up

# Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

---

### Option 3: Deploy to Netlify (Frontend Only)

**Prerequisites:**
- GitHub account
- Netlify account
- Backend deployed (see Deployment Guide)

**Steps:**

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Netlify**
   - Go to [netlify.com](https://netlify.com)
   - Click "New site from Git"
   - Select your repository
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/build`
   - Click Deploy!

3. **Set Environment Variables**
   - In Netlify dashboard → Settings → Build & deploy → Environment
   - Add: `REACT_APP_API_URL=https://your-backend-domain.com`

---

## 🔑 Getting API Keys

### Grok AI API

1. Go to: https://console.x.ai
2. Sign up or login
3. Create API key
4. Add to `.env`:
   ```
   GROK_API_KEY=your_key_here
   ```

### Gemini API

1. Go to: https://ai.google.dev
2. Click "Get API Key"
3. Create new key
4. Add to `.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```

---

## 📡 API Endpoints (Backend)

### Session Management
```
POST /api/session/start              → Start new session
GET /api/session/{session_id}        → Get session status
DELETE /api/session/{session_id}     → Delete session
```

### Conversation
```
POST /api/conversation               → Process user message
GET /api/triage-result/{session_id}  → Get triage assessment
```

### Advanced Analysis (NEW)
```
POST /api/advanced-analysis/{session_id}     → Get Grok + Gemini analysis
POST /api/diagnostic-question/{session_id}   → Get next diagnostic question
POST /api/diagnostic-answer/{session_id}     → Submit diagnostic answer
GET /api/diagnostic-assessment/{session_id}  → Get diagnostic assessment
```

### Health Check
```
GET /health                          → Server health status
```

**Full API documentation:** http://localhost:8000/docs (Swagger UI)

---

## 🧠 How It Works

### Pipeline:

```
1. USER INPUT (Chat)
        ↓
2. TRIAGE ENGINE (Conversation, Info Extraction)
        ↓
3. EMERGENCY DETECTION (Hard-coded triggers)
        ├─ Emergency? → CALL 911 (STOP)
        └─ Continue...
        ↓
4. TRIAGE COMPLETE → Trigger AI Analysis
        ↓
5. GROK AI ANALYSIS (Advanced symptom analysis)
        ↓
6. GEMINI REPORT (Professional formatted report)
        ↓
7. DISPLAY RESULTS (UI shows analysis + report)
```

### Key Differences from v1.0:

| Aspect | v1.0 | v2.0 |
|--------|------|------|
| **Analysis** | Heuristic | Grok AI + Gemini |
| **Report** | Simple text | AI-generated professional |
| **Frontend** | Streamlit | React |
| **Deployment** | Docker only | Docker + Netlify |
| **Approach** | Pattern matching | Triage-based assessment |

---

## ⚙️ Configuration

### Backend (.env)

```env
# API Keys (REQUIRED)
GROK_API_KEY=your_grok_key
GEMINI_API_KEY=your_gemini_key

# Server
API_HOST=0.0.0.0
API_PORT=8000

# Frontend (for CORS)
REACT_APP_API_URL=http://localhost:8000

# Logging
LOG_LEVEL=info
```

### Frontend (.env)

```env
# API Endpoint
REACT_APP_API_URL=http://localhost:8000

# For production (Netlify)
# REACT_APP_API_URL=https://your-backend-domain.com
```

---

## 🔒 Safety Features

✅ **Hard-coded Emergency Detection** - No ML-based classification for safety-critical decisions

✅ **Medical Disclaimers** - Displayed on every screen

✅ **No Prescriptions** - Only first-aid guidance

✅ **Source Attribution** - Shows what knowledge was used

✅ **Conservative Bias** - Escalates when uncertain

✅ **Triage-Based** - Asks questions instead of direct diagnosis

---

## 🚢 Production Deployment

### Backend Deployment Options:

#### 1. Heroku
```bash
# 1. Create Heroku app
heroku create your-healthmate-api

# 2. Set environment variables
heroku config:set GROK_API_KEY=your_key
heroku config:set GEMINI_API_KEY=your_key

# 3. Deploy
git push heroku main
```

#### 2. Railway.app
```bash
# 1. Connect GitHub repository
# 2. Set environment variables in dashboard
# 3. Auto-deploys on push
```

#### 3. AWS EC2
```bash
# 1. Launch EC2 instance
# 2. Install Docker
# 3. Build and run container
docker-compose -f docker-compose.yml up -d
```

### Frontend Deployment:

Already covered above (Netlify recommended)

---

## 📊 Monitoring & Logs

### Backend Logs
```bash
# View in real-time
docker-compose logs -f backend

# Or if running locally
# Terminal output shows all logs
```

### Frontend Logs
```bash
# Browser console (F12)
# Check Network tab for API calls
```

---

## 🔧 Development

### Install Development Tools

```bash
# Python
pip install black flake8 pytest pytest-cov

# Node
npm install -g eslint prettier
```

### Format Code

```bash
# Python
black backend/
flake8 backend/

# JavaScript
cd frontend && npm run format
```

### Run Tests

```bash
# Python tests (optional)
pytest tests/

# React tests (optional)
cd frontend && npm test
```

---

## 📚 Documentation

- **SETUP.md** - Detailed installation guide
- **ARCHITECTURE.md** - System design & modules
- **DEPLOYMENT.md** - Deployment procedures
- **API_REFERENCE.md** - API documentation
- **VIVA_PREPARATION.md** - Interview Q&A guide

---

## ⚠️ Important Notes

### This is Educational
- ✅ For learning and demonstration
- ✅ Safe and well-designed
- ⚠️ NOT FDA-approved
- ⚠️ NOT for real medical use

### Always Include Disclaimer
```
This system is for emergency triage guidance only.
It is NOT a substitute for professional medical diagnosis.
Always consult qualified healthcare professionals.
In emergencies, CALL 911 IMMEDIATELY.
```

---

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Backend
python -m uvicorn backend.main:app --port 8001

# Frontend
npm start -- --port 3001
```

### API Key Errors
- Check `.env` file exists
- Verify keys are correct
- Check API services are active

### CORS Errors
- Ensure backend is running
- Check `REACT_APP_API_URL` in frontend `.env`
- Verify API URL matches backend address

### Module Not Found
```bash
# Backend
pip install -r requirements.txt --force-reinstall

# Frontend
cd frontend && npm install
```

---

## 📞 Support

For issues:
1. Check logs (terminal output)
2. Review `.env` configuration
3. Verify API keys are valid
4. Check troubleshooting section above

---

## 📜 License

Educational project - MIT License

---

## 🎓 Project Info

**Version:** 2.0.0  
**Status:** Production Ready  
**Updated:** February 2025  

**Key Technologies:**
- Backend: FastAPI + Python
- Frontend: React + Axios
- AI: Grok AI + Gemini API
- Deployment: Docker + Netlify

**Features:**
- ✅ Grok AI Analysis
- ✅ Gemini Reports
- ✅ Triage-Based Diagnostics
- ✅ React Frontend
- ✅ Netlify Ready
- ✅ Professional UI/UX

---

**Ready to get started?** Follow the Quick Start guide above! 🚀
