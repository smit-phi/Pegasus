async function renderDoctorHistory() {
    const app = document.getElementById("app");
    app.innerHTML = `<h4>Appointment History</h4><p>Loading...</p>`;

    try {
        const appointments = await api.getAppointmentHistory();

        if (!appointments.length) {
            app.innerHTML = `
                <h4>Appointment History</h4>
                <p class="text-muted">No appointment history.</p>
            `;
            return;
        }

        let html = `
            <h4>Appointment History</h4>
            <table class="table table-bordered">
                <thead><tr><th>Patient</th><th>Date</th><th>Time</th><th>Status</th><th>Reason</th><th>Rejection Note</th></tr></thead>
                <tbody>
        `;
        appointments.forEach(a => {
            const sd = a.slot_detail;
            html += `<tr>
                <td>${a.patient_name}</td>
                <td>${sd.date}</td>
                <td>${sd.start_time} - ${sd.end_time}</td>
                <td><span class="status-${a.status}">${a.status.toUpperCase()}</span></td>
                <td>${a.reason_for_visit || "-"}</td>
                <td>${a.rejection_note || "-"}</td>
            </tr>`;
        });
        html += '</tbody></table>';
        app.innerHTML = html;

    } catch (err) {
        app.innerHTML = `<h4>Appointment History</h4><p class="text-danger">Failed to load.</p>`;
    }
}
