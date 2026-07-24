# Discord VLC Audio Share

**The missing piece for Discord screen sharing with virtual audio and dummy monitors.**

## The Problem

You want to stream a specific monitor or window to Discord with **complete audio control**. But Discord has issues:

- ❌ **"Share System Audio"** doesn't work properly with Discord's native screenshare
- ❌ **No audio routing** — apps dump to your default device, friends hear nothing, you hear everything
- ❌ **Multiple monitors** — Discord's full-screen capture gets the wrong one or creates a black screen
- ❌ **Dummy plugs** — Windows detects your virtual HDMI monitor, but Discord doesn't capture it cleanly
- ❌ **VB-Audio Virtual Cable** — Great for routing, but Discord can't see that audio path

## The Solution

**Discord VLC Audio Share** — A Windows GUI that:

1. **Captures exactly what you want** — Pick any monitor or open window
2. **Routes audio properly** — VB-Audio Virtual Cable funnels app audio into VLC
3. **Outputs to Discord** — Share the VLC window (not your screen) for clean, controllable streaming
4. **Works with dummy plugs** — Virtual monitors show up and capture perfectly
5. **One-button control** — Stream Deck integration for start/stop

## How It Works

```
Your App (Spotify, YouTube, etc.)
    ↓ (output to CABLE Input)
VB-Audio Virtual Cable
    ↓ (CABLE Output)
VLC (capturing monitor/window)
    ↓ (sends to Discord as application window)
Discord Voice Channel
    ↓
Friends hear your audio + see your screen
```

## Installation

### Requirements (one-time)

- **Windows 10/11**
- **[VLC media player](https://www.videolan.org/vlc/)** — free
- **[VB-Audio Virtual Cable](https://vb-audio.com/Cable/)** — free
  - Creates `CABLE Input` (virtual speaker) and `CABLE Output` (virtual mic)
  - Install and reboot if prompted

### Optional

- **[Stream Deck](https://www.elgato.com/stream-deck)** — one-button start/stop
- **Dummy HDMI dongle** (~$5–10) — for hidden/additional virtual monitors

## Quick Start

1. **Download** [Latest Release](https://github.com/YOUR_USERNAME/Discord-VLC-Audio-Share/releases)
2. **Extract ZIP** to a folder
3. **Run** `VLC Share Tool.exe`
4. **Pick your monitor** from the list
5. **Set audio**:
   - **Audio In** → `CABLE Output` (VLC reads from here)
   - **Audio Out** → Your headphones/speakers (so you can monitor)
6. **Click Launch VLC**
7. In Discord: **Share Screen** → **Application Window** → **VLC** → **Go Live**

## Full Setup Guide

See [HOW TO USE.txt](Release/HOW%20TO%20USE.txt) for detailed instructions on:
- Audio routing with VB-Audio Virtual Cable
- Dummy plug / virtual monitor setup
- Stream Deck integration
- Troubleshooting

## Key Features

### Monitor/Desktop Capture
- Auto-detects all monitors (any resolution, any layout)
- Shows resolution, position, and primary status
- Pick which monitor to capture and stream
- Auto-selects largest non-primary (usually your dummy plug)
- **Captures the entire desktop on that monitor** — whatever's on-screen goes to Discord

### Audio Routing
- Reads all VB-Audio devices from Windows registry
- Configures VLC to capture from `CABLE Output`
- Outputs back to your monitoring device (your headphones/speakers)
- Any app's audio that you route to `CABLE Input` will flow through VLC to Discord

### Persistent Config
- Save settings once → use Stream Deck forever
- `config.json` stores all preferences
- Headless mode: `vlc_share_ctl.exe toggle` / `start` / `stop`

### Stream Deck Integration
Both EXEs must be in the same folder:
- **One-button toggle**: `vlc_share_ctl.exe toggle` (start if stopped, stop if running)
- **Separate buttons**: `vlc_share_ctl.exe start` / `vlc_share_ctl.exe stop`

## Architecture

### `vlc_share_tool.py` — Configuration GUI
- tkinter, dark Catppuccin theme
- Monitor detection via `screeninfo` + `win32api`
- Audio device enumeration via Windows registry
- Calculates VLC coordinate transforms (critical for multi-monitor setups)
- Saves `config.json` for headless operation

### `vlc_share_ctl.py` — Stream Deck CLI
- Reads `config.json`
- Starts/stops VLC by PID
- Pure Python — no additional dependencies beyond stdlib

## Build From Source

```bash
pip install -r requirements.txt
.\build.bat
```

Generates:
- `dist\VLC Share Tool.exe` — Standalone GUI (no Python needed)
- `dist\vlc_share_ctl.exe` — Standalone CLI (no Python needed)

## Known Issues & Workarounds

| Issue | Cause | Fix |
|-------|-------|-----|
| No audio in Discord | VLC doesn't read from CABLE Output, or app doesn't output to CABLE Input | Check Audio In setting, verify app output device in Windows Sound Settings |
| Wrong monitor captured | Multi-monitor coordinate transform issue | Click Refresh, re-select monitor, click Launch again |
| VLC window is black | VLC needs time to initialize | Wait 2–3 seconds, click inside the VLC window |
| Stream Deck button does nothing | Config not generated yet | Run GUI first, click Launch once to create `config.json` |
| Dummy plug not detected | Driver issue or DisplayPort adapter not recognized | Unplug and replug, check Windows Device Manager |

## Why This Exists

Discord's native screen-share + system audio doesn't work well for:
- **Virtual audio routing** (VB-Audio, Voicemeeter, etc.)
- **Multiple/virtual monitors** (dummy plugs, vNIC adapters)
- **Controlled audio paths** (you need app audio in, but not monitor audio)

VLC as an intermediary solves all of these because:
- It can capture any rectangle on screen
- It can read from any audio device (including virtual cables)
- Discord can share VLC's window cleanly
- No black-screen issues

## License

MIT

## Contributing

Found a bug? Want to improve monitor detection? Submit an issue or PR!

---

**Pro tip**: After you get it working once, you never have to touch the GUI again. Just hit your Stream Deck button. That's the whole point.

