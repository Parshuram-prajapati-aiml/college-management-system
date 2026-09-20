// Admin Portal Frontend JavaScript Logic

// 1. Dashboard Logic
async function loadAdminDashboard() {
    const res = await apiRequest("/api/admin/stats");
    if (!res || !res.ok) return;

    const data = await res.json();

    document.getElementById("stat-students").textContent = data.total_students;
    document.getElementById("stat-teachers").textContent = data.total_teachers;
    document.getElementById("stat-departments").textContent = data.total_departments;
    document.getElementById("stat-programs").textContent = data.total_programs;
    document.getElementById("stat-courses").textContent = data.total_courses;
    document.getElementById("stat-classes").textContent = data.total_classes;
    document.getElementById("stat-pending-admissions").textContent = data.pending_admissions;
    document.getElementById("stat-pending-docs").textContent = data.pending_documents;

    // Recent Applications List
    const appsTbody = document.getElementById("recent-apps-tbody");
    if (appsTbody) {
        if (data.recent_applications.length === 0) {
            appsTbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--text-muted);">No recent applications</td></tr>`;
        } else {
            appsTbody.innerHTML = data.recent_applications.map(app => `
                <tr>
                    <td><strong>${escapeHtml(app.application_number)}</strong></td>
                    <td>${escapeHtml(app.applicant_name)}</td>
                    <td>${escapeHtml(app.program)}</td>
                    <td><span class="badge badge-${app.status.toLowerCase()}">${escapeHtml(app.status)}</span></td>
                </tr>
            `).join("");
        }
    }

    // Recent Announcements List
    const annTbody = document.getElementById("recent-ann-tbody");
    if (annTbody) {
        if (data.recent_announcements.length === 0) {
            annTbody.innerHTML = `<tr><td colspan="3" style="text-align:center;color:var(--text-muted);">No recent announcements</td></tr>`;
        } else {
            annTbody.innerHTML = data.recent_announcements.map(ann => `
                <tr>
                    <td><strong>${escapeHtml(ann.title)}</strong></td>
                    <td><span class="badge badge-active">${escapeHtml(ann.target_audience)}</span></td>
                    <td>${escapeHtml(new Date(ann.created_at).toLocaleDateString())}</td>
                </tr>
            `).join("");
        }
    }
}

// 2. User Management
async function loadUsers() {
    const roleFilter = document.getElementById("role-filter")?.value || "";
    const searchQuery = document.getElementById("search-users")?.value || "";

    let url = `/api/admin/users?`;
    if (roleFilter) url += `role=${roleFilter}&`;
    if (searchQuery) url += `search=${encodeURIComponent(searchQuery)}&`;

    const res = await apiRequest(url);
    if (!res || !res.ok) return;

    const users = await res.json();
    const tbody = document.getElementById("users-tbody");

    if (users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--text-muted);">No users found.</td></tr>`;
        return;
    }

    tbody.innerHTML = users.map(u => `
        <tr>
            <td>#${u.user_id}</td>
            <td><strong>${escapeHtml(u.username)}</strong></td>
            <td>${escapeHtml(u.email)}</td>
            <td><span class="badge badge-active">${escapeHtml(u.role)}</span></td>
            <td><span class="badge badge-${u.status.toLowerCase()}">${escapeHtml(u.status)}</span></td>
            <td>
                <button class="btn btn-sm btn-secondary" onclick="openEditUserModal(${u.user_id}, '${escapeHtml(u.username)}', '${escapeHtml(u.email)}', '${u.role}', '${u.status}')">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteUser(${u.user_id})">Delete</button>
            </td>
        </tr>
    `).join("");
}

