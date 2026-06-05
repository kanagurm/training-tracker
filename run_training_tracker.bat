@echo off
setlocal
cd /d "%~dp0"

echo ==============================================
echo   Employee Training Tracker - Launcher
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
      echo [ERROR] Python not found in PATH.
      pause
      exit /b 1
    )
  )
)

if not exist "app.py" (
  echo [ERROR] app.py not found in this folder.
  pause
  exit /b 1
)

echo Checking dependencies...
%PY% -m pip show streamlit >nul 2>nul || %PY% -m pip install streamlit
%PY% -m pip show pandas >nul 2>nul || %PY% -m pip install pandas
%PY% -m pip show plotly >nul 2>nul || %PY% -m pip install plotly
%PY% -m pip show openpyxl >nul 2>nul || %PY% -m pip install openpyxl

echo.
echo Starting app at http://localhost:8501
%PY% -m streamlit run app.py

if errorlevel 1 (
  echo.
  echo [ERROR] App exited with an error.
  pause
)
endlocal
