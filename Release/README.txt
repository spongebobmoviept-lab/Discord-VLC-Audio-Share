VLC Discord Share Tool
======================
REQUIREMENTS (install once):
  - VLC media player: https://www.videolan.org/vlc/
  - VB-Audio Virtual Cable (for audio routing): https://vb-audio.com/Cable/

HOW TO USE:
  1. Run "VLC Share Tool.exe"
  2. Pick your monitor (or a window) from the list
  3. Pick your Audio In device (the virtual cable feeding into VLC)
  4. Pick your Audio Out device (where VLC sends audio)
  5. Hit "Launch VLC"
  6. In Discord: Share Screen -> Application Window -> pick VLC (NOT fullscreen)

STREAM DECK:
  Both EXEs must stay in the same folder.
  Run the GUI once and hit Launch to save your settings.
  Then in Stream Deck add "System: Open" -> vlc_share_ctl.exe, argument: toggle
  One button = Start/Stop.

  Separate buttons:
    Start:  vlc_share_ctl.exe start
    Stop:   vlc_share_ctl.exe stop

NOTES:
  - VLC is auto-detected from your Windows registry (any install location works)
  - Monitors are auto-detected at launch (any resolution/layout works)
  - Re-run the GUI any time your display layout changes, then hit Launch once
    to save the new config. Stream Deck will use it automatically after that.
