@echo off
echo ========================================
echo   Resetting Chorus Database
echo ========================================
echo.
echo This will delete all data and recreate the database with the latest schema.
echo.
pause

cd "Flask Server"

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Deleting old database...
rem Handle if a directory named chorus.db exists (conflicts with SQLite file)
if exist chorus.db\NUL (
    echo Found directory named chorus.db - removing directory...
    rmdir /s /q chorus.db
) else (
    if exist chorus.db del /q /f chorus.db
)
echo.

echo Deleting old vector store...
if exist chroma_data rmdir /s /q chroma_data
echo.

echo Deleting uploaded files...
if exist uploads rmdir /s /q uploads
echo.

echo Recreating database with new schema...
python -c "from database import init_db; init_db()"

echo.
echo ========================================
echo   Database Reset Complete!
echo ========================================
echo.
echo Please restart your Flask server.
echo.
pause

