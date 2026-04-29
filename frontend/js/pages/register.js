function renderRegister() {
    const app = document.getElementById("app");
    app.innerHTML = `
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h4 class="card-title mb-3">Patient Registration</h4>
                        <div id="reg-error" class="alert alert-danger d-none"></div>
                        <div id="reg-success" class="alert alert-success d-none"></div>
                        <form id="register-form">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">First Name *</label>
                                    <input type="text" class="form-control" id="reg-fname" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Last Name *</label>
                                    <input type="text" class="form-control" id="reg-lname" required>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email *</label>
                                <input type="email" class="form-control" id="reg-email" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password * (min 8 chars)</label>
                                <input type="password" class="form-control" id="reg-password" required minlength="8">
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Sex</label>
                                    <select class="form-select" id="reg-sex">
                                        <option value="">--</option>
                                        <option value="Male">Male</option>
                                        <option value="Female">Female</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Age</label>
                                    <input type="number" class="form-control" id="reg-age" min="1">
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Weight (kg)</label>
                                    <input type="number" step="0.1" class="form-control" id="reg-weight">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Blood Group</label>
                                    <select class="form-select" id="reg-blood">
                                        <option value="">--</option>
                                        <option>A+</option><option>A-</option>
                                        <option>B+</option><option>B-</option>
                                        <option>AB+</option><option>AB-</option>
                                        <option>O+</option><option>O-</option>
                                    </select>
                                </div>
                            </div>
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="reg-insured">
                                    <label class="form-check-label" for="reg-insured">Insured</label>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Allergies</label>
                                <textarea class="form-control" id="reg-allergies" rows="2"></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Register</button>
                        </form>
                        <p class="mt-3 text-center">Already have an account? <a href="#/login">Login</a></p>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.getElementById("register-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const errEl = document.getElementById("reg-error");
        const sucEl = document.getElementById("reg-success");
        errEl.classList.add("d-none");
        sucEl.classList.add("d-none");

        const body = {
            first_name: document.getElementById("reg-fname").value.trim(),
            last_name: document.getElementById("reg-lname").value.trim(),
            email: document.getElementById("reg-email").value.trim(),
            password: document.getElementById("reg-password").value,
        };

        const sex = document.getElementById("reg-sex").value;
        if (sex) body.sex = sex;

        const age = document.getElementById("reg-age").value;
        if (age) body.age = parseInt(age);

        const weight = document.getElementById("reg-weight").value;
        if (weight) body.weight = parseFloat(weight);

        const blood = document.getElementById("reg-blood").value;
        if (blood) body.blood_group = blood;

        body.is_insured = document.getElementById("reg-insured").checked;

        const allergies = document.getElementById("reg-allergies").value.trim();
        if (allergies) body.allergies = allergies;

        try {
            await api.register(body);
            sucEl.textContent = "Registration successful! You can now login.";
            sucEl.classList.remove("d-none");
            document.getElementById("register-form").reset();
        } catch (err) {
            let msg = "Registration failed.";
            if (err.data && typeof err.data === "object") {
                msg = Object.entries(err.data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`).join("\n");
            }
            errEl.textContent = msg;
            errEl.style.whiteSpace = "pre-wrap";
            errEl.classList.remove("d-none");
        }
    });
}
