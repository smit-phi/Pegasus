// Main application entry point — registers routes and manages nav.
(function () {
    function updateNav() {
        const navEl = document.getElementById("nav-links");
        const loggedIn = auth.isLoggedIn();
        const role = auth.getRole();

        let links = "";

        if (!loggedIn) {
            links = `
                <a class="nav-link" href="#/login">Login</a>
                <a class="nav-link" href="#/register">Register</a>
            `;
        } else if (role === "patient") {
            links = `
                <a class="nav-link" href="#/patient">Dashboard</a>
                <a class="nav-link" href="#/browse-doctors">Doctors</a>
                <a class="nav-link" href="#/my-appointments">Appointments</a>
                <a class="nav-link" href="#/patient-profile">Profile</a>
                <a class="nav-link" href="#" id="logout-btn">Logout</a>
            `;
        } else if (role === "doctor") {
            links = `
                <a class="nav-link" href="#/doctor">Dashboard</a>
                <a class="nav-link" href="#/doctor-availability">Availability</a>
                <a class="nav-link" href="#/doctor-manual-slot">Manual Slot</a>
                <a class="nav-link" href="#/doctor-pending">Pending</a>
                <a class="nav-link" href="#/doctor-history">History</a>
                <a class="nav-link" href="#/doctor-profile">Profile</a>
                <a class="nav-link" href="#" id="logout-btn">Logout</a>
            `;
        }

        navEl.innerHTML = links;

        const logoutBtn = document.getElementById("logout-btn");
        if (logoutBtn) {
            logoutBtn.addEventListener("click", (e) => {
                e.preventDefault();
                auth.logout();
                updateNav();
            });
        }
    }

    // Register routes
    // Public
    router.register("#/login", () => { updateNav(); renderLogin(); });
    router.register("#/register", () => { updateNav(); renderRegister(); });

    // Patient
    router.register("#/patient", () => {
        if (!auth.isLoggedIn() || auth.getRole() !== "patient") { window.location.hash = "#/login"; return; }
        updateNav(); renderPatientDashboard();
    });
    router.register("#/browse-doctors", () => {
        if (!auth.isLoggedIn()) { window.location.hash = "#/login"; return; }
        updateNav(); renderBrowseDoctors();
    });
    router.register("#/doctor-slots/:id", (id) => {
        if (!auth.isLoggedIn() || auth.getRole() !== "patient") { window.location.hash = "#/login"; return; }
        updateNav(); renderDoctorSlots(id);
    });
    router.register("#/my-appointments", () => {
        if (!auth.isLoggedIn() || auth.getRole() !== "patient") { window.location.hash = "#/login"; return; }
        updateNav(); renderMyAppointments();
    });
    router.register("#/patient-profile", () => {
        if (!auth.isLoggedIn() || auth.getRole() !== "patient") { window.location.hash = "#/login"; return; }
        updateNav(); renderPatientProfile();
    });

    // Doctor
    router.register("#/doctor", () => {
        if (!auth.isLoggedIn() || auth.getRole() !== "doctor") { window.location.hash = "#/login"; return; }
        updateNav(); renderDoctorDashboard();
    });
    router.register("#/doctor-availability", () => {
        if (!auth.isLoggedIn() || auth.getRole() !== "doctor") { window.location.hash = "#/login"; return; }
        updateNav(); renderDoctorAvailability();
    });
    router.register("#/doctor-manual-slot", () => {
        if (!auth.isLoggedIn() || auth.getRole() !== "doctor") { window.location.hash = "#/login"; return; }
        updateNav(); renderDoctorManualSlot();
    });
    router.register("#/doctor-pending", () => {
        if (!auth.isLoggedIn() || auth.getRole() !== "doctor") { window.location.hash = "#/login"; return; }
        updateNav(); renderDoctorPending();
    });
    router.register("#/doctor-history", () => {
        if (!auth.isLoggedIn() || auth.getRole() !== "doctor") { window.location.hash = "#/login"; return; }
        updateNav(); renderDoctorHistory();
    });
    router.register("#/doctor-profile", () => {
        if (!auth.isLoggedIn() || auth.getRole() !== "doctor") { window.location.hash = "#/login"; return; }
        updateNav(); renderDoctorProfile();
    });

    // Default route
    router.register("#/", () => {
        updateNav();
        if (auth.isLoggedIn()) {
            const role = auth.getRole();
            if (role === "doctor") { window.location.hash = "#/doctor"; }
            else { window.location.hash = "#/patient"; }
        } else {
            window.location.hash = "#/login";
        }
    });

    // Initialize
    router.init();
})();
