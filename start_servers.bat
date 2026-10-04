@echo off
echo =========================================
echo   Launching AutoQA Platform
echo =========================================

echo [1/2] Starting FastAPI Backend on http://localhost:8000...
start cmd /k "cd backend && .\.venv\Scripts\activate && python run.py"

timeout /t 2 /nobreak >nul

echo [2/2] Starting Next.js Frontend on http://localhost:3000...
start cmd /k "cd frontend && npm run dev"

echo.
echo AutoQA is booting up!
echo - Frontend: http://localhost:3000
echo - Backend Docs: http://localhost:8000/docs
echo =========================================
pause
