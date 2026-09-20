// Teacher Portal Frontend JavaScript Logic

// 1. Dashboard Logic
async function loadTeacherDashboard() {
    const resClasses = await apiRequest("/api/classes");
    if (!resClasses || !resClasses.ok) return;
    const classes = await resClasses.json();

    document.getElementById("stat-my-classes").textContent = classes.length;

    const resAnn = await apiRequest("/api/announcements");
    if (resAnn && resAnn.ok) {
        const anns = await resAnn.json();
        const tbody = document.getElementById("teacher-ann-tbody");
        if (tbody) {
            tbody.innerHTML = anns.slice(0, 5).map(a => `
                <tr>
                    <td><strong>${escapeHtml(a.title)}</strong></td>
                    <td><span class="badge badge-active">${escapeHtml(a.target_type)}</span></td>
                    <td>${escapeHtml(new Date(a.created_at).toLocaleDateString())}</td>
                </tr>
            `).join("");
        }
    }
}

// 2. Attendance Marking
async function loadTeacherAttendancePage() {
    const res = await apiRequest("/api/classes");
    if (!res || !res.ok) return;

    const classes = await res.json();
    const select = document.getElementById("attendance-class-select");
    if (!select) return;

    select.innerHTML = `<option value="">-- Select Assigned Class --</option>` +
        classes.map(c => `<option value="${c.class_id}">${escapeHtml(c.course_code)} - ${escapeHtml(c.course_name)} (${escapeHtml(c.semester)})</option>`).join("");

    // Set today's date
    const dateInput = document.getElementById("attendance-date");
    if (dateInput) {
        dateInput.value = new Date().toISOString().split("T")[0];
    }
}

async function loadClassStudentsForAttendance() {
    const classId = document.getElementById("attendance-class-select").value;
    const tbody = document.getElementById("attendance-students-tbody");
    if (!classId) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--text-muted);">Please select a class to load students.</td></tr>`;
        return;
    }

    const res = await apiRequest("/api/students");
    if (!res || !res.ok) return;

    const students = await res.json();
    if (students.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--text-muted);">No enrolled students found.</td></tr>`;
        return;
    }

    tbody.innerHTML = students.map((s, idx) => `
        <tr>
            <td>${idx + 1}</td>
            <td><strong>${escapeHtml(s.usn)}</strong></td>
            <td>${escapeHtml(s.student_name)}</td>
            <td>
                <label style="margin-right:1rem;"><input type="radio" name="status_${s.student_id}" value="PRESENT" checked> PRESENT</label>
                <label><input type="radio" name="status_${s.student_id}" value="ABSENT"> ABSENT</label>
            </td>
        </tr>
    `).join("");

    document.getElementById("submit-attendance-btn").style.display = "inline-flex";
}

async function submitBatchAttendance() {
    const classId = document.getElementById("attendance-class-select").value;
    const dateVal = document.getElementById("attendance-date").value;

    if (!classId || !dateVal) {
        showToast("Select class and date", "warning");
        return;
    }

    const tbody = document.getElementById("attendance-students-tbody");
    const rows = tbody.querySelectorAll("tr");
    const records = [];

    rows.forEach(row => {
        const radio = row.querySelector("input[type='radio']:checked");
        if (radio) {
            const studentId = parseInt(radio.name.split("_")[1]);
            records.push({
                student_id: studentId,
                status: radio.value
            });
        }
    });

    if (records.length === 0) return;

    const res = await apiRequest("/api/attendance/batch", {
        method: "POST",
        body: JSON.stringify({
            class_id: parseInt(classId),
            date_recorded: dateVal,
            records: records
        })
    });

    if (res && res.ok) {
        showToast("Class attendance saved successfully!", "success");
    } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Error saving attendance", "danger");
    }
}

// 3. Marks Entry
async function loadTeacherMarksPage() {
    const resCls = await apiRequest("/api/classes");
    if (resCls && resCls.ok) {
        const classes = await resCls.json();
        const selectCls = document.getElementById("marks-class-select");
        selectCls.innerHTML = `<option value="">-- Select Class --</option>` +
            classes.map(c => `<option value="${c.class_id}">${escapeHtml(c.course_code)} - ${escapeHtml(c.course_name)}</option>`).join("");
    }

    const resStd = await apiRequest("/api/students");
    if (resStd && resStd.ok) {
        const students = await resStd.json();
        const selectStd = document.getElementById("marks-student-select");
        selectStd.innerHTML = `<option value="">-- Select Student --</option>` +
            students.map(s => `<option value="${s.student_id}">${escapeHtml(s.usn)} - ${escapeHtml(s.student_name)}</option>`).join("");
    }
}

