import { definePlugin } from "@vencord/types";

/**
 * Vencord Plugin: VLC Share Tool Launcher
 * 
 * Adds "/vlc_share" and "/vlc_toggle" commands to Discord.
 * Launches the VLC Share Tool exe with one click.
 * 
 * Installation:
 * 1. Place this file in: %APPDATA%\Vencord\src\userplugins\VLCShareVencord.tsx
 * 2. Close Discord completely (from taskbar)
 * 3. Reopen Discord
 * 4. Enable plugin in Vencord settings (Plugins tab)
 */

export default definePlugin({
    name: "VLC Share Tool",
    description: "Launch VLC Share Tool from Discord - use /vlc_share or /vlc_toggle commands",
    authors: [{ name: "You", id: "0" }],
    version: "1.0.0",
    
    commands: [
        {
            name: "vlc_share",
            description: "Launch VLC Share Tool GUI",
            execute: () => {
                launchVLCShare();
                return { content: "🎬 Launching VLC Share Tool...", flags: 64 };
            }
        },
        {
            name: "vlc_toggle",
            description: "Toggle VLC stream (start/stop)",
            execute: () => {
                launchVLCToggle();
                return { content: "⏯️ VLC stream toggled", flags: 64 };
            }
        }
    ]
});

/**
 * Launch VLC Share Tool GUI
 */
function launchVLCShare() {
    const { execSync } = require("child_process");
    try {
        // Try common installation paths
        const paths = [
            "D:\\Downloads\\VLC Discord audio Sharing Fix\\VLC Share Tool.exe",
            "C:\\Program Files\\VLC Share Tool\\VLC Share Tool.exe",
            "C:\\Users\\" + process.env.USERNAME + "\\Downloads\\VLC Discord audio Sharing Fix\\VLC Share Tool.exe"
        ];
        
        let found = false;
        for (const path of paths) {
            try {
                execSync(`"${path}"`, { detached: true, stdio: "ignore" });
                found = true;
                break;
            } catch (e) {
                // Try next path
            }
        }
        
        if (!found) {
            console.error("[VLC Share] Could not find VLC Share Tool.exe in common locations");
        }
    } catch (err) {
        console.error("[VLC Share] Error:", err);
    }
}

/**
 * Toggle VLC stream (requires vlc_share_ctl.exe in same dir)
 */
function launchVLCToggle() {
    const { execSync } = require("child_process");
    try {
        const paths = [
            "D:\\Downloads\\VLC Discord audio Sharing Fix\\vlc_share_ctl.exe",
            "C:\\Program Files\\VLC Share Tool\\vlc_share_ctl.exe",
            "C:\\Users\\" + process.env.USERNAME + "\\Downloads\\VLC Discord audio Sharing Fix\\vlc_share_ctl.exe"
        ];
        
        let found = false;
        for (const path of paths) {
            try {
                execSync(`"${path}" toggle`, { detached: true, stdio: "ignore" });
                found = true;
                break;
            } catch (e) {
                // Try next path
            }
        }
        
        if (!found) {
            console.error("[VLC Share] Could not find vlc_share_ctl.exe in common locations");
        }
    } catch (err) {
        console.error("[VLC Share] Error:", err);
    }
}
