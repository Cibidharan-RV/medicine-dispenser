const API_BASE = '/api/v1';

// --- State Management ---
let currentUser = null;
let currentToken = null;

// --- Utilities ---
function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        return null;
    }
}

async function apiFetch(endpoint, options = {}) {
    if (currentToken) {
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${currentToken}`
        };
    }
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    if (response.status === 401) {
        logout();
        throw new Error('Unauthorized');
    }
    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || 'API request failed');
    }
    return response.json();
}

// --- Authentication UI ---
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('login-error');
    
    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (!response.ok) throw new Error('Invalid credentials');
        
        const data = await response.json();
        handleLoginSuccess(data.access_token);
        errorDiv.classList.add('hidden');
    } catch (err) {
        errorDiv.textContent = err.message;
        errorDiv.classList.remove('hidden');
    }
});

document.getElementById('logout-btn').addEventListener('click', logout);

function handleLoginSuccess(token) {
    currentToken = token;
    localStorage.setItem('access_token', token);
    
    const payload = parseJwt(token);
    currentUser = { username: payload.sub, role: payload.role };
    
    document.getElementById('current-user').textContent = `Logged in as ${currentUser.username} (${currentUser.role})`;
    
    showDashboard();
}

function logout() {
    currentToken = null;
    currentUser = null;
    localStorage.removeItem('access_token');
    
    document.getElementById('login-section').classList.remove('hidden');
    document.getElementById('user-info').classList.add('hidden');
    
    document.querySelectorAll('.dashboard').forEach(d => d.classList.add('hidden'));
}

function showDashboard() {
    document.getElementById('login-section').classList.add('hidden');
    document.getElementById('user-info').classList.remove('hidden');
    
    document.getElementById('esp32-simulation').classList.remove('hidden');

    if (currentUser.role === 'DOCTOR') {
        document.getElementById('doctor-dashboard').classList.remove('hidden');
        doctorUI.loadPatients();
        doctorUI.loadMedicines();
    } else if (currentUser.role === 'PATIENT') {
        document.getElementById('patient-dashboard').classList.remove('hidden');
        patientUI.loadPrescriptions();
    } else if (currentUser.role === 'CAREGIVER') {
        document.getElementById('caregiver-dashboard').classList.remove('hidden');
        caregiverUI.loadPatients();
    }
}

// --- DOCTOR UI ---
const doctorUI = {
    async loadPatients() {
        try {
            const users = await apiFetch('/patients/');
            const tbody = document.querySelector('#patients-table tbody');
            tbody.innerHTML = '';
            users.forEach(u => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${u.userid || u.id || '-'}</td>
                    <td>${u.username || '-'}</td>
                    <td>${u.first_name || '-'} ${u.last_name || '-'}</td>
                    <td>${u.role || '-'}</td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            alert('Failed to load patients: ' + err.message);
        }
    },
    async loadMedicines() {
        try {
            const meds = await apiFetch('/medicines/');
            const tbody = document.querySelector('#medicines-table tbody');
            const select = document.getElementById('cpr-medicine-id');
            tbody.innerHTML = '';
            select.innerHTML = '<option value="" disabled selected>Select Medicine</option>';
            meds.forEach(m => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${m.medicine_id}</td>
                    <td>${m.medicine_name}</td>
                    <td>${m.strength}</td>
                    <td>${m.dosage_form}</td>
                `;
                tbody.appendChild(tr);
                
                const opt = document.createElement('option');
                opt.value = m.medicine_id;
                opt.textContent = `${m.medicine_name} (${m.strength})`;
                select.appendChild(opt);
            });
        } catch (err) {
            alert('Failed to load medicines: ' + err.message);
        }
    },
    showCreatePrescriptionModal() {
        document.getElementById('create-prescription-modal').classList.remove('hidden');
    }
};

