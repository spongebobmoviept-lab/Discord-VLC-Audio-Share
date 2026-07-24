import { definePlugin } from "@vencord/types";

/**
 * Vencord Plugin: VLC Share - Easy Access Button
 * 
 * Adds a quick button to launch VLC Share Tool setup.
 * 
 * Installation:
 * 1. Place in: %APPDATA%\Vencord\src\userplugins\VLCSharePlugin.tsx
 * 2. Restart Discord
 * 3. Enable in Vencord Settings > Plugins > VLC Share
 * 4. Use /vlc command or look for button in plugin menu
 */

export default definePlugin({
    name: "VLC Share",
    description: "Quick access to VLC Share Tool - stream anything to Discord",
    authors: [{ name: "You", id: "0" }],
    version: "1.0.0",
    
    commands: [
        {
            name: "vlc",
            description: "Show VLC Share Tool instructions and download link",
            execute: () => showVLCInstructions(),
        }
    ]
});

function showVLCInstructions() {
    return {
        content: `
🎬 **VLC Share Tool - Stream Anything to Discord**

**What it does:**
• Stream any monitor (including dummy plugs & virtual monitors)
• Stream any app window (Spotify, YouTube, OBS, games, etc.)
• Perfect audio routing through VB-Audio Virtual Cable
• Works where Discord's native screen share fails

**Quick Setup:**
1. Download ZIP: https://github.com/spongebobmoviept-lab/Discord-VLC-Audio-Share/releases
2. Extract anywhere
3. Double-click \`VLC Share Tool.exe\`
4. Pick monitor or window
5. Set Audio In = CABLE Output, Audio Out = (none)
6. Click "Launch VLC"
7. In Discord: Share Screen → Application Window → VLC → Go Live

**Why use this?**
Discord's native "Share System Audio" + screen share doesn't work with:
✗ Virtual audio devices (VB-Audio, Virtual Cable)
✗ Virtual monitors (dummy plugs)
✗ Specific app windows with system audio

VLC fixes all of this! 🚀

**Help:** Download at https://github.com/spongebobmoviept-lab/Discord-VLC-Audio-Share
        `,
        flags: 64 // Ephemeral message (only you see it)
    };
}
