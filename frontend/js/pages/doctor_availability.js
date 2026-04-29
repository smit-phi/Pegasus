const DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

async function renderDoctorAvailability() {
    const app = document.getElementById("app");
    app.innerHTML = `<h4>My Availability</h4><p>Loading...</p>`;

    try {
        // Get doctor profile id first
        const me = await api.getMe();
        const doctorId = me.id;

        const availability = await api.getAvailability();

        let html = `
            <h4>My Weekly Availability</h4>
            <div id="avail-msg" class="d-none"></div>

            <h5 class="mt-4">Current Schedule</h5>
        `;

        if (availability.length) {
            html += `<table class="table table-bordered">
                <thead><tr><th>Day</th><th>Start</th><th>End</th><th>Active</th><th>Actions</th></tr></thead>
                <tbody>`;
            availability.forEach(a => {
                html += `<tr>
                    <td>${a.day_display}</td>
                    <td>${a.start_time}</td>
                    <td>${a.end_time}</td>
                    <td>${a.is_active ? "✅" : "❌"}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-warning toggle-btn" data-id="${a.id}" data-active="${a.is_active}">${a.is_active ? "Deactivate" : "Activate"}</button>
                        <button class="btn btn-sm btn-outline-danger delete-btn" data-id="${a.id}">Delete</button>
                    </td>
                </tr>`;
            });
            html += '</tbody></table>';
        } else {
            html += `<p class="text-muted">No availability set yet.</p>`;
        }

        // Generate slots button
        html += `
            <div class="mt-3 mb-4">
                <button class="btn btn-success" id="generate-slots-btn">Generate Slots (next 14 days)</button>
                <span id="gen-msg" class="ms-2"></span>
            </div>
        `;

        // Add new availability form
        html += `
            <h5 class="mt-4">Add Availability</h5>
            <form id="add-avail-form" class="row g-2 align-items-end mb-4">
                <div class="col-auto">
                    <label class="form-label">Day</label>
                    <select class="form-select" id="avail-day" required>
                        ${DAY_NAMES.map((d, i) => `<option value="${i}">${d}</option>`).join("")}
                    </select>
                </div>
                <div class="col-auto">
                    <label class="form-label">Start Time</label>
                    <input type="time" class="form-control" id="avail-start" required>
                </div>
                <div class="col-auto">
                    <label class="form-label">End Time</label>
                    <input type="time" class="form-control" id="avail-end" required>
                </div>
                <div class="col-auto">
                    <button type="submit" class="btn btn-primary">Add</button>
                </div>
            </form>
        `;

        app.innerHTML = html;

        // Toggle active/inactive
        app.querySelectorAll(".toggle-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const id = btn.dataset.id;
                const isActive = btn.dataset.active === "true";
                try {
                    await api.updateAvailability(id, { is_active: !isActive });
                    renderDoctorAvailability();
                } catch (err) {
                    showAvailMsg("Failed to toggle: " + (err.data ? JSON.stringify(err.data) : err.message), "danger");
                }
            });
        });

        // Delete
        app.querySelectorAll(".delete-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                if (!confirm("Delete this availability entry?")) return;
                try {
                    await api.deleteAvailability(btn.dataset.id);
                    renderDoctorAvailability();
                } catch (err) {
                    showAvailMsg("Failed to delete.", "danger");
                }
            });
        });

        // Generate slots
        document.getElementById("generate-slots-btn").addEventListener("click", async () => {
            const genMsg = document.getElementById("gen-msg");
            genMsg.textContent = "Generating...";
            try {
                const res = await api.generateSlots(14);
                genMsg.textContent = res.message || "Slots generation started!";
                genMsg.className = "ms-2 text-success";
            } catch (err) {
                genMsg.textContent = "Failed: " + (err.data ? JSON.stringify(err.data) : err.message);
                genMsg.className = "ms-2 text-danger";
            }
        });

        // Add availability
        document.getElementById("add-avail-form").addEventListener("submit", async (e) => {
            e.preventDefault();
            const body = {
                doctor: doctorId,
                day_of_week: parseInt(document.getElementById("avail-day").value),
                start_time: document.getElementById("avail-start").value,
                end_time: document.getElementById("avail-end").value,
            };
            try {
                await api.createAvailability(body);
                renderDoctorAvailability();
            } catch (err) {
                showAvailMsg("Failed: " + (err.data ? JSON.stringify(err.data) : err.message), "danger");
            }
        });

    } catch (err) {
        app.innerHTML = `<h4>My Availability</h4><p class="text-danger">Failed to load. ${err.message}</p>`;
    }
}

function showAvailMsg(text, type) {
    const el = document.getElementById("avail-msg");
    if (!el) return;
    el.className = `alert alert-${type}`;
    el.textContent = text;
    el.classList.remove("d-none");
}
