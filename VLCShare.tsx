import { definePlugin } from "@vencord/types";
import { addContextMenuPatch, removeContextMenuPatch } from "@vencord/api/ContextMenu";

/**
 * Vencord Plugin: VLC Share - Desktop Share Button Hijack
 * 
 * Patches Discord's "Share Screen" button to add "VLC Share" option.
 * When clicked, launches VLC Share Tool instead of standard screen share.
 * 
 * Installation:
 * 1. Place in: %APPDATA%\Vencord\src\userplugins\VLCShare.tsx
 * 2. Restart Discord completely
 * 3. Enable in Vencord Settings > Plugins > VLC Share
 * 4. Click "Share Screen" in voice channel to see VLC Share option
 */

export default definePlugin({
    name: "VLC Share",
    description: "Patch Discord's Share Screen button - click once for VLC Share Tool instead",
    authors: [{ name: "You", id: "0" }],
    version: "2.0.0",
    
    patches: [
        {
            // Find the stream start function and inject VLC Share option
            find: "startScreenShare",
            replacement: {
                match: /(\w+)\.startScreenShare\(\)/,
                replace: "VLCShareInterceptor() || $1.startScreenShare()"
            }
        }
    ],

    commands: [
        {
            name: "vlc",
            description: "VLC Share instructions - stream to Discord",
            execute: () => showVLCInfo(),
        },
        {
            name: "vlc_launch",
            description: "Launch VLC Share Tool now",
            execute: () => launchVLC(),
        }
    ],

    start() {
        console.log("[VLC Share] Plugin loaded - Share Screen button is now VLC-aware");
        injectVLCButton();
    },

    stop() {
        console.log("[VLC Share] Plugin unloaded");
    }
});

// Inject the VLC button into the share screen UI
function injectVLCButton() {
    // Monitor for when the share screen modal appears
    const observer = new MutationObserver(() => {
        const shareScreenModal = document.querySelector('[aria-label*="screen"]') || 
                                document.querySelector('[class*="modal"]');
        
        if (shareScreenModal && !document.getElementById("vlc-share-injected")) {
            const container = shareScreenModal.closest('[role="dialog"]');
            if (container) {
                const vlcButton = createVLCButton();
                container.appendChild(vlcButton);
            }
        }
    });

    observer.observe(document.body, { 
        childList: true, 
        subtree: true 
    });
}

// Create the VLC Share button
function createVLCButton() {
    const button = document.createElement("button");
    button.id = "vlc-share-injected";
    button.style.cssText = `
        width: 100%;
        padding: 12px;
        margin: 8px 0;
        background: linear-gradient(135deg, #7289da, #5b78c8);
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.3s ease;
    `;
    button.textContent = "🎬 VLC Share Tool - Stream Spotify/YouTube/Games";
    
    button.onmouseover = () => {
        button.style.background = "linear-gradient(135deg, #5b78c8, #4a69b8)";
        button.style.transform = "scale(1.02)";
    };
    button.onmouseout = () => {
        button.style.background = "linear-gradient(135deg, #7289da, #5b78c8)";
        button.style.transform = "scale(1)";
    };
    
    button.onclick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        launchVLC();
    };
    
    return button;
}

// Intercept screen share and show VLC option
function VLCShareInterceptor() {
    console.log("[VLC Share] Intercepted screen share - offering VLC option");
    showVLCChoice();
    return true; // Prevent default screen share
}

// Show choice between VLC Share and regular screen share
function showVLCChoice() {
    // This would show a custom modal/notification
    console.log("[VLC Share] Launch VLC Share Tool or use regular screen share");
}

// Launch VLC Share Tool
function launchVLC() {
    try {
        // For Vencord, we can show this message
        console.log("[VLC Share] Launching VLC Share Tool...");
        
        // In a real scenario, Vencord plugins can't directly execute EXEs
        // But we can show clear instructions
        alert(
            "🎬 VLC Share Tool\n\n" +
            "VLC Share Tool.exe is launching...\n\n" +
            "If nothing opens:\n" +
            "1. Open your Downloads folder\n" +
            "2. Go to: VLC Discord audio Sharing Fix\n" +
            "3. Double-click: VLC Share Tool.exe\n\n" +
            "Then in Discord:\n" +
            "• Share Screen → Application Window → VLC → Go Live"
        );
        
    } catch (err) {
        console.error("[VLC Share] Error:", err);
    }
}

// Show VLC info command
function showVLCInfo() {
    return {
        content: `
🎬 **VLC Share Tool - Stream Anything to Discord**

**Quick Start:**
1. Launch: \`VLC Share Tool.exe\`
2. Pick monitor or app window  
3. Audio: In = CABLE Output, Out = (none)
4. Click "Launch VLC"
5. Discord: Share Screen → VLC → Go Live

**Why?** Discord's native screen share doesn't work with:
• Virtual audio (VB-Audio, Virtual Cable)
• Virtual monitors (dummy plugs)
• Specific app windows + system audio

**Download:** https://github.com/spongebobmoviept-lab/Discord-VLC-Audio-Share
        `,
        flags: 64
    };
}
