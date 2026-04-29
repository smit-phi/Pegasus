function renderPatientDashboard() {
    const app = document.getElementById("app");
    const name = auth.getUserName();
    app.innerHTML = `
        <h3>Welcome, ${name}</h3>
        <p>Patient Dashboard</p>
        <div class="row mt-4">
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5>Browse Doctors</h5>
                        <p class="text-muted">Find doctors by department and view available slots.</p>
                        <a href="#/browse-doctors" class="btn btn-outline-primary btn-sm">Browse</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5>My Appointments</h5>
                        <p class="text-muted">View, track, and cancel your appointments.</p>
                        <a href="#/my-appointments" class="btn btn-outline-primary btn-sm">View</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5>My Profile</h5>
                        <p class="text-muted">View and update your profile information.</p>
                        <a href="#/patient-profile" class="btn btn-outline-primary btn-sm">Profile</a>
                    </div>
                </div>
            </div>
        </div>
    `;
}
