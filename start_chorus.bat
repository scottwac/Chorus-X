@echo off
echo ========================================
echo      Starting Chorus Platform
echo ========================================
echo.
echo This will start both the Flask Server and Frontend
echo.
echo Opening Flask Server in new window...
start "Chorus Flask Server" cmd /k start_server.bat

echo Waiting 5 seconds for server to initialize...
timeout /t 5 /nobreak > nul

echo Opening Frontend in new window...
start "Chorus Frontend" cmd /k start_frontend.bat

echo.
echo ========================================
echo   Chorus is starting!
echo   Flask Server: http://localhost:5000
echo   Frontend: http://localhost:3000
echo ========================================
echo.
echo Press any key to exit this window...
pause > nul

