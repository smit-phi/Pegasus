function renderDoctorDashboard() {
    const app = document.getElementById("app");
    const name = auth.getUserName();
    app.innerHTML = `
        <h3>Welcome, Dr. ${name}</h3>
        <p>Doctor Dashboard</p>
        <div class="row mt-4">
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5>My Availability</h5>
                        <p class="text-muted">Set your weekly availability schedule.</p>
                        <a href="#/doctor-availability" class="btn btn-outline-primary btn-sm">Manage</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5>Add Manual Slot</h5>
                        <p class="text-muted">Create a one-off slot for a specific date/time.</p>
                        <a href="#/doctor-manual-slot" class="btn btn-outline-primary btn-sm">Add Slot</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5>Pending Appointments</h5>
                        <p class="text-muted">Review and approve/reject patient bookings.</p>
                        <a href="#/doctor-pending" class="btn btn-outline-primary btn-sm">Review</a>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5>Appointment History</h5>
                        <p class="text-muted">View past and upcoming appointments.</p>
                        <a href="#/doctor-history" class="btn btn-outline-primary btn-sm">View</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5>My Profile</h5>
                        <p class="text-muted">View your profile details.</p>
                        <a href="#/doctor-profile" class="btn btn-outline-primary btn-sm">Profile</a>
                    </div>
                </div>
            </div>
        </div>
    `;
}
