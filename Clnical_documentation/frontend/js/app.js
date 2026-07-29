// app.js
const API_BASE = "http://127.0.0.1:9000";




// ─── Provider colour map ──────────────────────────────────────────────────────
const PROVIDER_COLORS = {
    gemini: "#4285F4",
    openai: "#10a37f",
    groq:   "#f55036",
};

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "login.html";
        return;
    }

    // ─── Auth header helper ──────────────────────────────────────────────────
    function authHeader() {
        return { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" };
    }

    // ─── Logout ──────────────────────────────────────────────────────────────
    document.getElementById("logoutBtn").addEventListener("click", () => {
        localStorage.removeItem("token");
        window.location.href = "login.html";
    });

    // ─── Template Selection ──────────────────────────────────────────────────
    const templateButtons   = document.querySelectorAll(".template-btn");
    const documentTypeInput = document.getElementById("document_type");

    templateButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            templateButtons.forEach(b => b.classList.remove("selected"));
            btn.classList.add("selected");
            documentTypeInput.value = btn.dataset.value;
        });
    });

    // ─── Form Submission ─────────────────────────────────────────────────────
    const docForm        = document.getElementById("docForm");
    const generateBtn    = document.getElementById("generateBtn");
    const emptyState     = document.getElementById("emptyState");
    const loader         = document.getElementById("loader");
    const outputContainer = document.getElementById("outputContainer");
    const outputMeta     = document.getElementById("outputMeta");

    docForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const requestBody = {
            document_type:  documentTypeInput.value,
            patient_name:   document.getElementById("patient_name").value,
            patient_age:    parseInt(document.getElementById("patient_age").value) || null,
            doctor_name:    document.getElementById("doctor_name").value   || null,
            department:     document.getElementById("department").value    || null,
            chief_complaint:document.getElementById("chief_complaint").value || null,
            diagnosis:      document.getElementById("diagnosis").value     || null,
            treatment_plan: document.getElementById("treatment_plan").value || null,
        };

        // UI → loading
        emptyState.style.display       = "none";
        outputContainer.style.display  = "none";
        outputContainer.style.color    = "";
        outputMeta.style.display       = "none";
        loader.style.display           = "block";
        generateBtn.disabled           = true;
        generateBtn.textContent        = "Generating...";

        const controller = new AbortController();
        const timeoutId  = setTimeout(() => controller.abort(), 60000);

        try {
            const response = await fetch(API_BASE + "/generate", {
                method:  "POST",
                signal:  controller.signal,
                headers: authHeader(),
                body:    JSON.stringify(requestBody),
            });

            if (response.status === 401) {
                localStorage.removeItem("token");
                window.location.href = "login.html";
                return;
            }

            const data = await response.json();
            if (!response.ok) throw new Error(data.detail?.message || "An error occurred");

            // Update provider badge in case fallback was used
            const providerUsed = data.data?._provider_used || "unknown";
            if (data.data?._provider_used) updateProviderBadge(providerUsed);

            // Render as rich text
            const display = { ...data.data };
            delete display._provider_used;
            outputContainer.innerHTML = renderDocument(display);

            outputMeta.innerHTML = `
                <span>⏱ ${data.execution_time_seconds}s</span>
                <span>Provider: <strong style="color:${PROVIDER_COLORS[providerUsed] || '#fff'}">${providerUsed.toUpperCase()}</strong></span>
                <span>✅ Success</span>`;

            outputContainer.style.display = "block";
            outputMeta.style.display      = "flex";

        } catch (error) {
            clearTimeout(timeoutId);
            const errMsg = error.name === "AbortError"
                ? "Request timed out after 60 seconds."
                : error.message;
            outputContainer.textContent   = `Error: ${errMsg}`;
            outputContainer.style.display = "block";
            outputContainer.style.color   = "var(--error-red)";
        } finally {
            loader.style.display    = "none";
            generateBtn.disabled    = false;
            generateBtn.textContent = "Generate";
        }
    });

    // ─── Active Provider Badge ────────────────────────────────────────────────
    function updateProviderBadge(providerId) {
        const badge = document.getElementById("activeProviderBadge");
        const dot   = badge.querySelector(".provider-dot");
        const label = badge.querySelector(".provider-label");
        const color = PROVIDER_COLORS[providerId] || "#aaa";
        dot.style.backgroundColor = color;
        label.textContent = providerId.charAt(0).toUpperCase() + providerId.slice(1);
    }

    // ─── Settings Modal ───────────────────────────────────────────────────────
    const settingsModal = document.getElementById("settingsModal");
    const settingsBtn   = document.getElementById("settingsBtn");
    const closeSettings = document.getElementById("closeSettings");
    const providerList  = document.getElementById("providerList");
    const saveMsg       = document.getElementById("providerSaveMsg");

    let currentProvider = null;

    settingsBtn.addEventListener("click", () => {
        settingsModal.style.display = "flex";
        loadProviders();
    });

    closeSettings.addEventListener("click", () => {
        settingsModal.style.display = "none";
    });

    settingsModal.addEventListener("click", (e) => {
        if (e.target === settingsModal) settingsModal.style.display = "none";
    });

    async function loadProviders() {
        providerList.innerHTML = `
            <div class="provider-skeleton"></div>
            <div class="provider-skeleton"></div>
            <div class="provider-skeleton"></div>`;
        saveMsg.style.display = "none";

        try {
            const res  = await fetch(API_BASE + "/settings/providers", { headers: authHeader() });
            const data = await res.json();

            currentProvider = data.active_provider;
            updateProviderBadge(currentProvider);

            providerList.innerHTML = "";
            data.providers.forEach(p => {
                const card = document.createElement("div");
                card.className = "provider-card" + (p.id === currentProvider ? " active" : "");
                card.dataset.id = p.id;
                card.innerHTML = `
                    <div class="provider-card-header">
                        <div class="provider-card-dot" style="background:${p.color}"></div>
                        <div>
                            <div class="provider-card-name">${p.name}</div>
                            <div class="provider-card-model">${p.model}</div>
                        </div>
                        ${p.id === currentProvider
                            ? '<span class="provider-active-tag">Active</span>'
                            : `<button class="provider-select-btn" data-id="${p.id}">Set Active</button>`}
                    </div>`;
                providerList.appendChild(card);
            });

            // Attach select handlers
            providerList.querySelectorAll(".provider-select-btn").forEach(btn => {
                btn.addEventListener("click", () => switchProvider(btn.dataset.id));
            });

        } catch (err) {
            providerList.innerHTML = `<p style="color:var(--error-red)">Failed to load providers: ${err.message}</p>`;
        }
    }

    async function switchProvider(providerId) {
        saveMsg.style.display = "none";
        try {
            const res = await fetch(API_BASE + "/settings/provider", {
                method:  "POST",
                headers: authHeader(),
                body:    JSON.stringify({ provider: providerId }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Failed");

            currentProvider = data.active_provider;
            updateProviderBadge(currentProvider);

            saveMsg.textContent   = `✅ Switched to ${providerId.charAt(0).toUpperCase() + providerId.slice(1)} successfully.`;
            saveMsg.style.color   = "#10a37f";
            saveMsg.style.display = "block";

            // Re-render the cards
            loadProviders();

        } catch (err) {
            saveMsg.textContent   = `❌ Error: ${err.message}`;
            saveMsg.style.color   = "var(--error-red)";
            saveMsg.style.display = "block";
        }
    }

    // ─── Init: load active provider badge on page load ────────────────────────
    (async () => {
        try {
            const res  = await fetch(API_BASE + "/settings/providers", { headers: authHeader() });
            const data = await res.json();
            updateProviderBadge(data.active_provider);
        } catch (_) { /* silently fail */ }
    })();
});

// ═══════════════════════════════════════════════════════════════════════════
// 📄 Rich Document Renderer — converts structured JSON → formatted HTML
// ═══════════════════════════════════════════════════════════════════════════

function esc(str) {
    if (str == null) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function humanLabel(key) {
    return key
        .replace(/_/g, " ")
        .replace(/\b\w/g, c => c.toUpperCase());
}

function renderValue(value, depth = 0) {
    if (value == null || value === "") return `<span class="doc-empty">—</span>`;

    if (Array.isArray(value)) {
        if (value.length === 0) return `<span class="doc-empty">None</span>`;
        return `<ul class="doc-list">${value.map(v =>
            `<li>${typeof v === "object" ? renderObject(v, depth + 1) : esc(v)}</li>`
        ).join("")}</ul>`;
    }

    if (typeof value === "object") {
        return renderObject(value, depth);
    }

    // Plain string — detect placeholder
    const str = String(value);
    if (str.startsWith("[TO BE COMPLETED") || str.includes("[Physician")) {
        return `<span class="doc-placeholder">${esc(str)}</span>`;
    }
    return `<p class="doc-text">${esc(str)}</p>`;
}

function renderObject(obj, depth = 0) {
    return Object.entries(obj)
        .filter(([k]) => !["document_status", "confidence", "_provider_used"].includes(k))
        .map(([key, val]) => {
            if (typeof val === "object" && !Array.isArray(val) && val !== null) {
                return `
                    <div class="doc-subsection depth-${depth}">
                        <div class="doc-subsection-title">${humanLabel(key)}</div>
                        ${renderObject(val, depth + 1)}
                    </div>`;
            }
            return `
                <div class="doc-field">
                    <span class="doc-field-label">${humanLabel(key)}</span>
                    <div class="doc-field-value">${renderValue(val, depth)}</div>
                </div>`;
        }).join("");
}

// Section colour mapping
const SECTION_COLORS = {
    subjective:   { bg: "rgba(59,130,246,0.08)",  border: "#3b82f6", letter: "S" },
    objective:    { bg: "rgba(139,92,246,0.08)",  border: "#8b5cf6", letter: "O" },
    assessment:   { bg: "rgba(245,158,11,0.08)",  border: "#f59e0b", letter: "A" },
    plan:         { bg: "rgba(16,185,129,0.08)",  border: "#10b981", letter: "P" },
};

function renderSection(key, val) {
    const meta = SECTION_COLORS[key];
    const label = humanLabel(key);

    if (meta) {
        return `
        <div class="doc-section" style="border-left-color:${meta.border}; background:${meta.bg}">
            <div class="doc-section-header">
                <div class="doc-section-badge" style="background:${meta.border}">${meta.letter}</div>
                <h3 class="doc-section-title">${label}</h3>
            </div>
            <div class="doc-section-body">${renderObject(val, 1)}</div>
        </div>`;
    }

    // Generic section
    return `
        <div class="doc-section">
            <div class="doc-section-header">
                <h3 class="doc-section-title">${label}</h3>
            </div>
            <div class="doc-section-body">${renderValue(val, 1)}</div>
        </div>`;
}

function renderDocument(data) {
    const skip = new Set(["document_type", "title", "sections", "physician_signature_block",
                          "document_status", "confidence", "_provider_used"]);

    let html = "";

    // ── Header ────────────────────────────────────────────────────────────
    const docType = data.document_type || "Clinical Document";
    const title   = data.title || docType;
    const status  = data.document_status || "draft";

    html += `
    <div class="doc-root">
        <div class="doc-header">
            <div>
                <div class="doc-type-tag">${esc(docType)}</div>
                <h2 class="doc-title">${esc(title)}</h2>
            </div>
            <span class="doc-status-badge ${status === "draft" ? "draft" : "final"}">${status.toUpperCase()}</span>
        </div>
        <hr class="doc-divider">`;

    // ── Sections (SOAP etc.) ───────────────────────────────────────────────
    if (data.sections && typeof data.sections === "object") {
        html += `<div class="doc-sections">`;
        for (const [key, val] of Object.entries(data.sections)) {
            html += renderSection(key, val);
        }
        html += `</div>`;
    }

    // ── Top-level fields (referral letters, insurance, visit summary etc.) ──
    const topFields = Object.entries(data).filter(([k]) => !skip.has(k));
    if (topFields.length) {
        html += `<div class="doc-sections">`;
        for (const [key, val] of topFields) {
            if (typeof val === "object" && !Array.isArray(val)) {
                html += renderSection(key, val);
            } else {
                html += `
                <div class="doc-field top-level">
                    <span class="doc-field-label">${humanLabel(key)}</span>
                    <div class="doc-field-value">${renderValue(val)}</div>
                </div>`;
            }
        }
        html += `</div>`;
    }

    // ── Signature block ───────────────────────────────────────────────────
    if (data.physician_signature_block) {
        html += `
        <div class="doc-signature">
            <span class="doc-sig-label">Physician Signature</span>
            <span class="doc-sig-value">${esc(data.physician_signature_block)}</span>
        </div>`;
    }

    html += `</div>`; // .doc-root
    return html;
}
