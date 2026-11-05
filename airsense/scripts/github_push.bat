@echo off
REM ========================================================
REM AirSense — 1-Click GitHub Push & Backup Script
REM ========================================================
cd /d "%~dp0..\.."

echo.
echo ========================================================
echo   AirSense - 1-Click GitHub Backup & Push
echo ========================================================
echo.

REM Check if git is installed
where git >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git is not installed or not in PATH.
    pause
    exit /b 1
)

REM Check remote status
git remote -v | findstr "origin" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [SETUP] No GitHub remote repository configured yet.
    echo.
    echo Please create an empty repository on https://github.com/new
    echo Example URL: https://github.com/parmarkamal2005/airsense-capstone.git
    echo.
    set /p REPO_URL="Paste your GitHub repository URL here: "
    if "%REPO_URL%"=="" (
        echo [ERROR] No URL provided. Push aborted.
        pause
        exit /b 1
    )
    git remote add origin %REPO_URL%
    echo [OK] Remote 'origin' added: %REPO_URL%
    echo.
)

echo [1/3] Checking status and staging files...
git status -s

set /p COMMIT_MSG="Enter commit description (Press ENTER for default 'feat: project update'): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=feat: project update

git add .
git commit -m "%COMMIT_MSG%" 2>nul
IF %ERRORLEVEL% EQU 0 (
    echo [OK] Changes committed: %COMMIT_MSG%
) ELSE (
    echo [INFO] No new changes to commit (already up to date).
)

echo.
echo [2/3] Renaming branch to master...
git branch -M master

echo.
echo [3/3] Pushing to GitHub...
git push -u origin master

IF %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   [SUCCESS] Your code is safely backed up on GitHub!
    echo ========================================================
) ELSE (
    echo.
    echo [WARN] Push failed. If this is your first push with a personal access token:
    echo        1. Generate a token at: https://github.com/settings/tokens
    echo        2. Or use GitHub Desktop / VS Code credentials manager.
)

echo.
pause
