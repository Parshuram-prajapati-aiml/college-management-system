// Student Portal Frontend JavaScript Logic

// 1. Student Dashboard Logic
async function loadStudentDashboard() {
    const userId = localStorage.getItem("user_id");
    const resAuth = await apiRequest("/api/auth/me");
    if (!resAuth || !resAuth.ok) return;

    const user = await resAuth.json();

    // Fetch student profile via students API
    const resStudents = await apiRequest(`/api/students?search=${encodeURIComponent(user.username)}`);
    if (!resStudents || !resStudents.ok) return;
    const students = await resStudents.json();
    if (students.length === 0) return;

    const student = students[0];

    document.getElementById("stat-semester").textContent = student.semester || "5";
    document.getElementById("stat-gpa").textContent = student.gpa || "3.75";

    // Attendance summary
    const resAtt = await apiRequest("/api/attendance/me");
    if (resAtt && resAtt.ok) {
        const attSummaries = await resAtt.json();
        let totalClassesAll = 0;
        let presentAll = 0;

        attSummaries.forEach(s => {
            totalClassesAll += s.total_classes;
            presentAll += s.present_count;
        });

        const overallPct = totalClassesAll > 0 ? (presentAll / totalClassesAll * 100).toFixed(2) : "100.0";
        document.getElementById("stat-attendance-pct").textContent = `${overallPct}%`;
        document.getElementById("stat-courses-count").textContent = attSummaries.length || "1";
    }

    // Recent Announcements
    const resAnn = await apiRequest("/api/announcements");
    if (resAnn && resAnn.ok) {
        const anns = await resAnn.json();
        const tbody = document.getElementById("student-ann-tbody");
        if (tbody) {
            tbody.innerHTML = anns.slice(0, 5).map(a => `
                <tr>
                    <td><strong>${escapeHtml(a.title)}</strong></td>
                    <td>${escapeHtml(a.content.substring(0, 60))}...</td>
                    <td>${escapeHtml(new Date(a.created_at).toLocaleDateString())}</td>
                </tr>
            `).join("");
        }
    }
}

// 2. Student Profile View
async function loadStudentProfile() {
    const resAuth = await apiRequest("/api/auth/me");
    if (!resAuth || !resAuth.ok) return;
    const user = await resAuth.json();

    const resStudents = await apiRequest(`/api/students?search=${encodeURIComponent(user.username)}`);
    if (!resStudents || !resStudents.ok) return;
    const students = await resStudents.json();
    if (students.length === 0) return;

    const s = students[0];

    document.getElementById("profile-name").textContent = s.student_name;
    document.getElementById("profile-usn").textContent = s.usn;
    document.getElementById("profile-reg").textContent = s.registration_number;
    document.getElementById("profile-email").textContent = s.email;
    document.getElementById("profile-phone").textContent = s.phone || "N/A";
    document.getElementById("profile-address").textContent = s.address || "N/A";
    document.getElementById("profile-dob").textContent = s.date_of_birth ? new Date(s.date_of_birth).toLocaleDateString() : "N/A";
    document.getElementById("profile-gender").textContent = s.gender || "N/A";
    document.getElementById("profile-department").textContent = s.department_name || "N/A";
    document.getElementById("profile-program").textContent = s.program_name || "N/A";
    document.getElementById("profile-academic-year").textContent = s.academic_year;
    document.getElementById("profile-semester").textContent = s.semester;
    document.getElementById("profile-gpa").textContent = s.gpa;
    document.getElementById("profile-status").textContent = s.status;
}

