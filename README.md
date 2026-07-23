# VLC Discord Share Tool

Share a specific monitor or window into Discord with proper audio routing — no OBS, no black screen issues.

## Features

- 🖥️ **Auto-detects all monitors** with resolution and position
- 🪟 **Pick any window** or specific monitor to capture
- 🎵 **Built-in audio routing** via VB-Audio Virtual Cable
- 🎮 **Stream Deck integration** for one-button start/stop
- 🔌 **Dummy plug support** for hidden virtual monitors
- ⚡ **Zero dependencies** in the standalone EXE (no Python needed)

## Quick Start

1. **Download** the latest [Release](https://github.com/YOUR_USERNAME/VLC-Discord-Share-Tool/releases)
2. **Install requirements** (see below)
3. **Run** `VLC Share Tool.exe`
4. **Configure** your monitor, audio, and window
5. **Share** to Discord!

## Installation

### Requirements (one-time setup)

- [VLC media player](https://www.videolan.org/vlc/) — free
- [VB-Audio Virtual Cable](https://vb-audio.com/Cable/) — free, for audio routing
- Windows 10/11

### Optional

- **Stream Deck** — for one-button start/stop
- **Dummy HDMI plug** (~$5) — for hidden virtual monitors

## Setup Guide

See [HOW TO USE.txt](Release/HOW TO USE.txt) for detailed 5-step instructions:

1. Install VLC + VB-Audio Virtual Cable
2. (Optional) Set up dummy plug / virtual monitor
3. Configure audio routing
4. Share to Discord
5. (Optional) Stream Deck integration

## Architecture

### `vlc_share_tool.py` — Main GUI
- tkinter dark theme
- Auto-detects monitors via `screeninfo` + `win32api`
- Lists open windows
- Saves config for headless mode
- Launches VLC with proper coordinate transforms

### `vlc_share_ctl.py` — Stream Deck CLI
- Reads saved config
- Starts/stops/toggles VLC via PID
- No dependencies — pure Python stdlib + `ctypes`

## Build

```bash
pip install -r requirements.txt
.\build.bat
```

Outputs:
- `dist\VLC Share Tool.exe` — Standalone GUI
- `dist\vlc_share_ctl.exe` — Standalone CLI

## Known Issues

- **Audio endpoints**: VLC's `--mmdevice-audio-device` may need GUID instead of friendly name
- **Qt screen ordering**: Edge cases with multiple displays
- **First run**: GUI must run first to generate `config.json` before CLI works

## License

MIT

## Credits

Built for dummy plug streaming and Discord screen sharing.