document.getElementById('create-patient-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        username: document.getElementById('cp-username').value,
        password: document.getElementById('cp-password').value,
        role: "PATIENT",
        first_name: document.getElementById('cp-firstname').value,
        last_name: document.getElementById('cp-lastname').value
    };
    try {
        await apiFetch('/users/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        alert('Patient created successfully!');
        document.getElementById('create-patient-modal').classList.add('hidden');
        document.getElementById('create-patient-form').reset();
        doctorUI.loadPatients();
    } catch (err) {
        alert('Failed to create patient: ' + err.message);
    }
});

document.getElementById('create-medicine-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        medicine_name: document.getElementById('cm-name').value,
        strength: document.getElementById('cm-strength').value,
        dosage_form: document.getElementById('cm-form').value,
        manufacturer: document.getElementById('cm-manufacturer').value
    };
    try {
        await apiFetch('/medicines/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        alert('Medicine added successfully!');
        document.getElementById('create-medicine-modal').classList.add('hidden');
        document.getElementById('create-medicine-form').reset();
        doctorUI.loadMedicines();
    } catch (err) {
        alert('Failed to add medicine: ' + err.message);
    }
});

document.getElementById('create-prescription-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const durationDays = parseInt(document.getElementById('cpr-duration').value);
    const startDate = new Date();
    const endDate = new Date();
    endDate.setDate(startDate.getDate() + durationDays);

    const payload = {
        patient_id: parseInt(document.getElementById('cpr-patient-id').value),
        doctor_id: currentUser ? parseInt(currentUser.username) : 1, // Actually we need doctor id. We'll rely on backend fixing doctor_id.
        prescription_date: startDate.toISOString().split('T')[0],
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        items: [{
            medicine_id: parseInt(document.getElementById('cpr-medicine-id').value),
            dosage: document.getElementById('cpr-dosage').value,
            frequency: document.getElementById('cpr-frequency').value,
            duration: `${durationDays} days`
        }]
    };
    
    try {
        await apiFetch('/prescriptions/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        alert('Prescription assigned successfully!');
        document.getElementById('create-prescription-modal').classList.add('hidden');
        document.getElementById('create-prescription-form').reset();
    } catch (err) {
        alert('Failed to create prescription: ' + err.message);
    }
});

// --- PATIENT UI ---
const patientUI = {
    async loadPrescriptions() {
        try {
            const prescriptions = await apiFetch('/prescriptions/');
            const ul = document.getElementById('patient-prescriptions-list');
            ul.innerHTML = '';
            prescriptions.forEach(p => {
                const li = document.createElement('li');
                li.textContent = `Prescription #${p.prescription_id} (${p.start_date} to ${p.end_date})`;
                ul.appendChild(li);
            });
            this.loadSchedule();
            this.loadHistory();
        } catch (err) {
            console.error('Failed to load prescriptions', err);
        }
    },
    async loadSchedule() {
        try {
            const schedules = await apiFetch('/schedules/');
            const ul = document.getElementById('patient-schedule-list');
            ul.innerHTML = '';
            schedules.forEach(s => {
                const li = document.createElement('li');
                li.textContent = `Schedule #${s.schedule_id} at ${s.scheduled_time} (Qty: ${s.quantity_to_dispense})`;
                ul.appendChild(li);
            });
        } catch (err) {
            console.error('Failed to load schedule', err);
        }
    },
    async loadHistory() {
        try {
            const logs = await apiFetch('/dispensing/logs');
            const ul = document.getElementById('patient-dispense-history');
            ul.innerHTML = '';
            logs.forEach(l => {
                const li = document.createElement('li');
                li.textContent = `Dispense [${l.status}]: Qty ${l.quantity_dispensed} on ${new Date(l.dispensed_at).toLocaleString()}`;
                ul.appendChild(li);
            });
        } catch (err) {
            console.error('Failed to load dispense history', err);
        }
    }
};

