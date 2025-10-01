@echo off
echo ========================================
echo   Starting Chorus Frontend
echo ========================================
echo.

echo [1/3] Navigating to frontend directory...
echo Current working directory: %CD%

REM Change to script directory first
cd /d "%~dp0"
echo Script location: %CD%

REM Now go to frontend
if exist "frontend\" (
    cd /d "frontend"
    echo Successfully navigated to: %CD%
) else (
    echo ERROR: Could not find frontend directory!
    echo Looking in: %CD%
    echo.
    echo Please make sure you are running this from the Chorus X folder.
    pause
    exit /b 1
)

REM Verify we're actually in the frontend directory
if not exist "package.json" (
    echo ERROR: Not in frontend directory! package.json not found.
    echo Current location: %CD%
    pause
    exit /b 1
)

echo.
echo [2/3] Checking for node_modules...
if not exist "node_modules" (
    echo Node modules not found. Installing dependencies...
    echo Running: npm install
    echo.
    npm install
    echo.
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: npm install failed!
        echo.
        echo Please check:
        echo - Node.js is installed (run: node --version)
        echo - npm is available (run: npm --version)
        pause
        exit /b 1
    )
    echo Dependencies installed successfully!
) else (
    echo Node modules already exist.
)

echo.
echo [3/3] Starting development server...
echo ========================================
echo   Frontend Starting on Port 3000
echo   URL: http://localhost:3000
echo ========================================
echo.

npm run dev

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start frontend!
    pause
    exit /b 1
)

pause

