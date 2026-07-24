# Discord VLC Audio Share

**The missing piece for Discord screen sharing with virtual audio, dummy monitors, and app windows.**

## The Problem

You want to stream a specific monitor, window, or app to Discord with **complete audio control**. But Discord has issues:

- ❌ **"Share System Audio"** doesn't work properly with Discord's native screenshare
- ❌ **No audio routing** — apps dump to your default device, friends hear nothing, you hear everything
- ❌ **Multiple monitors** — Discord's full-screen capture gets the wrong one or creates a black screen
- ❌ **App windows** — Can't cleanly capture individual app windows with proper audio
- ❌ **Dummy plugs** — Windows detects your virtual HDMI monitor, but Discord doesn't capture it cleanly
- ❌ **VB-Audio Virtual Cable** — Great for routing, but Discord can't see that audio path

## The Solution

**Discord VLC Audio Share** — A Windows GUI that:

1. **Captures exactly what you want** — Pick any monitor OR any open app window
2. **Routes audio properly** — VB-Audio Virtual Cable funnels app audio into VLC
3. **Outputs to Discord** — Share the VLC window (not your screen) for clean, controllable streaming
4. **Works with dummy plugs** — Virtual monitors show up and capture perfectly
5. **Works with app windows** — Stream Spotify, YouTube, games, OBS, whatever
6. **One-button control** — Stream Deck integration for start/stop

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

### Optional (Recommended for One-Click Streaming)

- **[Vencord](https://vencord.dev/)** — Discord mod, free
  - Enables plugin that hijacks "Share Screen" button
  - Makes streaming one-click instead of multi-step
  - Not required, but highly recommended
- **[Stream Deck](https://www.elgato.com/stream-deck)** — button hardware, ~$100
  - Physical button for start/stop
- **Dummy HDMI dongle** — virtual monitor, ~$5–10

## Quick Start

### Option A: Vencord Plugin (Recommended - One-Click Streaming)

If you have **[Vencord](https://vencord.dev/)** installed:

1. **Download** [Latest Release](https://github.com/spongebobmoviept-lab/Discord-VLC-Audio-Share/releases)
2. **Extract ZIP** to a folder
3. **Run** `VLC Share Tool.exe` once to configure and test
4. **Copy** `VLCShare.tsx` to `%APPDATA%\Vencord\src\userplugins\`
5. **Restart Discord**
6. **Enable plugin**: Vencord Settings → Plugins → "VLC Share" → toggle ON
7. **Stream**: In Discord, click **"Share Screen"** → VLC launches automatically → Select **"Application Window"** → **"VLC"** → **"Go Live"**

That's it! Now clicking "Share Screen" always launches VLC with your saved settings.

### Option B: Manual (Without Vencord)

1. **Download** [Latest Release](https://github.com/spongebobmoviept-lab/Discord-VLC-Audio-Share/releases)
2. **Extract ZIP** to a folder
3. **Run** `VLC Share Tool.exe`
4. **Choose what to capture**:
   - **Monitors tab** → Pick a monitor (e.g., dummy plug, virtual monitor, second display)
   - **Windows tab** → Pick an app window (e.g., Spotify, YouTube, game, OBS)
5. **Set audio**:
   - **Audio In** → `CABLE Output` (VLC reads from the virtual cable)
   - **Audio Out** → `(none)` (so you don't hear audio bleeding through your speakers)
6. **Click Launch VLC**
7. In Discord: **Share Screen** → **Application Window** → **VLC** → **Go Live**

## Full Setup Guide

See [SETUP_INSTRUCTIONS.txt](Release/SETUP_INSTRUCTIONS.txt) for detailed instructions on:
- Installing prerequisites (VLC, VB-Audio, Vencord)
- Audio routing with VB-Audio Virtual Cable
- Vencord plugin setup and configuration
- Dummy plug / virtual monitor setup
- Stream Deck integration
- Troubleshooting

## Key Features

### ⚡ Vencord Plugin - Share Screen Button Hijack (NEW!)
When Vencord plugin is installed, clicking "Share Screen" in Discord automatically:
1. Launches VLC with your pre-configured settings
2. Waits for you to select "Application Window" → "VLC"
3. One-click streaming to Discord!

**To your viewers**: Looks like you're sharing a desktop
**Actually**: It's your perfectly-routed VLC stream with zero audio issues

### Monitor/Desktop Capture
- Auto-detects all monitors (any resolution, any layout)
- Shows resolution, position, and primary status
- Pick which monitor to capture and stream
- Auto-selects largest non-primary (usually your dummy plug)
- **Captures the entire desktop on that monitor** — whatever's on-screen goes to Discord

### App Window Capture
- Lists all visible open windows
- Pick any window: Spotify, YouTube, OBS, games, etc.
- Captures just that window — no desktop clutter

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

**Two ways to use with Stream Deck:**

#### Method 1: Direct Control (Works without Vencord)
Set up Stream Deck buttons for full control:
- **Button 1**: `vlc_share_ctl.exe start` — Launch VLC
- **Button 2**: `vlc_share_ctl.exe stop` — Stop VLC
- **Button 3**: `vlc_share_ctl.exe toggle` — Start if stopped, stop if running

Then manually click "Share Screen" in Discord when you want to stream.

#### Method 2: Vencord + Stream Deck (Recommended)
With Vencord plugin installed, use Stream Deck to launch VLC, then:
1. **Stream Deck button**: `vlc_share_ctl.exe toggle` — Launches VLC with your saved settings
2. **In Discord**: Click **"Share Screen"** 
3. **Vencord plugin** automatically detects it and launches VLC (if not already running)
4. **Select**: Application Window → VLC → Go Live

OR skip the Stream Deck button and just:
- Click "Share Screen" in Discord directly
- Vencord plugin launches VLC automatically
- Done!

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

