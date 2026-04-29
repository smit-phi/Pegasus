async function renderDoctorSlots(doctorId) {
    const app = document.getElementById("app");
    app.innerHTML = `<h4>Available Slots</h4><p>Loading...</p>`;

    try {
        const slots = await api.getSlots(doctorId);
        if (!slots.length) {
            app.innerHTML = `
                <h4>Available Slots</h4>
                <p class="text-muted">No available slots for this doctor right now.</p>
                <a href="#/browse-doctors" class="btn btn-outline-secondary btn-sm">Back to Doctors</a>
            `;
            return;
        }

        const doctorName = slots[0].doctor_name;
        const deptName = slots[0].department_name;

        let html = `
            <h4>Available Slots — Dr. ${doctorName}</h4>
            <p class="text-muted">Department: ${deptName || "N/A"}</p>
            <div id="booking-msg" class="d-none"></div>
            <table class="table table-bordered">
                <thead><tr><th>Date</th><th>Start</th><th>End</th><th>Action</th></tr></thead>
                <tbody>
        `;
        slots.forEach(s => {
            html += `<tr>
                <td>${s.date}</td>
                <td>${s.start_time}</td>
                <td>${s.end_time}</td>
                <td>
                    <button class="btn btn-sm btn-primary book-btn" data-slot-id="${s.id}">Book</button>
                    <div class="book-form d-none mt-1" id="book-form-${s.id}">
                        <input type="text" class="form-control form-control-sm mb-1" placeholder="Reason for visit (optional)" id="reason-${s.id}">
                        <button class="btn btn-sm btn-success confirm-book-btn" data-slot-id="${s.id}">Confirm</button>
                        <button class="btn btn-sm btn-outline-secondary cancel-book-btn" data-slot-id="${s.id}">Cancel</button>
                    </div>
                </td>
            </tr>`;
        });
        html += `</tbody></table>
            <a href="#/browse-doctors" class="btn btn-outline-secondary btn-sm">Back to Doctors</a>`;
        app.innerHTML = html;

        // Show inline form when "Book" is clicked
        app.querySelectorAll(".book-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const slotId = btn.dataset.slotId;
                console.log(slotId);
                btn.classList.add("d-none");
                document.getElementById(`book-form-${slotId}`).classList.remove("d-none");
            });
        });

        // Cancel — hide the form, show the Book button again
        app.querySelectorAll(".cancel-book-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const slotId = btn.dataset.slotId;
                document.getElementById(`book-form-${slotId}`).classList.add("d-none");
                app.querySelector(`.book-btn[data-slot-id="${slotId}"]`).classList.remove("d-none");
            });
        });

        // Confirm booking
        app.querySelectorAll(".confirm-book-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const slotId = btn.dataset.slotId;
                const reason = document.getElementById(`reason-${slotId}`).value.trim();
                const msgEl = document.getElementById("booking-msg");

                btn.disabled = true;
                btn.textContent = "Booking...";

                try {
                    await api.bookAppointment(parseInt(slotId), reason);
                    msgEl.className = "alert alert-success";
                    msgEl.textContent = "Appointment booked successfully! Waiting for doctor approval.";
                    msgEl.classList.remove("d-none");
                    // Replace the form with a "Booked" label
                    const formEl = document.getElementById(`book-form-${slotId}`);
                    formEl.innerHTML = '<span class="badge bg-secondary">Booked</span>';
                    formEl.classList.remove("d-none");
                } catch (err) {
                    msgEl.className = "alert alert-danger";
                    let msg = "Booking failed.";
                    if (err.data) {
                        if (typeof err.data === "string") msg = err.data;
                        else if (err.data.non_field_errors) msg = err.data.non_field_errors.join(", ");
                        else if (err.data.slot) msg = Array.isArray(err.data.slot) ? err.data.slot.join(", ") : err.data.slot;
                        else msg = JSON.stringify(err.data);
                    }
                    msgEl.textContent = msg;
                    msgEl.classList.remove("d-none");
                    btn.disabled = false;
                    btn.textContent = "Confirm";
                }
            });
        });

    } catch (err) {
        app.innerHTML = `
            <h4>Available Slots</h4>
            <p class="text-danger">Failed to load slots. ${err.data ? JSON.stringify(err.data) : err.message}</p>
            <a href="#/browse-doctors" class="btn btn-outline-secondary btn-sm">Back to Doctors</a>
        `;
    }
}
