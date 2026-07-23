# VLC Discord Share Tool — Session Handoff

## What this project is
A Windows GUI tool that captures a specific monitor or window and streams it
into Discord via VLC, with proper audio routing. Designed for dummy plug / 
virtual monitor use cases. Packaged as a self-contained EXE (no Python needed).

## Project location
`D:\Downloads\VLC Discord audio Sharing Fix\`

## Files
| File | Purpose |
|------|---------|
| `vlc_share_tool.py` | Main GUI app (tkinter) |
| `vlc_share_ctl.py` | Stream Deck CLI companion (start/stop/toggle VLC) |
| `build.bat` | Builds both EXEs via PyInstaller |
| `requirements.txt` | screeninfo, pywin32, pyinstaller |
| `Release\VLC Share Tool.exe` | Built GUI (no dependencies) |
| `Release\vlc_share_ctl.exe` | Built Stream Deck companion |
| `Release\HOW TO USE.txt` | User-facing setup guide |
| `VLC-Discord-Share-Tool.zip` | Shareable zip of Release folder |

## Architecture

### vlc_share_tool.py
- tkinter GUI, dark Catppuccin Mocha theme
- **Monitors tab**: detects all monitors via screeninfo + win32api, auto-selects
  largest non-primary (likely dummy plug). Populates "VLC opens on:" dropdown.
- **Windows tab**: enumerates visible top-level windows via win32gui
- **Audio dropdowns**: reads HKLM MMDevices registry for capture + render endpoints
- **Fullscreen checkbox** + **VLC opens on:** combobox (--qt-fullscreen-screennumber)
- On Launch: saves config.json + vlc.pid next to exe for ctl script
- Stop button: kills by PID from vlc.pid file using ctypes TerminateProcess
- Config load/save: json, persists fps/audio/fullscreen settings across runs

### Key VLC coordinate fix
VLC's `--screen-left` and `--screen-top` are offsets from the **virtual desktop
origin** (leftmost/topmost point across all monitors), NOT absolute Windows
screen coordinates. Must subtract `min(monitor.x)` and `min(monitor.y)`.

Example with 3 monitors:
  DISPLAY3: 1920x1080 at (-1920, 0)   ← far left
  DISPLAY2: 2560x1440 at (0, 0)       ← primary (middle)  
  DISPLAY1: 1920x1080 at (2560, 0)    ← far right

  Virtual desktop origin = (-1920, 0)
  To capture DISPLAY2 (0,0): --screen-left=1920 --screen-top=0

### vlc_share_ctl.py  
- Reads config.json for VLC launch params (pre-computed vlc_left/vlc_top)
- Checks if VLC is alive via ctypes OpenProcess(SYNCHRONIZE)
- toggle = start if dead, stop if alive
- No Python dependencies — pure stdlib + ctypes

### VLC detection
Both files use `find_vlc()` which checks:
1. HKLM\SOFTWARE\VideoLAN\VLC (registry default value = path to vlc.exe)
2. HKLM\SOFTWARE\WOW6432Node\VideoLAN\VLC
3. HKCU variants
4. Hardcoded common paths as fallback

### Shared files (written next to exe)
- `config.json` — last launch settings (vlc_left, vlc_top, w, h, fps, audio_in, audio_out, fullscreen, vlc_screen)
- `vlc.pid` — PID of running VLC process

## Dependencies
- `screeninfo` — monitor detection
- `pywin32` (win32gui, win32api, win32com.client) — window enum, shortcuts, monitor info
- `winreg` — built-in, used for audio device + VLC detection
- `tkinter` — built-in, UI
- `ctypes` — built-in, process kill

## Build
```
cd "D:\Downloads\VLC Discord audio Sharing Fix"
python -m PyInstaller --onefile --windowed --name "VLC Share Tool" \
  --collect-all screeninfo --hidden-import win32gui --hidden-import win32api \
  --hidden-import win32com --hidden-import win32com.client vlc_share_tool.py

python -m PyInstaller --onefile --console --name "vlc_share_ctl" vlc_share_ctl.py
```

## Known issues / things to still verify
- `--mmdevice-audio-device` for audio output: VLC's mmdevice module may need
  the endpoint GUID rather than friendly name. If audio out doesn't work,
  removing that arg and setting output in VLC prefs manually is the fallback.
- `--qt-fullscreen-screennumber` index mapping may differ between Qt screen
  ordering and Windows monitor ordering in edge cases.
- First run on a new machine: user must launch GUI first to generate config.json
  before vlc_share_ctl.exe will work.
