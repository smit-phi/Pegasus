// Central API helper — all fetch calls go through here.
const API_BASE = "http://localhost:8000";

const api = {
    /**
     * Generic fetch wrapper.
     * @param {string} path  — relative path, e.g. "/api/auth/login/"
     * @param {object} opts  — { method, body, auth (bool) }
     */
    async request(path, opts = {}) {
        const { method = "GET", body = null, auth = false } = opts;
        const headers = { "Content-Type": "application/json" };

        if (auth) {
            const token = localStorage.getItem("access");
            if (!token) {
                window.location.hash = "#/login";
                throw new Error("Not authenticated");
            }
            headers["Authorization"] = `Bearer ${token}`;
        }

        const fetchOpts = { method, headers };
        if (body) fetchOpts.body = JSON.stringify(body);

        const res = await fetch(`${API_BASE}${path}`, fetchOpts);

        // Try to parse JSON; some endpoints return empty body
        let data = null;
        const text = await res.text();
        if (text) {
            try { data = JSON.parse(text); } catch { data = text; }
        }

        if (!res.ok) {
            const err = new Error(typeof data === "object" ? JSON.stringify(data) : data || res.statusText);
            err.status = res.status;
            err.data = data;
            throw err;
        }

        return data;
    },

    // Auth
    login(email, password) {
        return this.request("/api/auth/login/", { method: "POST", body: { email, password } });
    },
    register(data) {
        return this.request("/api/auth/register/", { method: "POST", body: data });
    },
    getMe() {
        return this.request("/api/auth/me/", { auth: true });
    },
    updateMe(data) {
        return this.request("/api/auth/me/", { method: "PATCH", body: data, auth: true });
    },

    // Departments
    getDepartments() {
        return this.request("/api/departments/");
    },

    // Doctors
    getDoctors(departmentId) {
        const q = departmentId ? `?department=${departmentId}` : "";
        return this.request(`/api/doctors/${q}`);
    },
    getDoctor(id) {
        return this.request(`/api/doctors/${id}/`);
    },

    // Slots (patient browsing)
    getSlots(doctorId) {
        return this.request(`/slots/?doctor=${doctorId}`, { auth: true });
    },

    // Appointments (patient)
    bookAppointment(slotId, reason) {
        return this.request("/appointments/", { method: "POST", body: { slot: slotId, reason_for_visit: reason }, auth: true });
    },
    getMyAppointments() {
        return this.request("/appointments/mine/", { auth: true });
    },
    cancelAppointment(id) {
        return this.request(`/appointments/${id}/cancel/`, { method: "POST", auth: true });
    },

    // Doctor — availability
    getAvailability() {
        return this.request("/slots/availability/", { auth: true });
    },
    createAvailability(data) {
        return this.request("/slots/availability/", { method: "POST", body: data, auth: true });
    },
    updateAvailability(id, data) {
        return this.request(`/slots/availability/${id}/`, { method: "PATCH", body: data, auth: true });
    },
    deleteAvailability(id) {
        return this.request(`/slots/availability/${id}/`, { method: "DELETE", auth: true });
    },

    // Doctor — manual slot
    createManualSlot(data) {
        return this.request("/slots/manual/", { method: "POST", body: data, auth: true });
    },

    // Doctor — generate slots
    generateSlots(daysAhead = 14) {
        return this.request(`/slots/generate/?days_ahead=${daysAhead}`, { method: "POST", auth: true });
    },

    // Doctor — appointments
    getPendingAppointments() {
        return this.request("/appointments/pending/", { auth: true });
    },
    approveAppointment(id) {
        return this.request(`/appointments/${id}/approve/`, { method: "POST", auth: true });
    },
    rejectAppointment(id, note = "") {
        return this.request(`/appointments/${id}/reject/`, { method: "POST", body: { rejection_note: note }, auth: true });
    },
    getAppointmentHistory() {
        return this.request("/appointments/history/", { auth: true });
    },
};


/**
 * Convert a DRF error response body into a human-readable string.
 * Handles:
 *   - { detail: "..." }                       → "..."
 *   - { non_field_errors: ["..."] }            → "..."
 *   - { field: ["msg", ...], field2: ... }     → "field: msg\nfield2: msg"
 *   - plain string                             → string
 */
function formatApiError(data, fallback = "Something went wrong.") {
    if (!data) return fallback;
    if (typeof data === "string") return data;
    if (typeof data !== "object") return String(data);

    // { detail: "..." }  — JWT / permission errors
    if (data.detail) return data.detail;

    // { non_field_errors: [...] }
    if (data.non_field_errors) {
        return Array.isArray(data.non_field_errors)
            ? data.non_field_errors.join(", ")
            : data.non_field_errors;
    }

    // Field-level: { email: ["A user with this email already exists."], ... }
    return Object.entries(data)
        .map(([key, val]) => {
            const msg = Array.isArray(val) ? val.join(", ") : val;
            return `${key}: ${msg}`;
        })
        .join("\n");
}
