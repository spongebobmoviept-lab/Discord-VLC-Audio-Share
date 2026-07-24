import { definePlugin } from "@vencord/types";
import { findByCodeLazy } from "@vencord/webpack";
import { execFile } from "child_process";
import { join } from "path";
import { getChannel } from "@vencord/discord-common";

/**
 * Vencord Plugin: VLC Share Tool Launcher
 * 
 * Adds a "Launch VLC Share" button/command to Discord.
 * Launches the VLC Share Tool exe with one click.
 * 
 * Installation:
 * 1. Place this file in: %APPDATA%\Vencord\src\userplugins\VLCShare.tsx
 * 2. Restart Discord
 * 3. Enable plugin in Vencord settings
 */

export default definePlugin({
    name: "VLC Share Tool",
    description: "Launch VLC Share Tool from Discord with one click",
    authors: [{ name: "You", id: "0" }],
    
    commands: [
        {
            name: "vlc_share",
            description: "Launch VLC Share Tool",
            execute: async () => {
                launchVLCShare();
                return { content: "🎬 Launching VLC Share Tool...", flags: 64 };
            }
        },
        {
            name: "vlc_toggle",
            description: "Toggle VLC stream (start/stop)",
            execute: async () => {
                launchVLCToggle();
                return { content: "⏯️ VLC stream toggled", flags: 64 };
            }
        }
    ],

    patches: [
        {
            find: "useStreamSourceExperiment",
            replacement: {
                match: /(\(0,\w+\.jsxs?\)\("button",\{[^}]*?"Share Your Screen")/,
                replace: "$1"
            }
        }
    ]
});

/**
 * Launch VLC Share Tool GUI
 */
function launchVLCShare() {
    try {
        // Adjust these paths based on where you extract VLC Share Tool
        const exePath = join(
            process.env.APPDATA || "",
            "..",
            "Downloads",
            "VLC Discord audio Sharing Fix",
            "VLC Share Tool.exe"
        );
        
        // Launch with no arguments (opens GUI)
        execFile(exePath, [], { detached: true }, (error) => {
            if (error) {
                console.error("[VLC Share] Failed to launch:", error);
            }
        });
    } catch (err) {
        console.error("[VLC Share] Error:", err);
    }
}

/**
 * Toggle VLC stream (requires vlc_share_ctl.exe in same dir)
 */
function launchVLCToggle() {
    try {
        const exePath = join(
            process.env.APPDATA || "",
            "..",
            "Downloads",
            "VLC Discord audio Sharing Fix",
            "vlc_share_ctl.exe"
        );
        
        // Toggle: start/stop VLC
        execFile(exePath, ["toggle"], { detached: true }, (error) => {
            if (error) {
                console.error("[VLC Share] Toggle failed:", error);
            }
        });
    } catch (err) {
        console.error("[VLC Share] Error:", err);
    }
}
