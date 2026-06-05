@echo off
setlocal ENABLEDELAYEDEXPANSION
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
echo   Employee Training Tracker
echo ==============================================
echo.

if exist "venv\Scripts\python.exe" (
  set "PY=venv\Scripts\python.exe"
) else (
  where py >nul 2>nul
  if %errorlevel%==0 (
    set "PY=py"
  ) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
      set "PY=python"
    ) else (
      echo [ERROR] Python not found. Install Python 3.10+ and add to PATH.
      pause
      exit /b 1
    )
  )
)

echo Checking dependencies...
%PY% -m pip show streamlit >nul 2>nul || %PY% -m pip install streamlit
%PY% -m pip show pandas >nul 2>nul || %PY% -m pip install pandas
%PY% -m pip show plotly >nul 2>nul || %PY% -m pip install plotly
%PY% -m pip show openpyxl >nul 2>nul || %PY% -m pip install openpyxl
%PY% -m pip show sqlalchemy >nul 2>nul || %PY% -m pip install sqlalchemy

echo.
echo Starting app at http://localhost:8501
echo Keep this window open while using the app.
echo.
%PY% -m streamlit run app.py

echo.
echo App stopped. Press any key to close.
pause
endlocal
