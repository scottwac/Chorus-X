@echo off
echo ========================================
echo   Starting Chorus Flask Server
echo ========================================
echo.

REM Change to script directory first
cd /d "%~dp0"

cd /d "Flask Server"

echo [1/4] Checking for virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    echo Running: python -m venv venv
    python -m venv venv
    echo Virtual environment created successfully!
) else (
    echo Virtual environment already exists.
)

echo.
echo [2/4] Activating virtual environment...
echo Running: venv\Scripts\activate
call venv\Scripts\activate
echo Virtual environment activated!

echo.
echo [3/4] Installing/updating dependencies...
echo Running: pip install -r requirements.txt
echo.
pip install -r requirements.txt
echo.
echo Dependencies installed successfully!

echo.
echo [4/4] Initializing database and starting Flask server...
echo ========================================
echo   Flask Server Starting on Port 5000
echo   API: http://localhost:5000
echo ========================================
echo.

python app.py

pause

