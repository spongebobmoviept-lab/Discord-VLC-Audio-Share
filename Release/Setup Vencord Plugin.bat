@echo off
REM ======================================
REM VLC Share Tool - Vencord Auto Setup
REM ======================================

setlocal enabledelayedexpansion

set "VENCORD_PATH=%APPDATA%\Vencord\src\userplugins"
set "PLUGIN_FILE=%~dp0VLCShareVencord.tsx"

echo.
echo ============================================
echo VLC Share - Automatic Vencord Setup
echo ============================================
echo.

REM Check if plugin file exists
if not exist "%PLUGIN_FILE%" (
    echo ERROR: VLCShareVencord.tsx not found in %~dp0
    echo Make sure this script is in the same folder as the tool files.
    pause
    exit /b 1
)

REM Create Vencord plugins folder if it doesn't exist
if not exist "%VENCORD_PATH%" (
    echo Creating Vencord plugins folder...
    mkdir "%VENCORD_PATH%"
    if errorlevel 1 (
        echo ERROR: Could not create folder
        pause
        exit /b 1
    )
)

REM Copy plugin file
echo Copying VLC Share plugin to: %VENCORD_PATH%
copy /Y "%PLUGIN_FILE%" "%VENCORD_PATH%\" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy plugin file
    pause
    exit /b 1
)

echo ✓ Plugin file copied
echo.

REM Give file system time to sync
timeout /t 2 /nobreak >nul

REM Close Discord if running
echo Closing Discord completely...
taskkill /F /IM Discord.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Reopen Discord
echo Starting Discord...
start Discord

REM Wait for Discord to fully load
echo Waiting for Discord to load...
timeout /t 8 /nobreak >nul

echo.
echo ============================================
echo ✓ SETUP COMPLETE!
echo ============================================
echo.
echo Discord should now show Vencord in the sidebar.
echo.
echo Plugin should be ready to use:
echo   • Type: /vlc_share   (opens VLC Share Tool)
echo   • Type: /vlc_toggle  (starts/stops stream)
echo.
echo If you don't see the plugin or commands don't work:
echo   1. Open Vencord settings (gear icon, bottom-left of Discord)
echo   2. Click Plugins
echo   3. Search for "VLC" - you should see "VLC Share Tool"
echo   4. Toggle it ON (turn blue)
echo   5. Close settings
echo   6. Try typing /vlc_share again
echo.
echo If still missing: you may need to restart Discord manually
echo.
pause
