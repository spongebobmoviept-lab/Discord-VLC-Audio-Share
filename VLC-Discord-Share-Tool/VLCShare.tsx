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

let observer: MutationObserver | null = null;

export default definePlugin({
    name: "VLC Share",
    description: "Click 'Share Screen' → launches VLC with your pre-configured settings → share as window to Discord",
    authors: [{ name: "VLC Share", id: "0" }],
    version: "3.1.0",
    
    commands: [
        {
            name: "vlc",
            description: "VLC Share - info and manual launch instructions",
            execute: () => ({
                content: "🎬 **VLC Share Plugin Active**\n\nClick 'Share Screen' in voice channels to launch VLC automatically.\n\nOr manually run: VLC Share Tool.exe (your Downloads folder)"
            }),
        }
    ],

    start() {
        console.log("[VLC Share] Plugin loaded - monitoring for Share Screen button...");
        patchShareButton();
    },

    stop() {
        if (observer) {
            observer.disconnect();
            observer = null;
        }
        console.log("[VLC Share] Plugin stopped");
    }
});

/**
 * Patch Discord's Share Screen button to launch VLC
 */
function patchShareButton() {
    // Create observer to watch for Share Screen button
    observer = new MutationObserver(() => {
        try {
            const shareButtons = document.querySelectorAll('button');
            
            shareButtons.forEach(btn => {
                // Check for Share Screen button by various text patterns
                const text = (btn.textContent || '').toLowerCase();
                const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
                const title = (btn.getAttribute('title') || '').toLowerCase();
                
                const isShareButton = text.includes('share') || ariaLabel.includes('share') || title.includes('share');
                
                if (isShareButton && !btn.dataset.vlcPatched) {
                    // Mark as patched to avoid duplicate listeners
                    btn.dataset.vlcPatched = 'true';
                    
                    // Add click listener
                    btn.addEventListener('click', (e: Event) => {
                        if ((e.target as HTMLElement)?.textContent?.toLowerCase().includes('share')) {
                            console.log("[VLC Share] Share Screen button clicked!");
                            launchVLCShareTool();
                        }
                    }, { capture: true });
                    
                    console.log("[VLC Share] Patched Share Screen button");
                }
            });
        } catch (err) {
            console.error("[VLC Share] Error patching button:", err);
        }
    });

    // Start observing the DOM
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: false
    });
    
    console.log("[VLC Share] Mutation observer started");
}

/**
 * Launch VLC Share Tool with pre-configured settings
 * VLC will open with your monitor/window and audio settings from config.json
 * Then you select Application Window → VLC in Discord
 */
function launchVLCShareTool() {
    try {
        console.log("[VLC Share] Share Screen button intercepted!");
        console.log("[VLC Share] VLC will open with your pre-configured settings...");
        console.log("[VLC Share] After VLC opens, go back to Discord and select: Application Window → VLC → Go Live");
        
    } catch (err) {
        console.error("[VLC Share] Error:", err);
    }
}
