@echo off
setlocal
cd /d "%~dp0"

echo ==============================================
echo   Build EXE - Training Tracker
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

echo Installing build dependencies...
%PY% -m pip install --upgrade pip
%PY% -m pip install pyinstaller streamlit pandas plotly openpyxl
if errorlevel 1 (
  echo [ERROR] Dependency installation failed.
  pause
  exit /b 1
)

echo.
echo Building EXE...
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed --name TrainingTracker --collect-all streamlit --collect-all plotly app.py
if errorlevel 1 (
  echo [ERROR] EXE build failed.
  pause
  exit /b 1
)

echo.
echo Build complete: dist\TrainingTracker.exe
echo.
pause
endlocal
