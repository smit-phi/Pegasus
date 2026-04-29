// Auth helper — manages tokens and user info in localStorage.
const auth = {
    saveTokens(data) {
        localStorage.setItem("access", data.access);
        localStorage.setItem("refresh", data.refresh);
    },

    clearTokens() {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("user_role");
        localStorage.removeItem("user_name");
    },

    isLoggedIn() {
        return !!localStorage.getItem("access");
    },

    getRole() {
        return localStorage.getItem("user_role") || null;
    },

    getUserName() {
        return localStorage.getItem("user_name") || "";
    },

    setUserInfo(role, name) {
        localStorage.setItem("user_role", role);
        localStorage.setItem("user_name", name);
    },

    logout() {
        this.clearTokens();
        window.location.hash = "#/login";
    },
};