async function saveUser(event) {
    event.preventDefault();
    const userId = document.getElementById("user-id").value;
    const username = document.getElementById("user-username").value.trim();
    const email = document.getElementById("user-email").value.trim();
    const password = document.getElementById("user-password").value;
    const role = document.getElementById("user-role").value;
    const status = document.getElementById("user-status").value;

    const body = { username, email, role, status };
    if (password) body.password = password;

    const isEdit = !!userId;
    const url = isEdit ? `/api/admin/users/${userId}` : `/api/admin/users`;
    const method = isEdit ? "PUT" : "POST";

    const res = await apiRequest(url, { method, body: JSON.stringify(body) });
    if (!res) return;

    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Failed to save user", "danger");
        return;
    }

    showToast(`User ${isEdit ? "updated" : "created"} successfully!`, "success");
    closeModal("user-modal");
    loadUsers();
}

function openAddUserModal() {
    document.getElementById("user-id").value = "";
    document.getElementById("user-form").reset();
    document.getElementById("user-modal-title").textContent = "Add New User";
    openModal("user-modal");
}

function openEditUserModal(id, username, email, role, status) {
    document.getElementById("user-id").value = id;
    document.getElementById("user-username").value = username;
    document.getElementById("user-email").value = email;
    document.getElementById("user-password").value = "";
    document.getElementById("user-role").value = role;
    document.getElementById("user-status").value = status;
    document.getElementById("user-modal-title").textContent = "Edit User";
    openModal("user-modal");
}

async function deleteUser(id) {
    if (!confirm("Are you sure you want to delete this user?")) return;
    const res = await apiRequest(`/api/admin/users/${id}`, { method: "DELETE" });
    if (!res) return;
    if (res.ok) {
        showToast("User deleted successfully", "success");
        loadUsers();
    } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Delete failed", "danger");
    }
}

// 3. Students Management
async function loadStudents() {
    const search = document.getElementById("search-student")?.value || "";
    const deptId = document.getElementById("dept-filter")?.value || "";
    const statusFilter = document.getElementById("status-filter")?.value || "";

    let url = `/api/students?`;
    if (search) url += `search=${encodeURIComponent(search)}&`;
    if (deptId) url += `department_id=${deptId}&`;
    if (statusFilter) url += `status=${statusFilter}&`;

    const res = await apiRequest(url);
    if (!res || !res.ok) return;

    const students = await res.json();
    const tbody = document.getElementById("students-tbody");

    if (students.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;color:var(--text-muted);">No students found.</td></tr>`;
        return;
    }

    tbody.innerHTML = students.map(s => `
        <tr>
            <td><strong>${escapeHtml(s.usn)}</strong></td>
            <td>${escapeHtml(s.student_name)}</td>
            <td>${escapeHtml(s.email)}</td>
            <td>${escapeHtml(s.department_name || "N/A")}</td>
            <td>${escapeHtml(s.program_name || "N/A")}</td>
            <td>${escapeHtml(s.semester)}</td>
            <td><span class="badge badge-${s.status.toLowerCase()}">${escapeHtml(s.status)}</span></td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteStudent(${s.student_id})">Delete</button>
            </td>
        </tr>
    `).join("");
}

async function deleteStudent(id) {
    if (!confirm("Are you sure you want to delete this student profile?")) return;
    const res = await apiRequest(`/api/students/${id}`, { method: "DELETE" });
    if (!res) return;
    if (res.ok) {
        showToast("Student deleted successfully", "success");
        loadStudents();
    }
}

// 4. Teachers Management
async function loadTeachers() {
    const res = await apiRequest("/api/teachers");
    if (!res || !res.ok) return;

    const teachers = await res.json();
    const tbody = document.getElementById("teachers-tbody");

    if (teachers.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--text-muted);">No teachers found.</td></tr>`;
        return;
    }

    tbody.innerHTML = teachers.map(t => `
        <tr>
            <td>#${t.staff_id}</td>
            <td><strong>${escapeHtml(t.staff_name)}</strong></td>
            <td>${escapeHtml(t.email)}</td>
            <td>${escapeHtml(t.department_name || "N/A")}</td>
            <td>${escapeHtml(t.designation || "N/A")}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteTeacher(${t.staff_id})">Delete</button>
            </td>
        </tr>
    `).join("");
}

