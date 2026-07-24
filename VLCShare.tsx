import { definePlugin } from "@vencord/types";

export default definePlugin({
    name: "VLC Share",
    description: "Click Share Screen to use VLC",
    authors: [{ name: "VLC", id: "1" }],
    version: "3.2.0",

    start() {
        console.log("[VLC] Started");
    },

    stop() {
        console.log("[VLC] Stopped");
    }
});
