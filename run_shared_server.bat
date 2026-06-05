@echo off
setlocal
set "APP_DIR=%USERPROFILE%\Downloads\TrainingTracker"
if not exist "%APP_DIR%\app.py" (
  set "APP_DIR=%USERPROFILE%\Downloads\TrainingTracker_Build"
)
if not exist "%APP_DIR%\app.py" (
  echo [ERROR] Could not find app.py.
  pause
  exit /b 1
)
cd /d "%APP_DIR%"

echo ==============================================
echo   Training Tracker Shared Server
echo ==============================================
echo This exposes app to your network.
echo Keep this window open while users access the app.
echo.

if exist "venv\Scripts\python.exe" (
  set "PY=venv\Scripts\python.exe"
) else (
  where py >nul 2>nul
  if %errorlevel%==0 (
    set "PY=py"
  ) else (
    set "PY=python"
  )
)

%PY% -m pip show streamlit >nul 2>nul || %PY% -m pip install streamlit pandas plotly openpyxl

%PY% -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
endlocal