async function deleteTeacher(id) {
    if (!confirm("Are you sure you want to delete this teacher?")) return;
    const res = await apiRequest(`/api/teachers/${id}`, { method: "DELETE" });
    if (!res) return;
    if (res.ok) {
        showToast("Teacher deleted", "success");
        loadTeachers();
    }
}

// 5. Departments Management
async function loadDepartments() {
    const res = await apiRequest("/api/departments");
    if (!res || !res.ok) return;

    const depts = await res.json();
    const tbody = document.getElementById("departments-tbody");

    if (depts.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--text-muted);">No departments found.</td></tr>`;
        return;
    }

    tbody.innerHTML = depts.map(d => `
        <tr>
            <td><strong>${escapeHtml(d.department_code)}</strong></td>
            <td>${escapeHtml(d.department_name)}</td>
            <td>${escapeHtml(d.building || "Main")}</td>
            <td>${escapeHtml(d.hod_name || "Unassigned")}</td>
            <td>${d.programs_count}</td>
            <td>${d.students_count}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteDepartment(${d.department_id})">Delete</button>
            </td>
        </tr>
    `).join("");
}

async function saveDepartment(event) {
    event.preventDefault();
    const name = document.getElementById("dept-name").value.trim();
    const code = document.getElementById("dept-code").value.trim();
    const building = document.getElementById("dept-building").value.trim();
    const hod_name = document.getElementById("dept-hod").value.trim();

    const res = await apiRequest("/api/departments", {
        method: "POST",
        body: JSON.stringify({
            department_name: name,
            department_code: code,
            building,
            hod_name
        })
    });

    if (!res) return;
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Error creating department", "danger");
        return;
    }

    showToast("Department created!", "success");
    closeModal("department-modal");
    loadDepartments();
}

async function deleteDepartment(id) {
    if (!confirm("Are you sure you want to delete this department?")) return;
    const res = await apiRequest(`/api/departments/${id}`, { method: "DELETE" });
    if (res && res.ok) {
        showToast("Department deleted", "success");
        loadDepartments();
    }
}

// 6. Programs Management
async function loadPrograms() {
    const res = await apiRequest("/api/programs");
    if (!res || !res.ok) return;

    const progs = await res.json();
    const tbody = document.getElementById("programs-tbody");

    if (progs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--text-muted);">No programs found.</td></tr>`;
        return;
    }

    tbody.innerHTML = progs.map(p => `
        <tr>
            <td><strong>${escapeHtml(p.program_code)}</strong></td>
            <td>${escapeHtml(p.program_name)}</td>
            <td>${escapeHtml(p.department_name || "N/A")}</td>
            <td><span class="badge badge-active">${escapeHtml(p.degree_type)}</span></td>
            <td>${p.duration_years} Years</td>
            <td>${p.capacity}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteProgram(${p.program_id})">Delete</button>
            </td>
        </tr>
    `).join("");
}

async function saveProgram(event) {
    event.preventDefault();
    const deptId = document.getElementById("prog-dept").value;
    const name = document.getElementById("prog-name").value.trim();
    const code = document.getElementById("prog-code").value.trim();
    const degree = document.getElementById("prog-degree").value;
    const duration = document.getElementById("prog-duration").value;
    const capacity = document.getElementById("prog-capacity").value;

    const res = await apiRequest("/api/programs", {
        method: "POST",
        body: JSON.stringify({
            department_id: parseInt(deptId),
            program_name: name,
            program_code: code,
            degree_type: degree,
            duration_years: parseInt(duration),
            capacity: parseInt(capacity)
        })
    });

    if (!res) return;
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Error creating program", "danger");
        return;
    }

    showToast("Program created successfully!", "success");
    closeModal("program-modal");
    loadPrograms();
}

async function deleteProgram(id) {
    if (!confirm("Are you sure you want to delete this program?")) return;
    const res = await apiRequest(`/api/programs/${id}`, { method: "DELETE" });
    if (res && res.ok) {
        showToast("Program deleted", "success");
        loadPrograms();
    }
}

