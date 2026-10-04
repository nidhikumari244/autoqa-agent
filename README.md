# AutoQA — Autonomous Browser Agent for End-to-End Web Testing & Code Synthesis

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black?logo=next.js&logoColor=white)](https://nextjs.org)
[![Playwright](https://img.shields.io/badge/Playwright-1.44-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)

**AutoQA** is an enterprise-grade autonomous browser testing platform that translates high-level natural language verification goals into real-time web interactions, validates DOM state and visual regressions, and automatically synthesizes deterministic, runnable Playwright test suites (Python & TypeScript) for CI/CD pipelines.

---

## 🏛️ System Architecture

```
[ Next.js 14 Web Studio ] 
       │   ▲
  REST │   │ WebSockets (Screencast, Thoughts, Step Logs)
       ▼   │
 [ FastAPI Orchestrator Gateway ]
       │          │
  SQLAlchemy   Artifacts Store
 (Postgres/DB) (Screenshots & PDFs)
       │
   Async Task Dispatcher
       ▼
 [ Master Runner Execution Engine ]
       ├── Playwright Headless Chromium Sandbox
       ├── Set-of-Marks (SoM) DOM Grounding Parser
       ├── Multi-Modal Vision Agent (Gemini 1.5/2.0 Flash)
       ├── Deterministic Playwright Code Synthesizer
       └── ReportLab PDF Audit Generator
```

---

## 🚀 Key Technical Highlights & Innovations

1. **Set-of-Marks (SoM) Visual DOM Grounding**:
   - Rather than dumping the entire raw HTML tree (which overflows token contexts and fails on dynamic SPAs), AutoQA injects an in-browser observer script that prunes hidden nodes, indexes interactive elements (`button`, `input`, `a`, `role="button"`), and renders visual numeric badge overlays on screenshots.
   - Eliminates selector hallucination with exact 1:1 grounding between the Vision-Language Model and the DOM.

2. **Dual-Language Test Code Synthesizer**:
   - As the agent explores and validates the target scenario, it records deterministic selectors (`data-testid`, unique IDs, or text anchors).
   - Generates production-ready, copy-pasteable tests for both:
     - `pytest-playwright` (Python)
     - `@playwright/test` (TypeScript)

3. **Sub-Second Bi-Directional WebSocket Streaming**:
   - Live browser canvas streams screencasts directly to the user's dashboard alongside real-time agent reasoning thoughts, tool calls, and step execution latencies.

4. **Enterprise Audit & Compliance Reporting**:
   - Compiles formal PDF audit reports containing execution duration, pass/fail status, metadata tables, and step-by-step audit logs.

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide Icons |
| **Backend API** | FastAPI, Uvicorn, AsyncIO, WebSockets, Pydantic v2 |
| **Automation** | Microsoft Playwright (Chromium, Headless Shell) |
| **AI / Multi-Modal** | Google Gemini 1.5 Flash / Pro (native vision + tool calling) |
| **Persistence** | SQLAlchemy Async ORM (SQLite / PostgreSQL) |
| **Reporting & Media** | ReportLab PDF engine, Pillow image processing |
| **DevOps** | Docker, Docker Compose, Multi-stage builds |

---

## 📦 Quickstart Guide

### Option 1: Run Locally

#### 1. Backend Setup
```bash
cd backend
python -m venv .venv

# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

Create a `.env` file in the `backend/` directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
HEADLESS=true
```

Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```
Backend API and OpenAPI docs will be live at: `http://localhost:8000/docs`

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open your browser at: `http://localhost:3000`

---

### Option 2: Run with Docker Compose
```bash
docker compose up --build
```
Access the application at `http://localhost:3000`.

---

## 🧪 Running Automated Verification Tests
To verify the core engine and API locally without a browser window:
```bash
cd backend
.\.venv\Scripts\python tests\test_engine.py
.\.venv\Scripts\python tests\test_api.py
```

---

## 🎓 University Major Project Defense Q&A

**Q1: How does AutoQA prevent the AI from entering infinite loops?**
* **Answer**: AutoQA implements three safety layers: (1) A bounded `max_steps` horizon per scenario (default 20), (2) In-memory action history tracking that detects duplicate cyclic interactions, and (3) Dynamic state timeouts if DOM mutations stall.

**Q2: Why use Set-of-Marks (SoM) over raw HTML prompt injection?**
* **Answer**: Modern web applications (React, Next.js, Angular) generate massive DOM trees exceeding 50,000 tokens with thousands of invisible layout divs. SoM pruning filters out 95% of irrelevant nodes and tags visible interactive elements with numeric badges directly on the image, yielding 10x lower token cost and sub-second reasoning latency.

**Q3: How are the generated Playwright scripts made deterministic?**
* **Answer**: While the agent uses multi-modal reasoning to navigate and discover flows, the `CodeSynthesizer` resolves each interaction to robust, permanent locators (e.g. `data-testid`, semantic role, or unique text anchors) with explicit wait states (`waitForLoadState('domcontentloaded')`), ensuring the synthesized test runs independently of the LLM in standard CI/CD pipelines.