async function saveStudentMarks(event) {
    event.preventDefault();
    const classId = document.getElementById("marks-class-select").value;
    const studentId = document.getElementById("marks-student-select").value;
    const assessmentName = document.getElementById("marks-assessment").value.trim();
    const semester = document.getElementById("marks-semester").value;
    const internalMarks = parseFloat(document.getElementById("marks-internal").value || 0);
    const assignmentMarks = parseFloat(document.getElementById("marks-assignment").value || 0);
    const examMarks = parseFloat(document.getElementById("marks-exam").value || 0);
    const remarks = document.getElementById("marks-remarks").value.trim();

    if (!classId || !studentId || !assessmentName) {
        showToast("Please fill all required fields.", "warning");
        return;
    }

    const res = await apiRequest("/api/marks", {
        method: "POST",
        body: JSON.stringify({
            class_id: parseInt(classId),
            student_id: parseInt(studentId),
            assessment_name: assessmentName,
            semester: semester,
            internal_marks: internalMarks,
            assignment_marks: assignmentMarks,
            exam_marks: examMarks,
            remarks
        })
    });

    if (!res) return;
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Error saving marks", "danger");
        return;
    }

    showToast("Student internal marks saved successfully!", "success");
    document.getElementById("marks-form").reset();
    loadTeacherMarksList();
}

