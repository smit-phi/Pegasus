async function renderBrowseDoctors() {
    const app = document.getElementById("app");
    app.innerHTML = `
        <h4>Browse Doctors</h4>
        <div class="mb-3">
            <label class="form-label">Select Department</label>
            <select class="form-select" id="dept-select" style="max-width:400px;">
                <option value="">Loading departments...</option>
            </select>
        </div>
        <div id="doctors-list"></div>
    `;

    try {
        const departments = await api.getDepartments();
        const sel = document.getElementById("dept-select");
        sel.innerHTML = '<option value="">-- Select a department --</option>';
        departments.forEach(d => {
            sel.innerHTML += `<option value="${d.id}">${d.name}</option>`;
        });

        sel.addEventListener("change", async () => {
            const deptId = sel.value;
            const listEl = document.getElementById("doctors-list");
            if (!deptId) { listEl.innerHTML = ""; return; }

            listEl.innerHTML = "<p>Loading doctors...</p>";
            try {
                const doctors = await api.getDoctors(deptId);
                if (!doctors.length) {
                    listEl.innerHTML = "<p class='text-muted'>No doctors found in this department.</p>";
                    return;
                }
                let html = '<table class="table table-bordered"><thead><tr><th>Name</th><th>Email</th><th>Degree</th><th>Slot Duration</th><th>Action</th></tr></thead><tbody>';
                doctors.forEach(d => {
                    html += `<tr>
                        <td>${d.full_name}</td>
                        <td>${d.email}</td>
                        <td>${d.degree || "-"}</td>
                        <td>${d.slot_duration} min</td>
                        <td><a href="#/doctor-slots/${d.id}" class="btn btn-sm btn-outline-primary">View Slots</a></td>
                    </tr>`;
                });
                html += '</tbody></table>';
                listEl.innerHTML = html;
            } catch (err) {
                listEl.innerHTML = `<p class="text-danger">Error loading doctors.</p>`;
            }
        });
    } catch (err) {
        app.innerHTML += `<p class="text-danger">Failed to load departments.</p>`;
    }
}
