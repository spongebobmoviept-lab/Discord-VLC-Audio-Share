"""
VLC Discord Share Tool
-----------------------
• Auto-detects all monitors (resolution + position)
• Lists open windows so you can pick any app
• Launches VLC with the exact crop for your chosen region
• Creates a desktop shortcut — run once, done forever
"""

import os
import sys
import json
import subprocess
import winreg
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

# ---------------------------------------------------------------------------
# Optional heavy deps — gracefully degrade if missing at import time
# ---------------------------------------------------------------------------
try:
    import win32gui
    import win32api
    import win32com.client
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

try:
    from screeninfo import get_monitors as _screeninfo_monitors
    HAS_SCREENINFO = True
except ImportError:
    HAS_SCREENINFO = False

# ---------------------------------------------------------------------------
# CONFIG — change these if your setup differs
# ---------------------------------------------------------------------------
AUDIO_INPUT_DEVICE = "CABLE-A Output (VB-Audio Virtual Cable A)"

# Files written next to the exe (or script in dev mode) — shared with vlc_share_ctl.exe
APP_DIR     = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
CONFIG_FILE = APP_DIR / "config.json"
PID_FILE    = APP_DIR / "vlc.pid"


def find_vlc() -> str | None:
    """Locate VLC on any Windows machine — registry first, then common paths."""
    # 1. Windows registry (works for any install location)
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
    # 2. Common install paths
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
# Monitor / window detection
# ---------------------------------------------------------------------------

def get_monitors():
    """Return list of monitor dicts: name, x, y, width, height, is_primary."""
    monitors = []
    if HAS_SCREENINFO:
        for m in _screeninfo_monitors():
            monitors.append({
                "name": getattr(m, "name", f"Monitor {len(monitors) + 1}"),
                "x": m.x, "y": m.y,
                "width": m.width, "height": m.height,
                "is_primary": m.is_primary,
            })
    elif HAS_WIN32:
        def _cb(hMonitor, _hdc, _rect, _data):
            info = win32api.GetMonitorInfo(hMonitor)
            r = info["Monitor"]
            monitors.append({
                "name": info.get("Device", f"Monitor {len(monitors) + 1}"),
                "x": r[0], "y": r[1],
                "width": r[2] - r[0], "height": r[3] - r[1],
                "is_primary": bool(info.get("Flags", 0) & 1),
            })
            return True
        win32api.EnumDisplayMonitors(None, None, _cb, 0)
    return monitors


def get_windows():
    """Return list of visible top-level window dicts."""
    windows = []
    if not HAS_WIN32:
        return windows

    def _cb(hwnd, _extra):
        if not win32gui.IsWindowVisible(hwnd):
            return True
        title = win32gui.GetWindowText(hwnd)
        if not title or title == "Program Manager":
            return True
        try:
            x1, y1, x2, y2 = win32gui.GetWindowRect(hwnd)
            w, h = x2 - x1, y2 - y1
            if w > 80 and h > 80:
                windows.append({"title": title, "hwnd": hwnd,
                                 "x": x1, "y": y1, "width": w, "height": h})
        except Exception:
            pass
        return True

    win32gui.EnumWindows(_cb, None)
    return windows


# ---------------------------------------------------------------------------
# Audio device enumeration (Windows MMDevice registry — no extra deps)
# ---------------------------------------------------------------------------

def get_audio_endpoints(flow: str) -> list[str]:
    """
    Return friendly names of active audio endpoints from the Windows registry.
    flow: 'Render' for output/playback devices, 'Capture' for input/recording.
    """
    names = ["(none)"]
    try:
        base = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\{flow}"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base) as root:
            idx = 0
            while True:
                try:
                    guid = winreg.EnumKey(root, idx)
                    idx += 1
                    with winreg.OpenKey(root, guid) as dev:
                        # Skip non-active endpoints
                        try:
                            state, _ = winreg.QueryValueEx(dev, "DeviceState")
                            if state != 1:
                                continue
                        except OSError:
                            pass
                        # PKEY_Device_FriendlyName (pid 14), fallback DeviceDesc (pid 2)
                        try:
                            with winreg.OpenKey(dev, "Properties") as props:
                                for pid in (14, 2):
                                    key_name = "{a45c254e-df1c-4efd-8020-67d146a850e0},%d" % pid
                                    try:
                                        name, _ = winreg.QueryValueEx(props, key_name)
                                        if isinstance(name, str) and name.strip():
                                            names.append(name.strip())
                                            break
                                    except OSError:
                                        pass
                        except OSError:
                            pass
                except OSError:
                    break
    except Exception:
        pass
    return names


