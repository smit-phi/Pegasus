async function renderDoctorProfile() {
    const app = document.getElementById("app");
    app.innerHTML = `<h4>My Profile</h4><p>Loading...</p>`;

    try {
        const profile = await api.getMe();
        const u = profile.user;
        const dept = profile.department;

        app.innerHTML = `
            <h4>Doctor Profile</h4>
            <div class="card" style="max-width: 500px;">
                <div class="card-body">
                    <table class="table table-borderless mb-0">
                        <tr><td><strong>Name</strong></td><td>Dr. ${u.first_name} ${u.last_name}</td></tr>
                        <tr><td><strong>Email</strong></td><td>${u.email}</td></tr>
                        <tr><td><strong>Department</strong></td><td>${dept ? dept.name : "N/A"}</td></tr>
                        <tr><td><strong>Degree</strong></td><td>${profile.degree || "N/A"}</td></tr>
                        <tr><td><strong>Slot Duration</strong></td><td>${profile.slot_duration} min</td></tr>
                        <tr><td><strong>Sex</strong></td><td>${u.sex || "N/A"}</td></tr>
                        <tr><td><strong>Age</strong></td><td>${u.age || "N/A"}</td></tr>
                    </table>
                </div>
            </div>
        `;

    } catch (err) {
        app.innerHTML = `<h4>Doctor Profile</h4><p class="text-danger">Failed to load profile.</p>`;
    }
}
