@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo Starting Kelp Project Locally
echo ==========================================

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b
)

REM Check for Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    pause
    exit /b
)

echo.
echo [1/4] Setting up Backend...
cd backend

if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing backend dependencies (this may take a while)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install backend dependencies.
    pause
    exit /b
)

REM Set Environment Variables
set USE_LOCAL_STORAGE=True
set CELERY_TASK_ALWAYS_EAGER=True
set DATABASE_URL=sqlite:///./data/kelp.db

REM Ensure data directory exists
if not exist "data" mkdir data

echo Starting Backend Server...
start "Kelp Backend" cmd /k "title Kelp Backend && venv\Scripts\activate && set USE_LOCAL_STORAGE=True && set CELERY_TASK_ALWAYS_EAGER=True && set DATABASE_URL=sqlite:///./data/kelp.db && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo [2/4] Setting up Frontend...
cd ..\frontend\frontend

echo Installing frontend dependencies...
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install frontend dependencies.
    pause
    exit /b
)

echo Starting Frontend Dev Server...
start "Kelp Frontend" cmd /k "title Kelp Frontend && npm run dev"

echo.
echo ==========================================
echo Application is starting!
echo Backend API: http://localhost:8000/docs
echo Frontend UI: http://localhost:5173
echo ==========================================
echo.
pause