// --- CAREGIVER UI ---
const caregiverUI = {
    async loadPatients() {
        try {
            const patients = await apiFetch('/patients/');
            const tbody = document.querySelector('#caregiver-patients-table tbody');
            tbody.innerHTML = '';
            patients.forEach(u => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${u.userid || u.id || '-'}</td>
                    <td>${u.username || '-'}</td>
                    <td>${u.first_name || '-'} ${u.last_name || '-'}</td>
                    <td>${u.role || '-'}</td>
                    <td><button onclick="caregiverUI.selectPatient(${u.userid || u.id}, '${u.first_name} ${u.last_name}')">View</button></td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            alert('Failed to load caregiver patients: ' + err.message);
        }
    },
    async selectPatient(patientId, patientName) {
        document.getElementById('caregiver-selected-patient-view').classList.remove('hidden');
        document.getElementById('caregiver-selected-patient-title').textContent = `Records for ${patientName}`;
        
        try {
            // Load Schedule for Patient
            // Ideally backend has an endpoint /caregiver/patients/{id}/schedules, for now we will fetch if backend supports
            const schedules = await apiFetch(`/schedules/?patient_id=${patientId}`);
            const ulSchedule = document.getElementById('caregiver-patient-schedule');
            ulSchedule.innerHTML = '';
            schedules.forEach(s => {
                const li = document.createElement('li');
                li.textContent = `Schedule #${s.schedule_id} at ${s.scheduled_time} (Qty: ${s.quantity_to_dispense})`;
                ulSchedule.appendChild(li);
            });
            
            // Load History for Patient
            const logs = await apiFetch(`/dispensing/logs?patient_id=${patientId}`);
            const ulHistory = document.getElementById('caregiver-patient-history');
            ulHistory.innerHTML = '';
            logs.forEach(l => {
                const li = document.createElement('li');
                li.textContent = `Dispense [${l.status}]: Qty ${l.quantity_dispensed} on ${new Date(l.dispensed_at).toLocaleString()}`;
                ulHistory.appendChild(li);
            });
        } catch (err) {
            alert('Failed to load patient records: ' + err.message);
        }
    }
};

// --- ESP32 SIMULATION UI ---
const simulationUI = {
    currentDue: null,
    
    async checkDueMedicine() {
        const out = document.getElementById('sim-output');
        const patientId = document.getElementById('sim-patient-id').value;
        out.textContent = 'Checking due medicine...';
        
        let url = '/dispensing/due';
        if (patientId) {
            url += `?patient_id=${patientId}`;
        }
        
        try {
            const due = await apiFetch(url);
            if (due && due.length > 0) {
                this.currentDue = due[0];
                out.textContent = `Medicine Due!\nSchedule ID: ${this.currentDue.schedule_id}\nQuantity: ${this.currentDue.quantity_to_dispense}\nMedicine: ${this.currentDue.medicine_name}`;
                document.getElementById('sim-dispense-btn').disabled = false;
            } else {
                this.currentDue = null;
                out.textContent = 'No medicine due at this time for this patient.';
                document.getElementById('sim-dispense-btn').disabled = true;
            }
        } catch (err) {
            out.textContent = `Error checking due medicine: ${err.message}`;
            document.getElementById('sim-dispense-btn').disabled = true;
        }
    },
    
    async dispenseMedicine() {
        if (!this.currentDue) return;
        const out = document.getElementById('sim-output');
        out.textContent = 'Dispensing in progress...';
        document.getElementById('sim-dispense-btn').disabled = true;
        
        try {
            const payload = {
                schedule_id: this.currentDue.schedule_id,
                quantity: this.currentDue.quantity_to_dispense
            };
            const result = await apiFetch('/dispensing/dispense', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            out.textContent = `Dispense Successful!\nStatus: ${result.status}\nQuantity Dispensed: ${result.quantity_dispensed}\nLow Stock Alert: ${result.low_stock_warning ? 'YES' : 'NO'}`;
            
            if (result.low_stock_warning) {
                out.style.color = '#ffcc00';
            } else {
                out.style.color = '#0f0';
            }
            
            this.currentDue = null;
        } catch (err) {
            out.style.color = '#f00';
            out.textContent = `Dispense Failed: ${err.message}`;
        }
    }
};

// --- Initialization ---
const savedToken = localStorage.getItem('access_token');
if (savedToken) {
    handleLoginSuccess(savedToken);
}
