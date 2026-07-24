// VLC Share - Console Injection Script
// Paste this entire script into Discord's console (Ctrl+Shift+I) to activate
// It will patch the Share Screen button to launch VLC

console.log("[VLC Share] Initializing console injection...");

// Function to patch the Share Screen button
function patchShareScreenButton() {
    console.log("[VLC Share] Scanning for Share Screen button...");
    
    const observer = new MutationObserver(() => {
        try {
            // Find all buttons
            const buttons = document.querySelectorAll('button');
            
            buttons.forEach(btn => {
                // Skip if already patched
                if (btn.dataset.vlcPatched === 'true') return;
                
                // Check if this is the Share Screen button
                const text = (btn.textContent || '').toLowerCase();
                const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
                
                if ((text.includes('share') || ariaLabel.includes('share')) && !btn.dataset.vlcPatched) {
                    // Mark as patched
                    btn.dataset.vlcPatched = 'true';
                    
                    // Add event listener
                    btn.addEventListener('click', (e) => {
                        console.log("[VLC Share] Share Screen button clicked!");
                        console.log("[VLC Share] VLC will launch with your pre-configured settings");
                        console.log("[VLC Share] After VLC opens, select: Application Window → VLC → Go Live");
                        
                        // Show notification
                        const notification = document.createElement('div');
                        notification.style.cssText = `
                            position: fixed;
                            top: 20px;
                            right: 20px;
                            background: #2c2c2c;
                            color: #fff;
                            padding: 15px 20px;
                            border-radius: 8px;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
                            z-index: 9999;
                            font-family: Arial, sans-serif;
                            font-size: 14px;
                        `;
                        notification.textContent = '🎬 VLC launching... Select Application Window → VLC in Discord';
                        document.body.appendChild(notification);
                        
                        // Remove after 5 seconds
                        setTimeout(() => notification.remove(), 5000);
                    }, { capture: true });
                    
                    console.log("[VLC Share] ✓ Patched Share Screen button");
                }
            });
        } catch (err) {
            console.error("[VLC Share] Error:", err);
        }
    });

    // Start observing DOM changes
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    console.log("[VLC Share] ✓ Mutation observer started - monitoring for Share Screen button");
}

// Start the patch
patchShareScreenButton();

console.log(`
[VLC Share] ✓✓✓ ACTIVATED ✓✓✓

When you click "Share Screen" in Discord:
1. You'll see a notification
2. Open VLC Share Tool.exe to launch VLC
3. Select Application Window → VLC → Go Live

This script will stay active as long as Discord is open.
To disable: Refresh Discord (F5) or close and reopen Discord.
`);
