function renderDoctorManualSlot() {
    const app = document.getElementById("app");
    app.innerHTML = `
        <h4>Add Manual Slot</h4>
        <div id="manual-msg" class="d-none"></div>
        <form id="manual-slot-form" style="max-width: 500px;">
            <div class="mb-3">
                <label class="form-label">Date</label>
                <input type="date" class="form-control" id="ms-date" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Start Time</label>
                <input type="time" class="form-control" id="ms-start" required>
            </div>
            <div class="mb-3">
                <label class="form-label">End Time</label>
                <input type="time" class="form-control" id="ms-end" required>
            </div>
            <button type="submit" class="btn btn-primary">Create Slot</button>
        </form>
    `;

    // Set min date to today
    const today = new Date().toISOString().split("T")[0];
    document.getElementById("ms-date").setAttribute("min", today);

    document.getElementById("manual-slot-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const msgEl = document.getElementById("manual-msg");
        const body = {
            date: document.getElementById("ms-date").value,
            start_time: document.getElementById("ms-start").value,
            end_time: document.getElementById("ms-end").value,
        };

        try {
            await api.createManualSlot(body);
            msgEl.className = "alert alert-success";
            msgEl.textContent = "Manual slot created successfully!";
            msgEl.classList.remove("d-none");
            document.getElementById("manual-slot-form").reset();
        } catch (err) {
            msgEl.className = "alert alert-danger";
            let msg = "Failed to create slot.";
            if (err.data && typeof err.data === "object") {
                msg = Object.entries(err.data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`).join("\n");
            }
            msgEl.textContent = msg;
            msgEl.style.whiteSpace = "pre-wrap";
            msgEl.classList.remove("d-none");
        }
    });
}
