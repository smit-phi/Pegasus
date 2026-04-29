async function renderMyAppointments() {
    const app = document.getElementById("app");
    app.innerHTML = `<h4>My Appointments</h4><p>Loading...</p>`;

    try {
        const appointments = await api.getMyAppointments();
        if (!appointments.length) {
            app.innerHTML = `
                <h4>My Appointments</h4>
                <p class="text-muted">You don't have any appointments yet.</p>
                <a href="#/browse-doctors" class="btn btn-outline-primary btn-sm">Browse Doctors</a>
            `;
            return;
        }

        let html = `
            <h4>My Appointments</h4>
            <div id="apt-msg" class="d-none"></div>
            <table class="table table-bordered">
                <thead><tr><th>Date</th><th>Time</th><th>Doctor</th><th>Department</th><th>Status</th><th>Reason</th><th>Action</th></tr></thead>
                <tbody>
        `;
        appointments.forEach(a => {
            const sd = a.slot_detail;
            const canCancel = a.status === "pending" || a.status === "approved";
            html += `<tr>
                <td>${sd.date}</td>
                <td>${sd.start_time} - ${sd.end_time}</td>
                <td>${sd.doctor_name}</td>
                <td>${sd.department_name || "-"}</td>
                <td><span class="status-${a.status}">${a.status.toUpperCase()}</span></td>
                <td>${a.reason_for_visit || "-"}</td>
                <td>
                    ${canCancel ? `<button class="btn btn-sm btn-outline-danger cancel-btn" data-id="${a.id}">Cancel</button>` : "-"}
                    ${a.status === "rejected" && a.rejection_note ? `<small class="text-danger d-block">Note: ${a.rejection_note}</small>` : ""}
                </td>
            </tr>`;
        });
        html += '</tbody></table>';
        app.innerHTML = html;

        app.querySelectorAll(".cancel-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                if (!confirm("Are you sure you want to cancel this appointment?")) return;
                const msgEl = document.getElementById("apt-msg");
                try {
                    await api.cancelAppointment(parseInt(btn.dataset.id));
                    msgEl.className = "alert alert-success";
                    msgEl.textContent = "Appointment cancelled.";
                    msgEl.classList.remove("d-none");
                    // Refresh
                    setTimeout(() => renderMyAppointments(), 500);
                } catch (err) {
                    msgEl.className = "alert alert-danger";
                    msgEl.textContent = err.data?.error || "Failed to cancel.";
                    msgEl.classList.remove("d-none");
                }
            });
        });

    } catch (err) {
        app.innerHTML = `<h4>My Appointments</h4><p class="text-danger">Failed to load appointments.</p>`;
    }
}
