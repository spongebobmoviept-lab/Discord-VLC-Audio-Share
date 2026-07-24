@echo off
REM ======================================
REM VLC Share Tool - Vencord Plugin Setup
REM ======================================

setlocal enabledelayedexpansion

set "VENCORD_PATH=%APPDATA%\Vencord\src\userplugins"
set "PLUGIN_FILE=%~dp0VLCShareVencord.tsx"

echo.
echo ====================================
echo VLC Share - Vencord Plugin Installer
echo ====================================
echo.

if not exist "%PLUGIN_FILE%" (
    echo ERROR: VLCShareVencord.tsx not found in %~dp0
    echo Make sure this script is in the same folder as the tool files.
    pause
    exit /b 1
)

echo Creating Vencord plugins folder...
if not exist "%VENCORD_PATH%" (
    mkdir "%VENCORD_PATH%" >nul
    echo   Created: %VENCORD_PATH%
) else (
    echo   Found: %VENCORD_PATH%
)

echo.
echo Installing VLC Share plugin...
copy /Y "%PLUGIN_FILE%" "%VENCORD_PATH%\" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy plugin file
    pause
    exit /b 1
)

echo   ✓ Plugin installed successfully
echo.
echo Next steps:
echo   1. Restart Discord completely (close it fully, then reopen)
echo   2. In Discord, open Vencord settings (gear icon in bottom left)
echo   3. Go to Plugins tab
echo   4. Find "VLC Share Tool" and enable it
echo.
echo Commands available:
echo   /vlc_share    - Open VLC Share Tool GUI
echo   /vlc_toggle   - Start/stop VLC stream
echo.
pause
