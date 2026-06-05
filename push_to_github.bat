@echo off
setlocal ENABLEDELAYEDEXPANSION
cd /d "C:\Users\gt102120\Downloads\TrainingTracker"

echo ==============================================
echo   Push to GitHub (kanagurm/training-tracker)
echo ==============================================
echo.

if not exist "app.py" (
  echo [ERROR] app.py not found. Wrong folder.
  pause
  exit /b 1
)

REM Init git if needed
if not exist ".git" (
  echo Initializing git...
  git init
  git branch -M main
)

REM Stage and commit all changes
echo Staging files...
git add -A
git status --short
git diff --cached --quiet
if %errorlevel%==0 (
  echo Nothing new to commit. Will still push.
) else (
  git commit -m "Update Training Tracker"
  if errorlevel 1 (
    echo [ERROR] Commit failed.
    pause
    exit /b 1
  )
)

REM Set or update remote
git remote get-url origin >nul 2>nul
if errorlevel 1 (
  echo Adding GitHub remote...
  git remote add origin https://github.com/kanagurm/training-tracker.git
) else (
  echo Updating GitHub remote...
  git remote set-url origin https://github.com/kanagurm/training-tracker.git
)

REM Push
echo.
echo Pushing to GitHub...
git push -u origin main
if errorlevel 1 (
  echo.
  echo [ERROR] Push failed. Likely cause: GitHub authentication.
  echo.
  echo SOLUTION: Run this in a terminal:
  echo   git config --global credential.helper manager
  echo Then try this bat file again.
  pause
  exit /b 1
)

echo.
echo =============================================
echo SUCCESS! Live at:
echo https://github.com/kanagurm/training-tracker
echo =============================================
echo.
pause
endlocal