// 7. Courses Management
async function loadCourses() {
    const res = await apiRequest("/api/courses");
    if (!res || !res.ok) return;

    const courses = await res.json();
    const tbody = document.getElementById("courses-tbody");

    if (courses.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--text-muted);">No courses found.</td></tr>`;
        return;
    }

    tbody.innerHTML = courses.map(c => `
        <tr>
            <td><strong>${escapeHtml(c.course_code)}</strong></td>
            <td>${escapeHtml(c.course_name)}</td>
            <td>${c.credits} Credits</td>
            <td>${escapeHtml(c.department_name || "N/A")}</td>
            <td>${escapeHtml(c.semester)}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteCourse(${c.course_id})">Delete</button>
            </td>
        </tr>
    `).join("");
}

async function saveCourse(event) {
    event.preventDefault();
    const deptId = document.getElementById("course-dept").value;
    const code = document.getElementById("course-code").value.trim();
    const name = document.getElementById("course-name").value.trim();
    const credits = document.getElementById("course-credits").value;
    const semester = document.getElementById("course-semester").value;

    const res = await apiRequest("/api/courses", {
        method: "POST",
        body: JSON.stringify({
            department_id: parseInt(deptId),
            course_code: code,
            course_name: name,
            credits: parseInt(credits),
            semester: semester
        })
    });

    if (!res) return;
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Error creating course", "danger");
        return;
    }

    showToast("Course created successfully!", "success");
    closeModal("course-modal");
    loadCourses();
}

async function deleteCourse(id) {
    if (!confirm("Are you sure you want to delete this course?")) return;
    const res = await apiRequest(`/api/courses/${id}`, { method: "DELETE" });
    if (res && res.ok) {
        showToast("Course deleted", "success");
        loadCourses();
    }
}

// 8. Classes Management
async function loadClasses() {
    const res = await apiRequest("/api/classes");
    if (!res || !res.ok) return;

    const classesList = await res.json();
    const tbody = document.getElementById("classes-tbody");

    if (classesList.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--text-muted);">No class sections found.</td></tr>`;
        return;
    }

    tbody.innerHTML = classesList.map(c => `
        <tr>
            <td><strong>${escapeHtml(c.course_code)} - ${escapeHtml(c.course_name)}</strong></td>
            <td>${escapeHtml(c.program_name || "N/A")}</td>
            <td>${escapeHtml(c.teacher_name || "N/A")}</td>
            <td>${escapeHtml(c.semester)} (${escapeHtml(c.academic_year)})</td>
            <td>${escapeHtml(c.schedule || "TBD")}</td>
            <td>${escapeHtml(c.room || "TBD")}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteClass(${c.class_id})">Delete</button>
            </td>
        </tr>
    `).join("");
}

async function saveClass(event) {
    event.preventDefault();
    const courseId = document.getElementById("class-course").value;
    const progId = document.getElementById("class-prog").value;
    const staffId = document.getElementById("class-staff").value;
    const year = document.getElementById("class-year").value;
    const semester = document.getElementById("class-semester").value;
    const schedule = document.getElementById("class-schedule").value;
    const room = document.getElementById("class-room").value;
    const capacity = document.getElementById("class-capacity").value;

    const res = await apiRequest("/api/classes", {
        method: "POST",
        body: JSON.stringify({
            course_id: parseInt(courseId),
            program_id: parseInt(progId),
            staff_id: parseInt(staffId),
            academic_year: year,
            semester: semester,
            schedule,
            room,
            capacity: parseInt(capacity)
        })
    });

    if (!res) return;
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || "Error creating class section", "danger");
        return;
    }

    showToast("Class section created!", "success");
    closeModal("class-modal");
    loadClasses();
}

async function deleteClass(id) {
    if (!confirm("Are you sure you want to delete this class section?")) return;
    const res = await apiRequest(`/api/classes/${id}`, { method: "DELETE" });
    if (res && res.ok) {
        showToast("Class section deleted", "success");
        loadClasses();
    }
}

