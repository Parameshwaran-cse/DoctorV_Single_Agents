// Settings UI Logic
const settingsBtn = document.getElementById('settings-btn');
const settingsModal = document.getElementById('settings-modal');
const closeSettings = document.getElementById('close-settings');
const agentProviderSelect = document.getElementById('agent_provider');

// Load saved agent from localStorage, default to gemini
const savedAgent = localStorage.getItem('agent_provider') || 'gemini';
if (agentProviderSelect) {
    agentProviderSelect.value = savedAgent;

    settingsBtn.addEventListener('click', () => {
        settingsModal.classList.add('show');
    });

    closeSettings.addEventListener('click', () => {
        settingsModal.classList.remove('show');
    });

    window.addEventListener('click', (e) => {
        if (e.target === settingsModal) {
            settingsModal.classList.remove('show');
        }
    });

    agentProviderSelect.addEventListener('change', (e) => {
        localStorage.setItem('agent_provider', e.target.value);
    });
}

document.getElementById('followup-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const btn = document.getElementById('generate-btn');
    const loader = document.getElementById('btn-loader');
    const btnText = btn.querySelector('span');
    const resultContent = document.getElementById('result-content');
    
    // UI State: Loading
    btn.disabled = true;
    btnText.textContent = 'Generating...';
    loader.style.display = 'block';
    resultContent.innerHTML = '<p class="placeholder-text">Analyzing patient data...</p>';
    
    // Gather data
    const parseList = (str) => str ? str.split(',').map(s => s.trim()).filter(Boolean) : [];
    
    const requestData = {
        patient_name: document.getElementById('patient_name').value,
        patient_age: parseInt(document.getElementById('patient_age').value) || null,
        patient_gender: document.getElementById('patient_gender').value || null,
        diagnosis: document.getElementById('diagnosis').value,
        treatment_given: document.getElementById('treatment_given').value || null,
        medications: parseList(document.getElementById('medications').value),
        allergies: parseList(document.getElementById('allergies').value),
        follow_up_duration_weeks: parseInt(document.getElementById('follow_up_duration_weeks').value) || 4,
        special_instructions: document.getElementById('special_instructions').value || null,
        language: "english",
        agent_provider: localStorage.getItem('agent_provider') || 'gemini'
    };

    try {
        const response = await fetch('http://127.0.0.1:8003/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (!response.ok || !data.success) {
            throw new Error(data.error || data.detail || 'An unknown error occurred');
        }
        
        const plan = data.data;
        let html = '<div class="care-plan-rendered">';
        
        // Header
        html += `<div class="plan-header">
            <h3>Care Plan for ${plan.patient_name || 'Patient'}</h3>
            <span class="diagnosis-badge">${plan.diagnosis || ''}</span>
        </div>`;
        html += `<p class="plan-summary">${plan.care_plan_summary || ''}</p>`;
        
        // Medications
        if (plan.medication_reminders && plan.medication_reminders.length > 0) {
            html += `<div class="section"><h4>💊 Medications</h4><div class="cards-grid">`;
            plan.medication_reminders.forEach(med => {
                html += `<div class="card">
                    <h5>${med.medication} <span class="dose">${med.dose}</span></h5>
                    <p><strong>Freq:</strong> ${med.frequency} | <strong>Timing:</strong> ${med.timing}</p>
                    <p class="notes">${med.important_notes}</p>
                    <div class="reminders">🔔 ${(med.reminder_times || []).join(', ')}</div>
                </div>`;
            });
            html += `</div></div>`;
        }
        
        // Follow-ups
        if (plan.follow_up_schedule && plan.follow_up_schedule.length > 0) {
             html += `<div class="section"><h4>📅 Follow-up Appointments</h4><ul class="schedule-list">`;
             plan.follow_up_schedule.forEach(f => {
                 html += `<li><strong>Week ${f.week}:</strong> ${f.appointment_type} - ${f.purpose} <br><small>(Bring: ${(f.what_to_bring||[]).join(', ')})</small></li>`;
             });
             html += `</ul></div>`;
        }

        // Labs
        if (plan.lab_reminders && plan.lab_reminders.length > 0) {
             html += `<div class="section"><h4>🧪 Labs & Tests</h4><ul class="labs-list">`;
             plan.lab_reminders.forEach(l => {
                 html += `<li><strong>${l.test}</strong> (${l.when}): ${l.why} ${l.fasting_required ? '<span class="badge fasting">Fasting Req</span>' : ''}</li>`;
             });
             html += `</ul></div>`;
        }
        
        // Lifestyle
        if (plan.lifestyle_advice && plan.lifestyle_advice.length > 0) {
             html += `<div class="section"><h4>🌱 Lifestyle Advice</h4><ul class="lifestyle-list">`;
             plan.lifestyle_advice.forEach(l => {
                 html += `<li><strong>${l.category.toUpperCase()}</strong>: ${l.advice}</li>`;
             });
             html += `</ul></div>`;
        }
        
        // Diet
        if (plan.diet_plan) {
            html += `<div class="section"><h4>🥗 Diet Plan</h4><div class="diet-plan">
                <p><strong>To Eat:</strong> ${(plan.diet_plan.foods_to_eat||[]).join(', ')}</p>
                <p><strong>To Avoid:</strong> ${(plan.diet_plan.foods_to_avoid||[]).join(', ')}</p>
            </div></div>`;
        }
        
        // Warnings
        if (plan.warning_signs && plan.warning_signs.length > 0) {
            html += `<div class="section"><h4>🚨 Warning Signs</h4><ul class="warning-list">`;
            plan.warning_signs.forEach(w => {
                 html += `<li><strong>${w.symptom}</strong> &rarr; <span class="urgency-${w.urgency?.toLowerCase()}">${w.action}</span></li>`;
            });
            html += `</ul></div>`;
        }
        
        // Explanation
        if (plan.patient_explanation) {
             html += `<div class="patient-explanation section">
                <h4>Doctor's Note</h4>
                <p>${plan.patient_explanation}</p>
             </div>`;
        }
        
        html += `</div>`;
        
        resultContent.innerHTML = html + `
            <div class="execution-time">Execution Time: ${data.execution_time_seconds}s</div>
        `;
        
    } catch (error) {
        resultContent.innerHTML = `<div class="error-text"><strong>Error:</strong> ${error.message}</div>`;
    } finally {
        // UI State: Reset
        btn.disabled = false;
        btnText.textContent = 'Generate Care Plan';
        loader.style.display = 'none';
    }
});