// 3. Student Attendance View
async function loadStudentAttendance() {
    const res = await apiRequest("/api/attendance/me");
    if (!res || !res.ok) return;

    const summaries = await res.json();
    const tbody = document.getElementById("student-attendance-tbody");
    if (!tbody) return;

    if (summaries.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--text-muted);">No attendance records found.</td></tr>`;
        return;
    }

    tbody.innerHTML = summaries.map(s => {
        let barClass = "success";
        if (s.percentage < 75) barClass = "danger";
        else if (s.percentage < 85) barClass = "warning";

        return `
            <tr>
                <td><strong>${escapeHtml(s.course_code)}</strong> - ${escapeHtml(s.course_name)}</td>
                <td>${s.total_classes}</td>
                <td>${s.present_count}</td>
                <td>${s.absent_count}</td>
                <td style="width: 200px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.25rem;">
                        <span style="font-weight:600;">${s.percentage}%</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill ${barClass}" style="width: ${s.percentage}%;"></div>
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

// 4. Student Marks View
async function loadStudentMarks() {
    const res = await apiRequest("/api/marks/me");
    if (!res || !res.ok) return;

    const marks = await res.json();
    const tbody = document.getElementById("student-marks-tbody");
    if (!tbody) return;

    if (marks.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;color:var(--text-muted);">No internal marks recorded yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = marks.map(m => `
        <tr>
            <td><strong>${escapeHtml(m.course_name || "Course")}</strong></td>
            <td>${escapeHtml(m.assessment_name)}</td>
            <td>${m.internal_marks}</td>
            <td>${m.assignment_marks}</td>
            <td>${m.exam_marks}</td>
            <td><strong>${m.total_marks}</strong></td>
            <td><span class="badge badge-active">${escapeHtml(m.grade || "-")}</span></td>
            <td>${escapeHtml(m.remarks || "-")}</td>
        </tr>
    `).join("");
}

// 5. Student Study Materials View
async function loadStudentMaterials() {
    const res = await apiRequest("/api/materials");
    if (!res || !res.ok) return;

    const materials = await res.json();
    const tbody = document.getElementById("student-materials-tbody");
    if (!tbody) return;

    if (materials.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--text-muted);">No published study materials available.</td></tr>`;
        return;
    }

    tbody.innerHTML = materials.map(m => `
        <tr>
            <td><strong>${escapeHtml(m.title)}</strong></td>
            <td>${escapeHtml(m.course_name || "N/A")}</td>
            <td>${escapeHtml(m.teacher_name || "Instructor")}</td>
            <td><span class="badge badge-active">${escapeHtml(m.file_type)}</span></td>
            <td>
                <a href="${API_BASE_URL}${escapeHtml(m.file_path)}" target="_blank" class="btn btn-sm btn-primary">Download</a>
            </td>
        </tr>
    `).join("");
}

// 6. Student Announcements View
async function loadStudentAnnouncements() {
    const res = await apiRequest("/api/announcements");
    if (!res || !res.ok) return;

    const anns = await res.json();
    const container = document.getElementById("student-announcements-list");
    if (!container) return;

    if (anns.length === 0) {
        container.innerHTML = `<div style="text-align:center;color:var(--text-muted);padding:2rem;">No announcements at this time.</div>`;
        return;
    }

    container.innerHTML = anns.map(a => `
        <div class="card" style="margin-bottom:1rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                <h3 style="color:var(--primary);">${escapeHtml(a.title)}</h3>
                <span style="font-size:0.75rem;color:var(--text-muted);">${new Date(a.created_at).toLocaleDateString()}</span>
            </div>
            <p style="color:var(--text);white-space:pre-wrap;">${escapeHtml(a.content)}</p>
            <div style="margin-top:0.5rem;font-size:0.75rem;color:var(--text-muted);">
                Posted by: <strong>${escapeHtml(a.author_name || "Faculty")}</strong>
            </div>
        </div>
    `).join("");
}

// 7. Student Document Upload & Receipt View
async function loadStudentDocuments() {
    const res = await apiRequest("/api/documents");
    if (!res || !res.ok) return;

    const docs = await res.json();
    const tbody = document.getElementById("student-documents-tbody");
    if (!tbody) return;

    if (docs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--text-muted);">No documents uploaded yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = docs.map(d => `
        <tr>
            <td><strong>${escapeHtml(d.document_type)}</strong></td>
            <td><a href="${API_BASE_URL}${escapeHtml(d.file_path)}" target="_blank" class="btn btn-sm btn-secondary">View File</a></td>
            <td><span class="badge badge-${d.status.toLowerCase()}">${escapeHtml(d.status)}</span></td>
            <td>${d.rejection_reason ? `<span style="color:var(--danger);">${escapeHtml(d.rejection_reason)}</span>` : "-"}</td>
            <td>${d.receipt ? `<strong>${escapeHtml(d.receipt.receipt_number)}</strong>` : "Pending Verification"}</td>
            <td>${escapeHtml(new Date(d.upload_date).toLocaleDateString())}</td>
        </tr>
    `).join("");
}

async function uploadStudentDocument(event) {
    event.preventDefault();
    const docType = document.getElementById("doc-type").value;
    const fileInput = document.getElementById("doc-file");

    if (!docType || !fileInput.files[0]) {
        showToast("Please select document type and choose a file.", "warning");
        return;
    }

    const formData = new FormData();
    formData.append("document_type", docType);
    formData.append("file", fileInput.files[0]);

    const res = await apiRequest("/api/documents/upload", {
        method: "POST",
        body: formData
    });

    if (!res) return;
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Upload failed", "danger");
        return;
    }

    showToast("Document uploaded successfully!", "success");
    closeModal("upload-doc-modal");
    loadStudentDocuments();
}
