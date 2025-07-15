@echo off
setlocal enabledelayedexpansion

echo FastAPI Development Helper

if "%1"=="deps" goto check_deps
if "%1"=="install" goto install_reqs
if "%1"=="setup" goto setup_all
if "%1"=="dev" goto run_dev
if "%1"=="test" goto run_tests
if "%1"=="docker" goto run_docker
goto usage

:check_deps
echo Checking dependencies...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed
    exit /b 1
)
pip --version >nul 2>&1
if errorlevel 1 (
    echo pip is not installed
    exit /b 1
)
echo Dependencies OK
goto :eof

:install_reqs
echo Installing requirements...
pip install -r requirements.txt
echo Requirements installed
goto :eof

:setup_all
call :check_deps
call :install_reqs
echo Setting up database...
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
echo Database setup complete
goto :eof

:run_dev
echo Starting development server...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
goto :eof

:run_tests
echo Running tests...
pytest tests/ -v
echo Tests completed
goto :eof

:run_docker
echo Starting with Docker...
docker-compose up --build
goto :eof

:usage
echo Usage: %0 {deps^|install^|setup^|dev^|test^|docker}
echo.
echo Commands:
echo   deps    - Check dependencies
echo   install - Install Python requirements
echo   setup   - Full setup (install + database)
echo   dev     - Run development server
echo   test    - Run tests
echo   docker  - Run with Docker Compose
exit /b 1
