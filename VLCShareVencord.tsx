import { definePlugin } from "@vencord/types";
import { showNotification } from "@vencord/api/notices";

export default definePlugin({
    name: "VLC Share Tool",
    description: "Discord integration for VLC Share Tool streaming",
    authors: [{ name: "You", id: "0" }],
    version: "1.0.0",
    
    commands: [
        {
            name: "vlc_share",
            description: "Open VLC Share Tool",
            execute: () => {
                launchVLC("share");
                return { content: "🎬 VLC Share Tool launching...\n\nIf nothing opened, run VLC Share Tool.exe from your Downloads folder.", flags: 64 };
            }
        },
        {
            name: "vlc_toggle", 
            description: "Toggle VLC stream on/off",
            execute: () => {
                launchVLC("toggle");
                return { content: "⏯️ VLC stream toggled", flags: 64 };
            }
        }
    ]
});

function launchVLC(mode: string) {
    try {
        // Try to access Node.js require
        const { execFile } = require("child_process");
        const paths = [
            "D:\\Downloads\\VLC Discord audio Sharing Fix\\VLC Share Tool.exe",
            "C:\\Program Files\\VLC Share Tool\\VLC Share Tool.exe"
        ];
        
        for (const exePath of paths) {
            try {
                if (mode === "toggle") {
                    execFile("vlc_share_ctl.exe", ["toggle"], { detached: true, stdio: "ignore" });
                } else {
                    execFile(exePath, [], { detached: true, stdio: "ignore" });
                }
                return;
            } catch (e) {
                // Try next path
            }
        }
    } catch (err) {
        console.error("[VLC Share]", err);
    }
}
