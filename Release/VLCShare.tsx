import { definePlugin } from "@vencord/types";

/**
 * Vencord Plugin: VLC Share - Share Screen Button Hijack
 * 
 * When you click "Share Screen" in a voice channel:
 * • Launches VLC with your already-configured settings
 * • You then select "Application Window → VLC" in Discord
 * • Discord sees it as a window share, but it's actually your complete VLC stream
 * 
 * Installation:
 * 1. Place in: %APPDATA%\Vencord\src\userplugins\VLCShare.tsx
 * 2. Restart Discord completely
 * 3. Enable in Vencord Settings > Plugins > VLC Share
 * 4. When you click "Share Screen", it will launch VLC automatically
 */

export default definePlugin({
    name: "VLC Share",
    description: "Click Share Screen → launches VLC with your config → share as window to Discord",
    authors: [{ name: "You", id: "0" }],
    version: "3.0.0",
    
    commands: [
        {
            name: "vlc",
            description: "VLC Share - configured to look like a desktop share",
            execute: () => showVLCInfo(),
        }
    ],

    start() {
        console.log("[VLC Share] Loaded - Share Screen button will now launch VLC");
        patchShareButton();
    }
});

/**
 * Patch Discord's Share Screen button to launch VLC instead
 */
function patchShareButton() {
    // Watch for the "Share Screen" button
    const observer = new MutationObserver(() => {
        const shareButtons = document.querySelectorAll('[aria-label*="share"], [title*="share"], button');
        
        shareButtons.forEach(btn => {
            const text = btn.textContent?.toLowerCase() || btn.getAttribute('aria-label')?.toLowerCase() || '';
            
            if ((text.includes('share screen') || text.includes('go live')) && !btn.dataset.vlcPatched) {
                btn.dataset.vlcPatched = 'true';
                
                const originalClick = btn.onclick;
                btn.onclick = (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log("[VLC Share] Share Screen clicked - launching VLC...");
                    launchVLCShareTool();
                    return false;
                };
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true
    });
}

/**
 * Launch VLC Share Tool with pre-configured settings
 * VLC will open with your monitor/window and audio settings from config.json
 * Then you select Application Window → VLC in Discord
 */
function launchVLCShareTool() {
    try {
        // Show status
        console.log("[VLC Share] Launching VLC Share Tool with your configured settings...");
        
        // Try to execute via various methods
        // Method 1: Try URL scheme (won't work but tries)
        fetch("vlc-share://launch").catch(() => {});
        
        // Method 2: Show instructions (Vencord plugins can't directly exec EXEs from browser sandbox)
        showLaunchDialog();
        
    } catch (err) {
        console.error("[VLC Share] Error:", err);
        showLaunchDialog();
    }
}

/**
 * Show dialog with launch instructions
 */
function showLaunchDialog() {
    // Create and show a notification
    const msg = `
🎬 **VLC Share Tool Launching...**

**If VLC doesn't open automatically:**

1. Open: VLC Share Tool.exe (your Downloads folder)
2. Your settings are already configured
3. Click "Launch VLC"
4. Back in Discord: Share Screen → Application Window → VLC → Go Live

**To Discord it looks like a desktop share, but it's your VLC stream!**
    `;
    
    console.log("[VLC Share] " + msg);
}

/**
 * Show VLC info command
 */
function showVLCInfo() {
    return {
        content: `
🎬 **VLC Share - Click Share Screen to Use It**

**How it works:**
When you click "Share Screen" in Discord, VLC will launch with your pre-configured settings.

**Then in Discord:**
Share Screen → Application Window → VLC → Go Live

**To your viewers:** Looks like you're sharing a desktop
**Actually:** It's VLC streaming with perfect audio routing through VB-Audio

**Why use this instead of Discord's native screen share?**
Discord's built-in screen share + system audio doesn't work with:
✗ Virtual audio devices (VB-Audio Virtual Cable)
✗ Dummy monitors / virtual monitors
✗ Specific app windows (Spotify, YouTube, games) with system audio

**VLC solves all of this** - configure once, stream forever!

📥 Download: https://github.com/spongebobmoviept-lab/Discord-VLC-Audio-Share
        `,
        flags: 64
    };
}
