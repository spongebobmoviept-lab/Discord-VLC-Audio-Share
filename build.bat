@echo off
title VLC Share Tool — Build
echo ================================================
echo  VLC Share Tool + Stream Deck CTL — EXE Builder
echo ================================================
echo.

echo [1/4] Installing dependencies...
python -m pip install pyinstaller screeninfo pywin32 --quiet
if errorlevel 1 (
    echo ERROR: pip install failed. Make sure Python is in PATH.
    pause
    exit /b 1
)

echo [2/4] Building main GUI exe...
python -m PyInstaller ^
  --onefile ^
  --windowed ^
  --name "VLC Share Tool" ^
  --collect-all screeninfo ^
  --hidden-import win32gui ^
  --hidden-import win32api ^
  --hidden-import win32com ^
  --hidden-import win32com.client ^
  vlc_share_tool.py

if errorlevel 1 (
    echo ERROR: PyInstaller failed on vlc_share_tool.py. See output above.
    pause
    exit /b 1
)

echo [3/4] Building Stream Deck companion exe...
python -m PyInstaller ^
  --onefile ^
  --windowed ^
  --name "vlc_share_ctl" ^
  vlc_share_ctl.py

if errorlevel 1 (
    echo ERROR: PyInstaller failed on vlc_share_ctl.py. See output above.
    pause
    exit /b 1
)

echo [4/4] Done!
echo.
echo   Main GUI:        dist\VLC Share Tool.exe
echo   Stream Deck CTL: dist\vlc_share_ctl.exe
echo.
echo   HOW TO SET UP STREAM DECK:
echo     1. Put BOTH exes in the same folder.
echo     2. Open "VLC Share Tool.exe", configure and hit Launch once.
echo     3. In Stream Deck add a "System: Open" action.
echo     4. Point it at:  vlc_share_ctl.exe toggle
echo     5. Button now starts/stops VLC with one press.
echo.
pause
