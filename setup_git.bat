@echo off
echo Setting up Git for ICT Scanner Project
echo.

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo Git is not installed. Please install Git from https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git is installed. Setting up repository...
echo.

REM Initialize Git repository
git init

REM Add all files
git add .

REM Make initial commit
git commit -m "Initial commit: ICT PD Array Scanner"

echo.
echo Git repository initialized successfully!
echo.
echo Next steps:
echo 1. Create a repository on GitHub
echo 2. Run: git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
echo 3. Run: git push -u origin main
echo.
pause 