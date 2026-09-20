// Authentication & Navigation Guard Logic

async function handleLogin(event) {
    event.preventDefault();

    const usernameInput = document.getElementById("username").value.trim();
    const passwordInput = document.getElementById("password").value;
    const errorAlert = document.getElementById("login-error");

    if (errorAlert) errorAlert.style.display = "none";

    if (!usernameInput || !passwordInput) {
        if (errorAlert) {
            errorAlert.textContent = "Please enter both username/email and password.";
            errorAlert.style.display = "block";
        }
        return;
    }

    const response = await apiRequest("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({
            username: usernameInput,
            password: passwordInput
        })
    });

    if (!response) return;

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        if (errorAlert) {
            errorAlert.textContent = errorData.detail || "Login failed. Check your credentials.";
            errorAlert.style.display = "block";
        }
        return;
    }

    const data = await response.json();

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user_id", data.user_id);
    localStorage.setItem("username", data.username);
    localStorage.setItem("role", data.role);

    showToast("Login successful! Redirecting...", "success");

    setTimeout(() => {
        redirectToRoleDashboard(data.role);
    }, 500);
}

function redirectToRoleDashboard(role) {
    switch (role) {
        case "ADMIN":
            window.location.href = "/admin/dashboard.html";
            break;
        case "TEACHER":
            window.location.href = "/teacher/dashboard.html";
            break;
        case "STUDENT":
            window.location.href = "/student/dashboard.html";
            break;
        case "ADMISSION_OFFICER":
            window.location.href = "/admin/admissions.html";
            break;
        default:
            window.location.href = "/login.html";
    }
}

function checkAuth(allowedRoles = []) {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("role");

    if (!token || !role) {
        localStorage.clear();
        window.location.href = "/login.html";
        return false;
    }

    if (allowedRoles.length > 0 && !allowedRoles.includes(role)) {
        showToast("Unauthorized access attempt. Redirecting...", "danger");
        redirectToRoleDashboard(role);
        return false;
    }

    initPageUser();
    return true;
}

function initPageUser() {
    const username = localStorage.getItem("username") || "User";
    const role = localStorage.getItem("role") || "";

    const usernameElems = document.querySelectorAll(".current-user-name");
    usernameElems.forEach(el => el.textContent = username);

    const roleElems = document.querySelectorAll(".current-user-role");
    roleElems.forEach(el => el.textContent = role);
}

function logout() {
    localStorage.clear();
    showToast("Logged out successfully.", "info");
    setTimeout(() => {
        window.location.href = "/login.html";
    }, 500);
}
