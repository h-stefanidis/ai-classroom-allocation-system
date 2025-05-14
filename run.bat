@echo off
echo Running download_dependencies.py...
python download_dependencies.py
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to run download_dependencies.py
    exit /b %ERRORLEVEL%
)

echo Installing frontend dependencies...
cd frontend
call npm install
IF %ERRORLEVEL% NEQ 0 (
    echo npm install failed
    exit /b %ERRORLEVEL%
)

echo Starting frontend...
call npm run start
