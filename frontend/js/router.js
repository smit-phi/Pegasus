// Simple hash-based router.
const router = {
    routes: {},

    register(hash, handler) {
        this.routes[hash] = handler;
    },

    navigate(hash) {
        window.location.hash = hash;
    },

    /** Resolve current hash and call the matching handler */
    resolve() {
        const hash = window.location.hash || "#/";
        // Match exact first, then try prefix patterns like #/doctor-slots/123
        if (this.routes[hash]) {
            this.routes[hash]();
            return;
        }
        // Try pattern matching for dynamic routes
        for (const pattern in this.routes) {
            if (pattern.includes(":")) {
                const regex = new RegExp("^" + pattern.replace(/:[^/]+/g, "([^/]+)") + "$");
                const match = hash.match(regex);
                if (match) {
                    this.routes[pattern](match[1]);
                    return;
                }
            }
        }
        // Default
        if (this.routes["#/"]) this.routes["#/"]();
    },

    init() {
        window.addEventListener("hashchange", () => this.resolve());
        this.resolve();
    },
};