# ---------------------------------------------------------------------------
# VLC launcher
# ---------------------------------------------------------------------------

def launch_vlc(x: int, y: int, w: int, h: int, fps: int = 30,
               audio_in: str = AUDIO_INPUT_DEVICE,
               audio_out: str = "",
               fullscreen: bool = True,
               vlc_screen: int = -1,
               vlc_path: str = None) -> "subprocess.Popen | None":
    """
    Launch VLC capturing region (x,y,w,h).  Returns the Popen object so the
    caller can track / kill the process, or None on error.
    """
    if vlc_path is None:
        vlc_path = VLC_PATH
    
    if not os.path.exists(vlc_path):
        messagebox.showerror("VLC Not Found",
                             f"VLC not found at:\n{vlc_path}\n\n"
                             "Go to Settings tab and specify the correct VLC path, "
                             "or install VLC from videolan.org")
        return None

    # VLC's --screen-left/top are offsets from the virtual desktop origin,
    # NOT absolute Windows screen coordinates.  Subtract the origin so the
    # offset is correct even when monitors sit at negative coordinates.
    monitors = get_monitors()
    virt_left = min(m["x"] for m in monitors) if monitors else 0
    virt_top  = min(m["y"] for m in monitors) if monitors else 0

    screen_left = x - virt_left
    screen_top  = y - virt_top

    cmd = [
        vlc_path,
        "screen://",
        f"--screen-fps={fps}",
        f"--screen-left={screen_left}",
        f"--screen-top={screen_top}",
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

    ain = audio_in.strip()
    if ain and ain != "(none)":
        cmd += ["--dshow-adev", ain]
    aout = audio_out.strip()
    if aout and aout != "(none)":
        cmd += ["--aout=mmdevice", f"--mmdevice-audio-device={aout}"]

    return subprocess.Popen(cmd)


# ---------------------------------------------------------------------------
# Desktop shortcut
# ---------------------------------------------------------------------------

def create_desktop_shortcut() -> str | None:
    """Create a .lnk on the Desktop pointing at this exe (or pythonw + script)."""
    if not HAS_WIN32:
        messagebox.showerror("Error",
                             "pywin32 is required to create shortcuts.\n"
                             "Run:  pip install pywin32")
        return None

    desktop = Path(os.path.expanduser("~")) / "Desktop"
    lnk_path = str(desktop / "VLC Share Tool.lnk")

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(lnk_path)

    if getattr(sys, "frozen", False):
        # Running as PyInstaller EXE
        shortcut.Targetpath = sys.executable
        shortcut.WorkingDirectory = str(Path(sys.executable).parent)
        shortcut.IconLocation = sys.executable
    else:
        # Running as .py — point at pythonw.exe so no console window appears
        pythonw = Path(sys.executable).parent / "pythonw.exe"
        if not pythonw.exists():
            pythonw = Path(sys.executable)   # fallback
        shortcut.Targetpath = str(pythonw)
        shortcut.Arguments = f'"{os.path.abspath(__file__)}"'
        shortcut.WorkingDirectory = str(Path(__file__).parent)
        shortcut.IconLocation = str(Path(__file__).parent / "icon.ico") \
            if (Path(__file__).parent / "icon.ico").exists() else str(pythonw)

    shortcut.Description = "Launch VLC Discord Share Tool"
    shortcut.save()
    return lnk_path


# ---------------------------------------------------------------------------
# GUI Color Scheme (auto-detect Windows light/dark mode)
# ---------------------------------------------------------------------------

def get_windows_theme() -> str:
    """Detect if Windows is in light or dark mode."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize") as k:
            mode, _ = winreg.QueryValueEx(k, "AppsUseLightTheme")
            return "light" if mode == 1 else "dark"
    except Exception:
        return "dark"  # Default to dark mode


_THEME = get_windows_theme()

# Dark mode (default)
if _THEME == "dark":
    DARK = "#1e1e2e"
    SURFACE = "#313244"
    OVERLAY = "#45475a"
    BLUE = "#89b4fa"
    GREEN = "#a6e3a1"
    MAUVE = "#cba6f7"
    TEXT = "#cdd6f4"
    SUBTEXT = "#a6adc8"
    MUTED = "#6c7086"
else:
    # Light mode (Windows light theme)
    DARK = "#f5f5f5"      # Window background (light gray)
    SURFACE = "#e8e8e8"   # Panel background
    OVERLAY = "#d0d0d0"   # Hover/pressed
    BLUE = "#0066cc"      # Accent (Windows blue)
    GREEN = "#107c10"     # Success (Windows green)
    MAUVE = "#8661c5"     # Muted purple
    TEXT = "#1a1a1a"      # Foreground text
    SUBTEXT = "#5a5a5a"   # Secondary text
    MUTED = "#808080"     # Disabled text

DARK_COLOR = "#1e1e2e"
SURFACE_COLOR = "#313244"
OVERLAY_COLOR = "#45475a"
BLUE_COLOR = "#89b4fa"
GREEN_COLOR = "#a6e3a1"
MAUVE_COLOR = "#cba6f7"
TEXT_COLOR = "#cdd6f4"
SUBTEXT_COLOR = "#a6adc8"
MUTED_COLOR = "#6c7086"



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VLC Discord Share Tool")
        self.configure(bg=DARK)
        self.resizable(True, True)
        self.minsize(560, 460)
        self._monitors: list[dict] = []
        self._windows: list[dict] = []
        self._vlc_proc: subprocess.Popen | None = None
        self._build_styles()
        self._build_ui()
        self._refresh_monitors()
        self._load_config()

    # ------------------------------------------------------------------
    def _build_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", background=DARK, foreground=TEXT, font=("Segoe UI", 10))
        s.configure("TFrame", background=DARK)
        s.configure("TLabel", background=DARK, foreground=TEXT)
        s.configure("Title.TLabel", font=("Segoe UI", 14, "bold"), foreground=BLUE)
        s.configure("Sub.TLabel", foreground=GREEN, font=("Segoe UI", 9))
        s.configure("Hint.TLabel", foreground=MUTED, font=("Segoe UI", 8))
        s.configure("Status.TLabel", foreground=GREEN, font=("Segoe UI", 9))

        s.configure("TButton", background=BLUE, foreground=DARK,
                    font=("Segoe UI", 10, "bold"), padding=(10, 6), relief="flat")
        s.map("TButton",
              background=[("active", MAUVE), ("disabled", OVERLAY)],
              foreground=[("disabled", MUTED)])

        s.configure("Secondary.TButton", background=SURFACE, foreground=TEXT,
                    font=("Segoe UI", 9), padding=(8, 5))
        s.map("Secondary.TButton", background=[("active", OVERLAY)])

        s.configure("TNotebook", background=DARK, borderwidth=0, tabmargins=0)
        s.configure("TNotebook.Tab", background=SURFACE, foreground=SUBTEXT,
                    padding=(14, 7), font=("Segoe UI", 10))
        s.map("TNotebook.Tab",
              background=[("selected", BLUE)],
              foreground=[("selected", DARK)])

        s.configure("Treeview", background=SURFACE, foreground=TEXT,
                    fieldbackground=SURFACE, rowheight=30,
                    font=("Segoe UI", 10), borderwidth=0)
        s.configure("Treeview.Heading", background=OVERLAY, foreground=BLUE,
                    font=("Segoe UI", 10, "bold"), relief="flat")
        s.map("Treeview",
              background=[("selected", BLUE)],
              foreground=[("selected", DARK)])

        s.configure("TSpinbox", background=SURFACE, foreground=TEXT,
                    arrowcolor=BLUE, fieldbackground=SURFACE)
        s.configure("TSeparator", background=OVERLAY)

    # ------------------------------------------------------------------
    def _build_ui(self):
        # ---- Header ----
        hdr = ttk.Frame(self)
        hdr.pack(fill="x", padx=18, pady=(16, 4))
        ttk.Label(hdr, text="VLC Discord Share Tool", style="Title.TLabel").pack(side="left")

        # ---- Notebook ----
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=14, pady=6)
        self.nb = nb

        # Monitors tab
        mon_tab = ttk.Frame(nb)
        nb.add(mon_tab, text="  Monitors  ")
        self._build_monitor_tab(mon_tab)

        # Windows tab
        win_tab = ttk.Frame(nb)
        nb.add(win_tab, text="  Windows  ")
        self._build_window_tab(win_tab)

        # Settings tab
        settings_tab = ttk.Frame(nb)
        nb.add(settings_tab, text="  ⚙ Settings  ")
        self._build_settings_tab(settings_tab)

        # ---- Options row ----
        opts = ttk.Frame(self)
        opts.pack(fill="x", padx=18, pady=(4, 0))

        ttk.Label(opts, text="FPS:").pack(side="left")
        self.fps_var = tk.IntVar(value=30)
        tk.Spinbox(opts, from_=5, to=60, textvariable=self.fps_var,
                   width=5, bg=SURFACE, fg=TEXT, insertbackground=TEXT,
                   buttonbackground=OVERLAY, relief="flat",
                   font=("Segoe UI", 10), highlightthickness=0)\
            .pack(side="left", padx=(4, 16))

        ttk.Button(opts, text="⟳  Refresh Audio", style="Secondary.TButton",
                   command=self._refresh_audio).pack(side="left")

        # Fullscreen / VLC display row
        disp_row = ttk.Frame(self)
        disp_row.pack(fill="x", padx=18, pady=(4, 0))

        self.fullscreen_var = tk.BooleanVar(value=True)
        tk.Checkbutton(disp_row, text="Fullscreen", variable=self.fullscreen_var,
                       bg=DARK, fg=TEXT, selectcolor=SURFACE,
                       activebackground=DARK, activeforeground=TEXT,
                       font=("Segoe UI", 10), bd=0, highlightthickness=0)\
            .pack(side="left", padx=(0, 18))

        ttk.Label(disp_row, text="VLC opens on:").pack(side="left")
        self.vlc_screen_var = tk.StringVar(value="Auto")
        self.vlc_screen_cb = ttk.Combobox(disp_row, textvariable=self.vlc_screen_var,
                                           font=("Segoe UI", 9), width=38, state="readonly")
        self.vlc_screen_cb["values"] = ["Auto"]
        self.vlc_screen_cb.pack(side="left", padx=4)
        ttk.Label(disp_row, text="← which monitor VLC goes to",
                  style="Hint.TLabel").pack(side="left", padx=4)

        # Audio In row
        ain_row = ttk.Frame(self)
        ain_row.pack(fill="x", padx=18, pady=(4, 0))
        ttk.Label(ain_row, text="Audio In: ", width=10, anchor="e").pack(side="left")
        self.audio_in_var = tk.StringVar(value=AUDIO_INPUT_DEVICE)
        self.audio_in_cb = ttk.Combobox(ain_row, textvariable=self.audio_in_var,
                                         font=("Segoe UI", 9), width=52)
        self.audio_in_cb.pack(side="left", padx=4)
        ttk.Label(ain_row, text="← capture / virtual cable",
                  style="Hint.TLabel").pack(side="left", padx=4)

        # Audio Out row
        aout_row = ttk.Frame(self)
        aout_row.pack(fill="x", padx=18, pady=(3, 0))
        ttk.Label(aout_row, text="Audio Out:", width=10, anchor="e").pack(side="left")
        self.audio_out_var = tk.StringVar(value="(none)")
        self.audio_out_cb = ttk.Combobox(aout_row, textvariable=self.audio_out_var,
                                          font=("Segoe UI", 9), width=52)
        self.audio_out_cb.pack(side="left", padx=4)
        ttk.Label(aout_row, text="← playback device VLC uses",
                  style="Hint.TLabel").pack(side="left", padx=4)

        self._refresh_audio()

        # ---- Status ----
        self.status_var = tk.StringVar(value="Ready — select a monitor or window.")
        ttk.Label(self, textvariable=self.status_var, style="Status.TLabel")\
            .pack(padx=18, anchor="w")

        # ---- Action buttons ----
        btn_row = ttk.Frame(self)
        btn_row.pack(fill="x", padx=14, pady=(8, 4))

        ttk.Button(btn_row, text="▶  Launch VLC",
                   command=self._launch)\
            .pack(side="left", padx=(4, 6))

        ttk.Button(btn_row, text="⏹  Stop VLC",
                   command=self._stop_vlc, style="Secondary.TButton")\
            .pack(side="left", padx=(0, 14))

        ttk.Button(btn_row, text="🖇  Create Desktop Shortcut",
                   command=self._create_shortcut, style="Secondary.TButton")\
            .pack(side="left", padx=4)

        ttk.Label(self,
                  text="In Discord: share the VLC app window (NOT fullscreen).  "
                       "Audio In = what VLC captures.  Audio Out = where VLC plays it.",
                  style="Hint.TLabel")\
            .pack(pady=(2, 12))

    def _build_monitor_tab(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        self.mon_tree = ttk.Treeview(
            frame,
            columns=("name", "res", "pos", "primary"),
            show="headings", height=7, selectmode="browse")
        for col, w, txt, anchor in [
            ("name",    180, "Monitor",    "w"),
            ("res",     120, "Resolution", "center"),
            ("pos",     130, "Position",   "center"),
            ("primary",  70, "Primary",    "center"),
        ]:
            self.mon_tree.heading(col, text=txt)
            self.mon_tree.column(col, width=w, anchor=anchor, stretch=col == "name")
        self.mon_tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.mon_tree.yview)
        sb.pack(side="right", fill="y")
        self.mon_tree.configure(yscrollcommand=sb.set)

        ttk.Button(parent, text="⟳  Refresh", style="Secondary.TButton",
                   command=self._refresh_monitors).pack(pady=(0, 8))

    def _build_window_tab(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        self.win_tree = ttk.Treeview(
            frame,
            columns=("title", "size", "pos"),
            show="headings", height=7, selectmode="browse")
        for col, w, txt, anchor in [
            ("title", 260, "Window Title", "w"),
            ("size",  110, "Size",         "center"),
            ("pos",   110, "Position",     "center"),
        ]:
            self.win_tree.heading(col, text=txt)
            self.win_tree.column(col, width=w, anchor=anchor, stretch=col == "title")
        self.win_tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.win_tree.yview)
        sb.pack(side="right", fill="y")
        self.win_tree.configure(yscrollcommand=sb.set)

        ttk.Button(parent, text="⟳  Refresh", style="Secondary.TButton",
                   command=self._refresh_windows).pack(pady=(0, 8))

    # ------------------------------------------------------------------
    def _refresh_monitors(self):
        for row in self.mon_tree.get_children():
            self.mon_tree.delete(row)
        self._monitors = get_monitors()
        for i, m in enumerate(self._monitors):
            tag = "✓" if m["is_primary"] else ""
            self.mon_tree.insert("", "end", iid=str(i),
                values=(m["name"],
                        f"{m['width']} × {m['height']}",
                        f"({m['x']}, {m['y']})",
                        tag))
        # Auto-select largest non-primary (likely the dummy/virtual) else primary
        if self._monitors:
            best = max(self._monitors,
                       key=lambda m: (not m["is_primary"], m["width"] * m["height"]))
            self.mon_tree.selection_set(str(self._monitors.index(best)))
        self.status_var.set(f"Found {len(self._monitors)} monitor(s).")
        # Keep VLC display dropdown in sync with detected monitors
        screen_opts = ["Auto"] + [
            "Screen %d — %s  %d×%d%s" % (
                i, m["name"], m["width"], m["height"],
                " (Primary)" if m["is_primary"] else "")
            for i, m in enumerate(self._monitors)
        ]
        self.vlc_screen_cb["values"] = screen_opts
        if self.vlc_screen_var.get() not in screen_opts:
            self.vlc_screen_var.set("Auto")

    def _refresh_windows(self):
        for row in self.win_tree.get_children():
            self.win_tree.delete(row)
        self._windows = get_windows()
        for i, w in enumerate(self._windows):
            self.win_tree.insert("", "end", iid=str(i),
                values=(w["title"][:55],
                        f"{w['width']} × {w['height']}",
                        f"({w['x']}, {w['y']})"))
        self.status_var.set(f"Found {len(self._windows)} window(s).")

    def _get_region(self) -> tuple[int, int, int, int] | None:
        tab = self.nb.index(self.nb.select())
        if tab == 0:
            sel = self.mon_tree.selection()
            if not sel:
                messagebox.showwarning("No Selection", "Select a monitor first.")
                return None
            m = self._monitors[int(sel[0])]
            return m["x"], m["y"], m["width"], m["height"]
        else:
            sel = self.win_tree.selection()
            if not sel:
                messagebox.showwarning("No Selection", "Select a window first.")
                return None
            w = self._windows[int(sel[0])]
            return w["x"], w["y"], w["width"], w["height"]

    def _build_settings_tab(self, parent):
        """Settings tab — manual path overrides if auto-detection fails."""
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Title
        ttk.Label(frame, text="🔧 Paths & Auto-Detection",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 12))

        # VLC Path
        vlc_row = ttk.Frame(frame)
        vlc_row.pack(fill="x", pady=6)
        ttk.Label(vlc_row, text="VLC Path:").pack(side="left", anchor="w")
        self.vlc_path_var = tk.StringVar(value=VLC_PATH)
        vlc_entry = ttk.Entry(vlc_row, textvariable=self.vlc_path_var,
                              font=("Segoe UI", 9), width=60)
        vlc_entry.pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(vlc_row, text="Browse", width=8,
                   command=self._browse_vlc).pack(side="left")

        ttk.Label(frame, text="Current: " + VLC_PATH, font=("Segoe UI", 8),
                  foreground="gray").pack(anchor="w", pady=(0, 12))

        # Auto-detection info
        ttk.Label(frame, text="ℹ️ Auto-Detection Status",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(12, 6))

        info_text = []
        if HAS_SCREENINFO:
            info_text.append("✓ Monitor detection (screeninfo)")
        else:
            info_text.append("✗ Monitor detection needs screeninfo (auto-installs on first run)")

        if HAS_WIN32:
            info_text.append("✓ Window capture & audio")
        else:
            info_text.append("✗ Window capture needs win32 (auto-installs on first run)")

        if os.path.exists(VLC_PATH):
            info_text.append(f"✓ VLC found: {VLC_PATH}")
        else:
            info_text.append("✗ VLC not found — specify path above or install from videolan.org")

        for line in info_text:
            ttk.Label(frame, text=line, font=("Segoe UI", 9)).pack(anchor="w", pady=2)

        # Spacer
        ttk.Frame(frame).pack(fill="y", expand=True)

        # Save button
        ttk.Button(frame, text="💾 Save Settings",
                   command=self._save_settings).pack(pady=12)

    def _browse_vlc(self):
        """Open file browser to find vlc.exe."""
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Find VLC executable",
            filetypes=[("VLC Executable", "vlc.exe"), ("All Files", "*.*")],
            initialfile="vlc.exe"
        )
        if path:
            self.vlc_path_var.set(path)

    def _save_settings(self):
        """Save custom paths to config."""
        cfg = {}
        try:
            if CONFIG_FILE.exists():
                cfg = json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass

        vlc_custom = self.vlc_path_var.get().strip()
        if vlc_custom and os.path.exists(vlc_custom):
            cfg["vlc_path"] = vlc_custom
            messagebox.showinfo("Settings Saved",
                                f"VLC path saved:\n{vlc_custom}")
        else:
            messagebox.showwarning("Invalid Path",
                                   "VLC path must be a valid file.")

        try:
            CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save settings:\n{e}")

    def _refresh_audio(self):
        captures = get_audio_endpoints("Capture")
        renders  = get_audio_endpoints("Render")
        self.audio_in_cb["values"]  = captures
        self.audio_out_cb["values"] = renders
        # Pre-select first real capture device (index 1, skip "(none)")
        if len(captures) > 1 and self.audio_in_var.get() == AUDIO_INPUT_DEVICE:
            # Keep default if it appears in the list, otherwise pick first real one
            if AUDIO_INPUT_DEVICE not in captures:
                self.audio_in_var.set(captures[1])
        # Leave audio out as (none) until user picks

    def _launch(self):
        region = self._get_region()
        if region is None:
            return
        x, y, w, h = region
        fps       = self.fps_var.get()
        audio_in  = self.audio_in_var.get().strip()
        audio_out = self.audio_out_var.get().strip()
        fullscreen = bool(self.fullscreen_var.get())

        vlc_screen = -1
        sel = self.vlc_screen_var.get()
        if sel != "Auto":
            try:
                vlc_screen = int(sel.split()[1])
            except (IndexError, ValueError):
                pass

        vlc_path = self.vlc_path_var.get().strip()
        proc = launch_vlc(x, y, w, h, fps, audio_in, audio_out, fullscreen, vlc_screen, vlc_path)
        if proc:
            self._vlc_proc = proc
            try:
                PID_FILE.write_text(str(proc.pid))
            except Exception:
                pass
            self._save_config(x, y, w, h)
            monitors = get_monitors()
            virt_left = min(m["x"] for m in monitors) if monitors else 0
            virt_top  = min(m["y"] for m in monitors) if monitors else 0
            fs_tag = "fullscreen" if fullscreen else "windowed"
            self.status_var.set(
                f"VLC launched  •  {w}×{h}  •  vlc-offset=({x-virt_left},{y-virt_top})"
                f"  •  {fps}fps  •  {fs_tag}")

    def _stop_vlc(self):
        """Kill VLC via PID file (works even after a restart)."""
        killed = False
        if PID_FILE.exists():
            try:
                pid = int(PID_FILE.read_text().strip())
                PROCESS_TERMINATE = 0x0001
                import ctypes
                handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
                if handle:
                    ctypes.windll.kernel32.TerminateProcess(handle, 0)
                    ctypes.windll.kernel32.CloseHandle(handle)
                    killed = True
            except Exception:
                pass
            try:
                PID_FILE.unlink()
            except Exception:
                pass
        if self._vlc_proc and self._vlc_proc.poll() is None:
            self._vlc_proc.terminate()
            killed = True
        self._vlc_proc = None
        self.status_var.set("VLC stopped." if killed else "VLC was not running.")

    def _save_config(self, x: int, y: int, w: int, h: int):
        monitors = get_monitors()
        virt_left = min(m["x"] for m in monitors) if monitors else 0
        virt_top  = min(m["y"] for m in monitors) if monitors else 0

        vlc_screen = -1
        sel = self.vlc_screen_var.get()
        if sel != "Auto":
            try:
                vlc_screen = int(sel.split()[1])
            except (IndexError, ValueError):
                pass

        cfg = {
            "vlc_left":   x - virt_left,
            "vlc_top":    y - virt_top,
            "width":      w,
            "height":     h,
            "fps":        self.fps_var.get(),
            "audio_in":   self.audio_in_var.get().strip(),
            "audio_out":  self.audio_out_var.get().strip(),
            "fullscreen": bool(self.fullscreen_var.get()),
            "vlc_screen": vlc_screen,
        }
        try:
            CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
        except Exception:
            pass

    def _load_config(self):
        if not CONFIG_FILE.exists():
            return
        try:
            cfg = json.loads(CONFIG_FILE.read_text())
            if "fps" in cfg:
                self.fps_var.set(cfg["fps"])
            if "audio_in" in cfg:
                self.audio_in_var.set(cfg["audio_in"])
            if "audio_out" in cfg:
                self.audio_out_var.set(cfg["audio_out"])
            if "fullscreen" in cfg:
                self.fullscreen_var.set(cfg["fullscreen"])
            if "vlc_path" in cfg:
                self.vlc_path_var.set(cfg["vlc_path"])
        except Exception:
            pass

    def _create_shortcut(self):
        result = create_desktop_shortcut()
        if result:
            self.status_var.set(f"Shortcut saved: {result}")
            messagebox.showinfo("Shortcut Created",
                                f"Desktop shortcut created:\n{result}\n\n"
                                "Run it after any display layout change and hit Launch.")


# ---------------------------------------------------------------------------
# Entry point — auto-install missing deps on first run
# ---------------------------------------------------------------------------

def _check_and_install_deps():
    missing = []
    if not HAS_WIN32:
        missing.append("pywin32")
    if not HAS_SCREENINFO:
        missing.append("screeninfo")
    if not missing:
        return True

    root = tk.Tk()
    root.withdraw()
    ok = messagebox.askyesno(
        "Missing Packages",
        f"The following packages are required:\n  {', '.join(missing)}\n\n"
        "Install them now? (requires internet connection)")
    root.destroy()
    if not ok:
        return False

    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet"] + missing,
        check=True)

    messagebox.showinfo("Done",
                        "Packages installed!\nPlease restart VLC Share Tool.")
    return False   # restart needed


if __name__ == "__main__":
    if _check_and_install_deps():
        App().mainloop()
