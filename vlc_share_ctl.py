"""
vlc_share_ctl.py  —  Stream Deck companion for VLC Discord Share Tool
----------------------------------------------------------------------
Usage:
    vlc_share_ctl.exe start      Start VLC with the last saved config
    vlc_share_ctl.exe stop       Kill VLC
    vlc_share_ctl.exe toggle     Start if stopped, stop if running (default)

Stream Deck setup:
    1.  Open "VLC Share Tool" once, configure everything, hit Launch.
        (This saves config.json next to the exe automatically.)
    2.  In Stream Deck, add a "System: Open" action.
    3.  Point it at:  vlc_share_ctl.exe toggle
    4.  Done — one button starts/stops the share.
"""

import sys
import os
import json
import subprocess
import ctypes
from pathlib import Path

# ---------------------------------------------------------------------------
# Locate config + PID files next to this exe (or script in dev mode)
# ---------------------------------------------------------------------------
APP_DIR     = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
CONFIG_FILE = APP_DIR / "config.json"
PID_FILE    = APP_DIR / "vlc.pid"


def find_vlc() -> str | None:
    """Locate VLC on any Windows machine — registry first, then common paths."""
    import winreg
    for reg_root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for reg_path in (
            r"SOFTWARE\VideoLAN\VLC",
            r"SOFTWARE\WOW6432Node\VideoLAN\VLC",
        ):
            try:
                with winreg.OpenKey(reg_root, reg_path) as k:
                    path, _ = winreg.QueryValueEx(k, "")
                    if path and os.path.exists(path):
                        return path
            except OSError:
                pass
    for candidate in [
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\VideoLAN\VLC\vlc.exe"),
    ]:
        if os.path.exists(candidate):
            return candidate
    return None


VLC_PATH = find_vlc() or r"C:\Program Files\VideoLAN\VLC\vlc.exe"


# ---------------------------------------------------------------------------
# Process helpers (no psutil needed)
# ---------------------------------------------------------------------------

def _pid_alive(pid: int) -> bool:
    """Return True if the given PID is still a live process."""
    SYNCHRONIZE = 0x00100000
    handle = ctypes.windll.kernel32.OpenProcess(SYNCHRONIZE, False, pid)
    if not handle:
        return False
    ctypes.windll.kernel32.CloseHandle(handle)
    return True


def is_running() -> bool:
    if not PID_FILE.exists():
        return False
    try:
        pid = int(PID_FILE.read_text().strip())
        return _pid_alive(pid)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Core actions
# ---------------------------------------------------------------------------

def stop():
    """Kill VLC by the PID saved in vlc.pid."""
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            PROCESS_TERMINATE = 0x0001
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
            if handle:
                ctypes.windll.kernel32.TerminateProcess(handle, 0)
                ctypes.windll.kernel32.CloseHandle(handle)
        except Exception:
            pass
        try:
            PID_FILE.unlink()
        except Exception:
            pass


def start():
    """
    Launch VLC using the settings saved by the main GUI tool.
    Opens the GUI tool if no config exists yet.
    """
    if not CONFIG_FILE.exists():
        # First time — open the GUI so the user can configure
        gui = APP_DIR / "VLC Share Tool.exe"
        if gui.exists():
            subprocess.Popen([str(gui)])
        return

    try:
        cfg = json.loads(CONFIG_FILE.read_text())
    except Exception:
        return

    vlc_left   = cfg.get("vlc_left",   0)
    vlc_top    = cfg.get("vlc_top",    0)
    w          = cfg.get("width",      1920)
    h          = cfg.get("height",     1080)
    fps        = cfg.get("fps",        30)
    audio_in   = cfg.get("audio_in",   "").strip()
    audio_out  = cfg.get("audio_out",  "").strip()
    fullscreen = cfg.get("fullscreen", True)
    vlc_screen = cfg.get("vlc_screen", -1)

    if not os.path.exists(VLC_PATH):
        return   # VLC not found — silently skip

    cmd = [
        VLC_PATH,
        "screen://",
        f"--screen-fps={fps}",
        f"--screen-left={vlc_left}",
        f"--screen-top={vlc_top}",
        f"--screen-width={w}",
        f"--screen-height={h}",
        "--no-video-title-show",
    ]
    if fullscreen:
        cmd.append("--fullscreen")
        if vlc_screen >= 0:
            cmd.append(f"--qt-fullscreen-screennumber={vlc_screen}")
    else:
        cmd.append("--no-fullscreen")

    if audio_in and audio_in != "(none)":
        cmd += ["--dshow-adev", audio_in]
    if audio_out and audio_out != "(none)":
        cmd += ["--aout=mmdevice", f"--mmdevice-audio-device={audio_out}"]

    proc = subprocess.Popen(cmd)
    try:
        PID_FILE.write_text(str(proc.pid))
    except Exception:
        pass


def toggle():
    if is_running():
        stop()
    else:
        start()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else "toggle"
    {"start": start, "stop": stop}.get(cmd, toggle)()
