# AutoQA — Production Deployment Guide & GitHub Setup

This document provides step-by-step instructions to push **AutoQA** to GitHub and deploy both the **Next.js 14 Web Studio** and the **FastAPI + Playwright Headless Engine** to the cloud.

---

## 🐙 Step 1: Push Project to GitHub

A pristine Git repository has already been initialized locally with all sensitive `.env` files, build caches, and test artifacts safely ignored.

### 1. Create a Repository on GitHub
1. Navigate to [github.com/new](https://github.com/new).
2. Enter the repository name: `AutoQA` (or your preferred name).
3. Select **Public** or **Private**.
4. **Important**: Leave "Add a README file", ".gitignore template", and "license" **unchecked** (we already have them initialized).
5. Click **Create repository**.

### 2. Push Your Local Code to GitHub
Open your terminal in `C:\Users\nidhi\.gemini\antigravity\scratch\autoqa` and run:

```bash
# Add your GitHub repository as origin
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/AutoQA.git

# Set default branch to main
git branch -M main

# Push code to GitHub
git push -u origin main
```

---

## ☁️ Step 2: Deployment Options

AutoQA consists of two interdependent services:
- **Frontend**: Next.js 14 App Router (React, Tailwind CSS, WebSockets client)
- **Backend**: FastAPI API Gateway + Microsoft Playwright (Chromium Headless Sandbox) + Gemini AI Vision Agent

---

### Option A: Free Cloud Deployment (Recommended)
Deploy the **Frontend to Vercel** and the **Backend to Render or Railway**.

#### 1. Deploy Backend (FastAPI + Playwright Docker) on Render / Railway
Because Playwright requires Chromium and Linux rendering libraries, the backend runs in a Docker container using Microsoft's official Playwright base image (`mcr.microsoft.com/playwright/python:v1.44.0-jammy`).

##### On Render:
1. Go to [dashboard.render.com](https://dashboard.render.com) and click **New + > Web Service**.
2. Connect your GitHub repository: `AutoQA`.
3. Select **Docker** environment.
   - **Root Directory**: `backend`
   - **Dockerfile Path**: `Dockerfile`
4. In **Environment Variables**, add:
   - `GEMINI_API_KEY`: *Your Google Gemini API Key*
   - `HEADLESS`: `true`
   - `DEFAULT_MODEL`: `gemini-1.5-flash`
   - `PROJECT_NAME`: `AutoQA Engine`
5. Click **Create Web Service**.
6. Once deployed, copy your backend URL (e.g., `https://autoqa-backend.onrender.com`).

##### Or On Railway:
1. Go to [railway.app](https://railway.app) and create a **New Project > Deploy from GitHub repo**.
2. Set root directory to `backend`.
3. Add the `GEMINI_API_KEY` environment variable.
4. Copy the assigned public URL.

#### 2. Deploy Frontend (Next.js 14) on Vercel
1. Go to [vercel.com/new](https://vercel.com/new) and import your `AutoQA` repository.
2. In **Root Directory**, click edit and select `frontend`.
3. In **Environment Variables**, add:
   - `NEXT_PUBLIC_BACKEND_URL`: *Your deployed backend URL* (e.g. `https://autoqa-backend.onrender.com`)
   - `NEXT_PUBLIC_API_URL`: `https://autoqa-backend.onrender.com/api/v1`
   - `NEXT_PUBLIC_WS_URL`: `wss://autoqa-backend.onrender.com/api/v1/ws`
4. Click **Deploy**.
5. Your production studio will be live at `https://autoqa-<username>.vercel.app`!

---

### Option B: 1-Click Render Blueprint (`render.yaml`)
A `render.yaml` specification is included in the root directory.
1. Connect your repository on Render.
2. Click **New + > Blueprint**.
3. Select your repository. Render will automatically provision both `autoqa-backend` (Docker) and `autoqa-frontend` (Node.js) and wire their URLs together.

---

### Option C: Single-Server / VPS Deployment with Docker Compose
If deploying to an AWS EC2 instance, DigitalOcean Droplet, Linode, or any Linux VPS:

1. Clone your repository:
   ```bash
   git clone https://github.com/<YOUR_GITHUB_USERNAME>/AutoQA.git
   cd AutoQA
   ```

2. Create `.env` file in the root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. Launch all services:
   ```bash
   docker compose up -d --build
   ```

4. Both services are now running:
   - Frontend: `http://<SERVER_IP>:3000`
   - Backend API: `http://<SERVER_IP>:8000`
   - Swagger / OpenAPI Docs: `http://<SERVER_IP>:8000/docs`

---

## 🖥️ Local Demonstration Quickstart

To run the full stack locally for live demonstrations:

### Method 1: Using the Startup Scripts
Double-click or run from PowerShell:
```powershell
.\start_servers.ps1
```
Or command prompt:
```cmd
start_servers.bat
```

### Method 2: Manual Terminal Startup

**Terminal 1 — Backend**:
```powershell
cd backend
.\.venv\Scripts\python run.py
```
*API live at `http://localhost:8000` (docs at `http://localhost:8000/docs`)*

**Terminal 2 — Frontend**:
```powershell
cd frontend
npm run dev
```
*Studio live at `http://localhost:3000`*

---

## 🔑 Environment Variables Reference

### Backend (`backend/.env`)
| Variable | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | Yes | `""` | Google AI Studio Gemini API Key |
| `OPENAI_API_KEY` | No | `""` | Optional fallback provider |
| `DEFAULT_MODEL` | No | `gemini-1.5-flash` | Gemini model for vision reasoning |
| `HEADLESS` | No | `true` | Set to `false` for visible browser window |
| `DATABASE_URL` | No | `sqlite+aiosqlite:///./autoqa.db` | Async SQLAlchemy database URL |

### Frontend (`frontend/.env.local`)
| Variable | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `NEXT_PUBLIC_BACKEND_URL` | No | `http://localhost:8000` | Base URL of the FastAPI backend |
| `NEXT_PUBLIC_API_URL` | No | `http://localhost:8000/api/v1` | REST API v1 endpoint |
| `NEXT_PUBLIC_WS_URL` | No | `ws://localhost:8000/api/v1/ws` | Bi-directional WebSocket endpoint |