async function loadTeacherMarksList() {
    const classId = document.getElementById("marks-class-select")?.value;
    let url = "/api/marks?";
    if (classId) url += `class_id=${classId}`;

    const res = await apiRequest(url);
    if (!res || !res.ok) return;

    const marks = await res.json();
    const tbody = document.getElementById("marks-list-tbody");
    if (!tbody) return;

    if (marks.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--text-muted);">No marks entered yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = marks.map(m => `
        <tr>
            <td><strong>${escapeHtml(m.usn || "N/A")}</strong> - ${escapeHtml(m.student_name || "")}</td>
            <td>${escapeHtml(m.assessment_name)}</td>
            <td>${m.internal_marks}</td>
            <td>${m.assignment_marks}</td>
            <td>${m.exam_marks}</td>
            <td><strong>${m.total_marks}</strong></td>
            <td><span class="badge badge-active">${escapeHtml(m.grade || "-")}</span></td>
        </tr>
    `).join("");
}

// 4. Study Materials
async function loadTeacherMaterialsPage() {
    const resCls = await apiRequest("/api/classes");
    if (resCls && resCls.ok) {
        const classes = await resCls.json();
        const selectCls = document.getElementById("mat-class-select");
        if (selectCls) {
            selectCls.innerHTML = `<option value="">-- Select Class --</option>` +
                classes.map(c => `<option value="${c.class_id}" data-course="${c.course_id}">${escapeHtml(c.course_code)} - ${escapeHtml(c.course_name)}</option>`).join("");
        }
    }
    loadTeacherMaterialsList();
}

async function saveStudyMaterial(event) {
    event.preventDefault();
    const classSelect = document.getElementById("mat-class-select");
    const classId = classSelect.value;
    const courseId = classSelect.options[classSelect.selectedIndex].getAttribute("data-course");
    const title = document.getElementById("mat-title").value.trim();
    const description = document.getElementById("mat-desc").value.trim();
    const semester = document.getElementById("mat-semester").value;
    const publishedStatus = document.getElementById("mat-status").value;
    const fileInput = document.getElementById("mat-file");

    if (!classId || !title || !fileInput.files[0]) {
        showToast("Please fill all required fields and select a file.", "warning");
        return;
    }

    const formData = new FormData();
    formData.append("title", title);
    formData.append("course_id", courseId);
    formData.append("class_id", classId);
    formData.append("description", description);
    formData.append("academic_year", "2025-2026");
    formData.append("semester", semester);
    formData.append("published_status", publishedStatus);
    formData.append("file", fileInput.files[0]);

    const res = await apiRequest("/api/materials", {
        method: "POST",
        body: formData
    });

    if (!res) return;
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Error uploading material", "danger");
        return;
    }

    showToast("Study material uploaded successfully!", "success");
    closeModal("material-modal");
    loadTeacherMaterialsList();
}

async function loadTeacherMaterialsList() {
    const res = await apiRequest("/api/materials");
    if (!res || !res.ok) return;

    const materials = await res.json();
    const tbody = document.getElementById("materials-tbody");
    if (!tbody) return;

    if (materials.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--text-muted);">No study materials uploaded yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = materials.map(m => `
        <tr>
            <td><strong>${escapeHtml(m.title)}</strong></td>
            <td>${escapeHtml(m.course_name || "N/A")}</td>
            <td><span class="badge badge-active">${escapeHtml(m.file_type)}</span></td>
            <td><span class="badge badge-${m.published_status.toLowerCase()}">${escapeHtml(m.published_status)}</span></td>
            <td>${escapeHtml(new Date(m.upload_date).toLocaleDateString())}</td>
            <td>
                <a href="${API_BASE_URL}${escapeHtml(m.file_path)}" target="_blank" class="btn btn-sm btn-secondary">Download</a>
                <button class="btn btn-sm btn-danger" onclick="deleteMaterial(${m.material_id})">Delete</button>
            </td>
        </tr>
    `).join("");
}

async function deleteMaterial(id) {
    if (!confirm("Are you sure you want to delete this study material?")) return;
    const res = await apiRequest(`/api/materials/${id}`, { method: "DELETE" });
    if (res && res.ok) {
        showToast("Material deleted", "success");
        loadTeacherMaterialsList();
    }
}

// 5. Teacher Announcements
async function loadTeacherAnnouncementsPage() {
    const resCls = await apiRequest("/api/classes");
    if (resCls && resCls.ok) {
        const classes = await resCls.json();
        const selectCls = document.getElementById("ann-class-select");
        if (selectCls) {
            selectCls.innerHTML = `<option value="">-- All Classes --</option>` +
                classes.map(c => `<option value="${c.class_id}">${escapeHtml(c.course_code)} - ${escapeHtml(c.course_name)}</option>`).join("");
        }
    }
    loadTeacherAnnouncementsList();
}

async function saveAnnouncement(event) {
    event.preventDefault();
    const title = document.getElementById("ann-title").value.trim();
    const content = document.getElementById("ann-content").value.trim();
    const targetType = document.getElementById("ann-target").value;
    const classId = document.getElementById("ann-class-select").value;

    const body = {
        title,
        content,
        target_type: targetType,
        class_id: classId ? parseInt(classId) : null
    };

    const res = await apiRequest("/api/announcements", {
        method: "POST",
        body: JSON.stringify(body)
    });

    if (!res) return;
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Error publishing announcement", "danger");
        return;
    }

    showToast("Announcement published successfully!", "success");
    closeModal("announcement-modal");
    loadTeacherAnnouncementsList();
}

async function loadTeacherAnnouncementsList() {
    const res = await apiRequest("/api/announcements");
    if (!res || !res.ok) return;

    const anns = await res.json();
    const tbody = document.getElementById("announcements-tbody");
    if (!tbody) return;

    if (anns.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--text-muted);">No announcements published yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = anns.map(a => `
        <tr>
            <td><strong>${escapeHtml(a.title)}</strong></td>
            <td>${escapeHtml(a.content.substring(0, 50))}...</td>
            <td><span class="badge badge-active">${escapeHtml(a.target_type)}</span></td>
            <td>${escapeHtml(new Date(a.created_at).toLocaleDateString())}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteAnnouncement(${a.announcement_id})">Delete</button>
            </td>
        </tr>
    `).join("");
}

async function deleteAnnouncement(id) {
    if (!confirm("Are you sure you want to delete this announcement?")) return;
    const res = await apiRequest(`/api/announcements/${id}`, { method: "DELETE" });
    if (res && res.ok) {
        showToast("Announcement deleted", "success");
        loadTeacherAnnouncementsList();
    }
}
