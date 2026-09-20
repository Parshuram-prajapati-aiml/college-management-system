// Centralized API Client & Utility Library

const API_BASE_URL = "http://127.0.0.1:8000";

async function apiRequest(url, options = {}) {
    const token = localStorage.getItem("access_token");

    const headers = {
        ...(options.headers || {})
    };

    // If body is not FormData and Content-Type isn't explicitly set, default to JSON
    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
    }

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}${url}`, {
            ...options,
            headers
        });

        if (response.status === 401) {
            localStorage.clear();
            showToast("Session expired. Please log in again.", "warning");
            setTimeout(() => {
                window.location.href = "/login.html";
            }, 1000);
            return null;
        }

        return response;
    } catch (err) {
        console.error("API Request Error:", err);
        showToast("Network error. Unable to connect to backend server.", "danger");
        return null;
    }
}

// Toast Notification System
function showToast(message, type = "info") {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span>${escapeHtml(message)}</span>
        <button style="background:none;border:none;cursor:pointer;color:inherit;font-weight:bold;margin-left:0.5rem;" onclick="this.parentElement.remove()">✕</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 4000);
}

// HTML Escaping Utility
function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Modal Helpers
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add("active");
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove("active");
    }
}
