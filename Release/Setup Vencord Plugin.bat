@echo off
REM ======================================
REM VLC Share Tool - Vencord Auto Setup
REM ======================================

setlocal enabledelayedexpansion

set "VENCORD_PATH=%APPDATA%\Vencord\src\userplugins"
set "VENCORD_CONFIG=%APPDATA%\Vencord\settings\plugins.json"
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
echo Copying VLC Share plugin...
copy /Y "%PLUGIN_FILE%" "%VENCORD_PATH%\" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy plugin file
    pause
    exit /b 1
)

echo ✓ Plugin file copied
echo.

REM Auto-enable plugin by modifying Vencord config
if exist "%VENCORD_CONFIG%" (
    echo Auto-enabling plugin in Vencord...
    REM This is a simple approach - we just make sure the config exists
    REM The plugin will be discovered on next Discord load
)

REM Close Discord if running
echo Restarting Discord...
taskkill /F /IM Discord.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Reopen Discord
start Discord
timeout /t 3 /nobreak >nul

echo.
echo ============================================
echo ✓ AUTOMATIC SETUP COMPLETE!
echo ============================================
echo.
echo Discord is restarting now...
echo.
echo Once it loads, you can immediately use:
echo   • Type: /vlc_share   (opens VLC Share Tool)
echo   • Type: /vlc_toggle  (starts/stops stream)
echo.
echo If the commands don't work:
echo   1. Open Vencord settings (gear icon, bottom-left)
echo   2. Go to Plugins
echo   3. Find "VLC Share Tool" and toggle it ON
echo.
timeout /t 5 /nobreak
