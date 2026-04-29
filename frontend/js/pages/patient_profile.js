async function renderPatientProfile() {
    const app = document.getElementById("app");
    app.innerHTML = `<h4>My Profile</h4><p>Loading...</p>`;

    try {
        const profile = await api.getMe();
        const u = profile.user;
        app.innerHTML = `
            <h4>My Profile</h4>
            <div id="profile-msg" class="d-none"></div>
            <form id="profile-form">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">First Name</label>
                        <input type="text" class="form-control" id="pf-fname" value="${u.first_name || ""}">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Last Name</label>
                        <input type="text" class="form-control" id="pf-lname" value="${u.last_name || ""}">
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-control" value="${u.email}" disabled>
                </div>
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Sex</label>
                        <select class="form-select" id="pf-sex">
                            <option value="" ${!u.sex ? "selected" : ""}>--</option>
                            <option value="Male" ${u.sex === "Male" ? "selected" : ""}>Male</option>
                            <option value="Female" ${u.sex === "Female" ? "selected" : ""}>Female</option>
                        </select>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Age</label>
                        <input type="number" class="form-control" id="pf-age" value="${u.age || ""}">
                    </div>
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Weight (kg)</label>
                        <input type="number" step="0.1" class="form-control" id="pf-weight" value="${profile.weight || ""}">
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Blood Group</label>
                        <select class="form-select" id="pf-blood">
                            <option value="">--</option>
                            ${["A+","A-","B+","B-","AB+","AB-","O+","O-"].map(bg =>
                                `<option ${profile.blood_group === bg ? "selected" : ""}>${bg}</option>`
                            ).join("")}
                        </select>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Insured</label>
                        <div class="form-check mt-1">
                            <input class="form-check-input" type="checkbox" id="pf-insured" ${profile.is_insured ? "checked" : ""}>
                            <label class="form-check-label">Yes</label>
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <label class="form-label">Allergies</label>
                    <textarea class="form-control" id="pf-allergies" rows="2">${profile.allergies || ""}</textarea>
                </div>
                <button type="submit" class="btn btn-primary">Update Profile</button>
            </form>
        `;

        document.getElementById("profile-form").addEventListener("submit", async (e) => {
            e.preventDefault();
            const msgEl = document.getElementById("profile-msg");
            const body = {
                user: {
                    first_name: document.getElementById("pf-fname").value.trim(),
                    last_name: document.getElementById("pf-lname").value.trim(),
                    sex: document.getElementById("pf-sex").value,
                    age: parseInt(document.getElementById("pf-age").value) || null,
                },
                weight: parseFloat(document.getElementById("pf-weight").value) || null,
                blood_group: document.getElementById("pf-blood").value,
                is_insured: document.getElementById("pf-insured").checked,
                allergies: document.getElementById("pf-allergies").value.trim(),
            };
            try {
                await api.updateMe(body);
                // Update stored name
                auth.setUserInfo("patient", `${body.user.first_name} ${body.user.last_name}`);
                msgEl.className = "alert alert-success";
                msgEl.textContent = "Profile updated.";
                msgEl.classList.remove("d-none");
            } catch (err) {
                msgEl.className = "alert alert-danger";
                msgEl.textContent = "Update failed: " + (err.data ? JSON.stringify(err.data) : err.message);
                msgEl.classList.remove("d-none");
            }
        });

    } catch (err) {
        app.innerHTML = `<h4>My Profile</h4><p class="text-danger">Failed to load profile.</p>`;
    }
}
