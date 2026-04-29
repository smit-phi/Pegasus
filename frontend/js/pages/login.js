function renderLogin() {
    const app = document.getElementById("app");
    app.innerHTML = `
        <div class="row justify-content-center">
            <div class="col-md-5">
                <div class="card">
                    <div class="card-body">
                        <h4 class="card-title mb-3">Login</h4>
                        <div id="login-error" class="alert alert-danger d-none"></div>
                        <form id="login-form">
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control" id="login-email" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password</label>
                                <input type="password" class="form-control" id="login-password" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Login</button>
                        </form>
                        <p class="mt-3 text-center">Don't have an account? <a href="#/register">Register as Patient</a></p>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.getElementById("login-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const errEl = document.getElementById("login-error");
        errEl.classList.add("d-none");

        const email = document.getElementById("login-email").value.trim();
        const password = document.getElementById("login-password").value;

        try {
            const data = await api.login(email, password);
            auth.saveTokens(data);

            // Fetch profile to get role
            const me = await api.getMe();
            const role = me.user ? me.user.role : "unknown";
            const name = me.user ? `${me.user.first_name} ${me.user.last_name}` : email;
            auth.setUserInfo(role, name);

            if (role === "doctor") {
                window.location.hash = "#/doctor";
            } else {
                window.location.hash = "#/patient";
            }
        } catch (err) {
            errEl.textContent = err.data?.detail || "Login failed. Check your credentials.";
            errEl.classList.remove("d-none");
        }
    });
}
