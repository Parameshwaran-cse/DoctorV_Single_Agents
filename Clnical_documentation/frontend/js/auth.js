// auth.js
document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const signupForm = document.getElementById("signupForm");
    const authError = document.getElementById("authError");
    const API_BASE = "http://127.0.0.1:9000";

    async function handleAuth(url, email, password) {
        try {
            let options = {};
            if (url.includes("login")) {
                const formData = new URLSearchParams();
                formData.append("username", email);
                formData.append("password", password);
                options = {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: formData
                };
            } else {
                options = {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password })
                };
            }

            const response = await fetch(API_BASE + url, options);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Authentication failed");
            }

            localStorage.setItem("token", data.access_token);
            window.location.href = "app.html";
        } catch (error) {
            authError.textContent = error.message;
        }
    }

    if (loginForm) {
        loginForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            handleAuth("/auth/login", email, password);
        });
    }

    if (signupForm) {
        signupForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            handleAuth("/auth/signup", email, password);
        });
    }
});