// 9. Admissions Workflow
async function loadAdmissions() {
    const res = await apiRequest("/api/admissions");
    if (!res || !res.ok) return;

    const admissions = await res.json();
    const tbody = document.getElementById("admissions-tbody");

    if (admissions.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--text-muted);">No admission applications found.</td></tr>`;
        return;
    }

    tbody.innerHTML = admissions.map(a => `
        <tr>
            <td><strong>${escapeHtml(a.application_number)}</strong></td>
            <td>${escapeHtml(a.student_name || a.usn || "Applicant")}</td>
            <td>${escapeHtml(a.program_name || "N/A")}</td>
            <td>${a.admission_year || "2025"}</td>
            <td><span class="badge badge-${a.status.toLowerCase()}">${escapeHtml(a.status)}</span></td>
            <td>
                <select class="form-control" style="width:auto;display:inline-block;padding:0.2rem 0.4rem;font-size:0.75rem;" onchange="updateAdmissionStatus(${a.admission_id}, this.value)">
                    <option value="PENDING" ${a.status === 'PENDING' ? 'selected' : ''}>PENDING</option>
                    <option value="UNDER_REVIEW" ${a.status === 'UNDER_REVIEW' ? 'selected' : ''}>UNDER REVIEW</option>
                    <option value="APPROVED" ${a.status === 'APPROVED' ? 'selected' : ''}>APPROVED</option>
                    <option value="REJECTED" ${a.status === 'REJECTED' ? 'selected' : ''}>REJECTED</option>
                    <option value="CANCELLED" ${a.status === 'CANCELLED' ? 'selected' : ''}>CANCELLED</option>
                </select>
            </td>
        </tr>
    `).join("");
}

async function updateAdmissionStatus(id, newStatus) {
    const res = await apiRequest(`/api/admissions/${id}`, {
        method: "PUT",
        body: JSON.stringify({ status: newStatus })
    });

    if (res && res.ok) {
        showToast(`Admission status updated to ${newStatus}`, "success");
        loadAdmissions();
    }
}

// 10. Document Verification
async function loadDocuments() {
    const res = await apiRequest("/api/documents");
    if (!res || !res.ok) return;

    const docs = await res.json();
    const tbody = document.getElementById("documents-tbody");

    if (docs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--text-muted);">No uploaded documents found.</td></tr>`;
        return;
    }

    tbody.innerHTML = docs.map(d => `
        <tr>
            <td>#${d.document_id}</td>
            <td><strong>${escapeHtml(d.student_name || "N/A")}</strong> (${escapeHtml(d.usn || "")})</td>
            <td>${escapeHtml(d.document_type)}</td>
            <td><a href="${API_BASE_URL}${escapeHtml(d.file_path)}" target="_blank" class="btn btn-sm btn-secondary">View File</a></td>
            <td><span class="badge badge-${d.status.toLowerCase()}">${escapeHtml(d.status)}</span></td>
            <td>${d.receipt ? `<strong>${escapeHtml(d.receipt.receipt_number)}</strong>` : "None"}</td>
            <td>
                ${d.status === 'PENDING' ? `
                    <button class="btn btn-sm btn-primary" onclick="verifyDocument(${d.document_id})">Verify</button>
                    <button class="btn btn-sm btn-danger" onclick="rejectDocument(${d.document_id})">Reject</button>
                ` : '-'}
            </td>
        </tr>
    `).join("");
}

async function verifyDocument(id) {
    const res = await apiRequest(`/api/documents/${id}/verify`, { method: "PUT" });
    if (res && res.ok) {
        showToast("Document verified and receipt generated!", "success");
        loadDocuments();
    }
}

async function rejectDocument(id) {
    const reason = prompt("Enter rejection reason:");
    if (!reason) return;

    const res = await apiRequest(`/api/documents/${id}/reject`, {
        method: "PUT",
        body: JSON.stringify({ rejection_reason: reason })
    });

    if (res && res.ok) {
        showToast("Document rejected.", "warning");
        loadDocuments();
    }
}
