async function renderDoctorPending() {
    const app = document.getElementById("app");
    app.innerHTML = `<h4>Pending Appointments</h4><p>Loading...</p>`;

    try {
        const appointments = await api.getPendingAppointments();

        if (!appointments.length) {
            app.innerHTML = `
                <h4>Pending Appointments</h4>
                <p class="text-muted">No pending appointments.</p>
            `;
            return;
        }

        let html = `
            <h4>Pending Appointments</h4>
            <div id="pending-msg" class="d-none"></div>
            <table class="table table-bordered">
                <thead><tr><th>Patient</th><th>Date</th><th>Time</th><th>Reason</th><th>Actions</th></tr></thead>
                <tbody>
        `;
        appointments.forEach(a => {
            const sd = a.slot_detail;
            html += `<tr id="row-${a.id}">
                <td>${a.patient_name}</td>
                <td>${sd.date}</td>
                <td>${sd.start_time} - ${sd.end_time}</td>
                <td>${a.reason_for_visit || "-"}</td>
                <td>
                    <div class="action-btns-${a.id}">
                        <button class="btn btn-sm btn-success approve-btn" data-id="${a.id}">Approve</button>
                        <button class="btn btn-sm btn-danger reject-btn" data-id="${a.id}">Reject</button>
                    </div>
                    <div class="reject-form d-none" id="reject-form-${a.id}">
                        <input type="text" class="form-control form-control-sm mb-1" placeholder="Rejection note (optional)" id="reject-note-${a.id}">
                        <button class="btn btn-sm btn-danger confirm-reject-btn" data-id="${a.id}">Confirm Reject</button>
                        <button class="btn btn-sm btn-outline-secondary cancel-reject-btn" data-id="${a.id}">Cancel</button>
                    </div>
                </td>
            </tr>`;
        });
        html += '</tbody></table>';
        app.innerHTML = html;

        // Approve
        app.querySelectorAll(".approve-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                try {
                    await api.approveAppointment(parseInt(btn.dataset.id));
                    showPendingMsg("Appointment approved!", "success");
                    setTimeout(() => renderDoctorPending(), 500);
                } catch (err) {
                    showPendingMsg("Failed to approve.", "danger");
                }
            });
        });

        // Show reject form
        app.querySelectorAll(".reject-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const id = btn.dataset.id;
                document.querySelector(`.action-btns-${id}`).classList.add("d-none");
                document.getElementById(`reject-form-${id}`).classList.remove("d-none");
            });
        });

        // Cancel reject
        app.querySelectorAll(".cancel-reject-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const id = btn.dataset.id;
                document.getElementById(`reject-form-${id}`).classList.add("d-none");
                document.querySelector(`.action-btns-${id}`).classList.remove("d-none");
            });
        });

        // Confirm reject
        app.querySelectorAll(".confirm-reject-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.dataset.id;
                const note = document.getElementById(`reject-note-${id}`).value.trim();
                btn.disabled = true;
                btn.textContent = "Rejecting...";
                try {
                    await api.rejectAppointment(parseInt(id), note);
                    showPendingMsg("Appointment rejected.", "warning");
                    setTimeout(() => renderDoctorPending(), 500);
                } catch (err) {
                    showPendingMsg("Failed to reject.", "danger");
                    btn.disabled = false;
                    btn.textContent = "Confirm Reject";
                }
            });
        });

    } catch (err) {
        app.innerHTML = `<h4>Pending Appointments</h4><p class="text-danger">Failed to load.</p>`;
    }
}

function showPendingMsg(text, type) {
    const el = document.getElementById("pending-msg");
    if (!el) return;
    el.className = `alert alert-${type}`;
    el.textContent = text;
    el.classList.remove("d-none");
}
