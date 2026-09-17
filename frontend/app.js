const API_BASE = '/api/v1';

// --- State Management ---
let currentUser = null;
let currentToken = null;
let medicineMap = {};
let prescriptionItemMap = {};
let scheduleMap = {};
let pendingPrescriptionItems = [];

// --- Theme Management ---
const themeToggleBtn = document.getElementById('theme-toggle');
const rootHtml = document.documentElement;

const savedTheme = localStorage.getItem('theme') || 'light';
rootHtml.setAttribute('data-theme', savedTheme);
updateThemeToggleText(savedTheme);

themeToggleBtn.addEventListener('click', () => {
    const currentTheme = rootHtml.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    rootHtml.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeToggleText(newTheme);
});

function updateThemeToggleText(theme) {
    if(theme === 'dark') {
        themeToggleBtn.textContent = '☀️ Light Mode';
    } else {
        themeToggleBtn.textContent = '🌙 Dark Mode';
    }
}

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
    currentUser = { username: payload.sub, role: payload.role, userid: payload.userid };
    
    document.getElementById('current-user').textContent = `Logged in as ${currentUser.username} (${currentUser.role})`;
    
    initializeDashboardData();
}

async function initializeDashboardData() {
    try {
        const meds = await apiFetch('/medicines/');
        meds.forEach(m => {
            medicineMap[m.medicine_id] = m;
        });
    } catch(e) {
        console.warn("Could not load medicines", e);
    }
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
    filterPatients() {
        const term = document.getElementById('search-patients').value.toLowerCase();
        const rows = document.querySelectorAll('#patients-table tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(term) ? '' : 'none';
        });
    },
    filterMedicines() {
        const term = document.getElementById('search-medicines').value.toLowerCase();
        const rows = document.querySelectorAll('#medicines-table tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(term) ? '' : 'none';
        });
    },
    filterSelect(inputId, selectId) {
        const term = document.getElementById(inputId).value.toLowerCase();
        const select = document.getElementById(selectId);
        Array.from(select.options).forEach(opt => {
            if (opt.value === "") return;
            const text = opt.textContent.toLowerCase();
            opt.style.display = text.includes(term) ? '' : 'none';
        });
    },
    async loadPatients() {
        try {
            const users = await apiFetch('/patients/');
            const tbody = document.querySelector('#patients-table tbody');
            const select = document.getElementById('cpr-patient-id');
            tbody.innerHTML = '';
            if (select) select.innerHTML = '<option value="" disabled selected>Select Patient</option>';
            
            users.forEach(u => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${u.userid || u.id || '-'}</td>
                    <td>${u.username || '-'}</td>
                    <td>${u.first_name || '-'} ${u.last_name || '-'}</td>
                `;
                tr.style.cursor = 'pointer';
                tr.onclick = () => this.viewPatient(u.userid || u.id, `${u.first_name || u.username} ${u.last_name || ''}`);
                tbody.appendChild(tr);
                
                if (select) {
                    const opt = document.createElement('option');
                    opt.value = u.userid || u.id;
                    opt.textContent = `${u.first_name || u.username} ${u.last_name || ''} (ID: ${u.userid || u.id})`;
                    select.appendChild(opt);
                }
            });
        } catch (err) {
            alert('Failed to load patients: ' + err.message);
        }
    },
    async loadMedicines() {
        try {
            const [meds, inventory] = await Promise.all([
                apiFetch('/medicines/'),
                apiFetch('/inventory/')
            ]);
            
            // Aggregate inventory by medicine_id
            const inventoryByMed = {};
            inventory.forEach(inv => {
                if (!inventoryByMed[inv.medicine_id]) {
                    inventoryByMed[inv.medicine_id] = { total: 0, minStock: inv.minimum_stock_level, expiries: new Set() };
                }
                inventoryByMed[inv.medicine_id].total += inv.quantity_available;
                if (inv.quantity_available > 0) {
                    if (inv.expiry_date) {
                        const date = new Date(inv.expiry_date);
                        const month = String(date.getMonth() + 1).padStart(2, '0');
                        const year = date.getFullYear();
                        inventoryByMed[inv.medicine_id].expiries.add(`${month}/${year}`);
                    }
                }
            });

            const tbody = document.querySelector('#medicines-table tbody');
            const select = document.getElementById('cpr-medicine-id');
            tbody.innerHTML = '';
            if (select) select.innerHTML = '<option value="" disabled selected>Select Medicine</option>';
            meds.forEach(m => {
                const invData = inventoryByMed[m.medicine_id] || { total: 0, minStock: 0 };
                let stockStatus = '';
                if (invData.total === 0) stockStatus = '<span class="badge badge-danger">Out of Stock</span>';
                else if (invData.total <= invData.minStock) stockStatus = '<span class="badge badge-warning">Low Stock</span>';
                else stockStatus = '<span class="badge badge-success">In Stock</span>';

                const expiryStr = invData.expiries && invData.expiries.size > 0 ? Array.from(invData.expiries).join(', ') : '-';
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${m.medicine_id}</td>
                    <td style="font-weight: 500;">${m.medicine_name}</td>
                    <td>${m.strength || '-'}</td>
                    <td>${m.dosage_form || '-'}</td>
                    <td>${expiryStr}</td>
                    <td>${invData.total}</td>
                    <td>${stockStatus}</td>
                    <td>
                        <button class="button-secondary" style="font-size: 0.8rem; padding: 0.25rem 0.5rem;" onclick="doctorUI.showTopupModal(${m.medicine_id}, '${m.medicine_name}', ${invData.minStock})">Top Up</button>
                    </td>
                `;
                tbody.appendChild(tr);
                
                if (select) {
                    const opt = document.createElement('option');
                    opt.value = m.medicine_id;
                    opt.textContent = `${m.medicine_name} (${m.strength}) - Stock: ${invData.total}`;
                    select.appendChild(opt);
                }
            });
        } catch (err) {
            console.error('Failed to load medicines: ', err);
        }
    },
    showCreatePrescriptionModal() {
        document.getElementById('create-prescription-modal').classList.remove('hidden');
        pendingPrescriptionItems = [];
        this.renderPendingItems();
    },
    showTopupModal(medicineId, medicineName, currentMinStock) {
        document.getElementById('tm-medicine-id').value = medicineId;
        document.getElementById('tm-name').value = medicineName;
        document.getElementById('tm-expiry-month').value = '';
        document.getElementById('tm-expiry-year').value = '';
        document.getElementById('tm-quantity').value = '';
        document.getElementById('tm-min-stock').value = currentMinStock;
        document.getElementById('topup-medicine-modal').classList.remove('hidden');
    },
    renderPendingItems() {
        const container = document.getElementById('cpr-items-container');
        if (pendingPrescriptionItems.length === 0) {
            container.innerHTML = '<p style="color: var(--text-secondary); text-align: center; font-size: 0.9rem;">No medicines added yet.</p>';
            return;
        }
        let html = '';
        pendingPrescriptionItems.forEach((item, index) => {
            const med = medicineMap[item.medicine_id];
            const medName = med ? `${med.medicine_name} (${med.strength})` : `Medicine ID: ${item.medicine_id}`;
            html += `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; border-bottom: 1px solid var(--border-color); background: #f8fafc; border-radius: 4px; margin-bottom: 0.25rem;">
                    <div>
                        <strong>${medName}</strong><br>
                        <small>${item.dosage}, ${item.frequency}, for ${item.duration} days</small>
                    </div>
                    <button type="button" onclick="doctorUI.removePendingItem(${index})" style="background: var(--danger-color); padding: 0.25rem 0.5rem; font-size: 0.8rem;">Remove</button>
                </div>
            `;
        });
        container.innerHTML = html;
    },
    removePendingItem(index) {
        pendingPrescriptionItems.splice(index, 1);
        this.renderPendingItems();
    },

    closePatientView() {
        document.getElementById('doctor-selected-patient-view').classList.add('hidden');
        document.getElementById('doctor-patients-view').classList.remove('hidden');
        document.getElementById('doctor-medicines-view').classList.remove('hidden');
        document.querySelector('.dashboard-grid').style.display = 'grid'; // restore layout if needed
    },

    async viewPatient(patientId, patientName) {
        document.getElementById('doctor-patients-view').classList.add('hidden');
        document.getElementById('doctor-medicines-view').classList.add('hidden');
        document.getElementById('doctor-selected-patient-view').classList.remove('hidden');
        
        document.getElementById('doctor-selected-patient-title').textContent = `Patient: ${patientName}`;
        
        const prescriptionsDiv = document.getElementById('doctor-patient-prescriptions-list');
        const scheduleUl = document.getElementById('doctor-patient-schedule');
        const historyUl = document.getElementById('doctor-patient-history');
        
        prescriptionsDiv.innerHTML = 'Loading...';
        scheduleUl.innerHTML = 'Loading...';
        historyUl.innerHTML = 'Loading...';
        
        let prescriptionItemMap = {};
        let scheduleMap = {};

        // Load Prescriptions
        try {
            const prescriptions = await apiFetch(`/prescriptions/?patient_id=${patientId}`);
            prescriptionsDiv.innerHTML = '';
            
            if (prescriptions.length === 0) {
                prescriptionsDiv.innerHTML = '<div class="prescription-sig">No active prescriptions.</div>';
            }

            prescriptions.forEach(p => {
                let itemsHtml = '';
                if (p.items && p.items.length > 0) {
                    p.items.forEach(item => {
                        prescriptionItemMap[item.prescription_item_id] = {
                            prescription_id: p.prescription_id,
                            medicine_id: item.medicine_id,
                            dosage: item.dosage,
                            frequency: item.frequency
                        };
                        const med = medicineMap[item.medicine_id];
                        const medName = med ? `${med.medicine_name} (${med.strength})` : `Unknown Med (ID: ${item.medicine_id})`;
                        itemsHtml += `
                            <div class="prescription-item" style="border-top: 1px solid var(--border-color); padding-top: 0.5rem; margin-top: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div class="prescription-med">${medName}</div>
                                    <div class="prescription-sig">Take ${item.dosage}, ${item.frequency} for ${item.duration}</div>
                                </div>
                                <button class="button-danger" onclick="doctorUI.deletePrescriptionItem(${item.prescription_item_id}, ${patientId}, '${patientName}')" style="background: rgba(239, 68, 68, 0.1); color: var(--danger); border: 1px solid var(--danger); padding: 0.25rem 0.5rem; border-radius: 4px; cursor: pointer;">Delete Item</button>
                            </div>
                        `;
                    });
                } else {
                    itemsHtml = '<div class="prescription-sig">No items attached.</div>';
                }

                const div = document.createElement('div');
                div.className = 'prescription-card fade-in';
                div.innerHTML = `
                    <div class="prescription-header">
                        <div>
                            <span style="font-weight: bold; margin-right: 1rem;">Rx #${p.prescription_id}</span>
                            <span style="font-size: 0.9rem;">${p.start_date} to ${p.end_date}</span>
                        </div>
                        <button class="button-danger" onclick="doctorUI.deletePrescription(${p.prescription_id}, ${patientId}, '${patientName}')" style="background: var(--danger); color: white; border: none; padding: 0.25rem 0.5rem; border-radius: 4px; cursor: pointer;">Delete Rx</button>
                    </div>
                    ${itemsHtml}
                `;
                prescriptionsDiv.appendChild(div);
            });
        } catch (e) {
            prescriptionsDiv.innerHTML = `<div class="error">Error loading prescriptions: ${e.message}</div>`;
        }

        // Load Schedules
        try {
            const schedules = await apiFetch(`/schedules/?patient_id=${patientId}`);
            scheduleUl.innerHTML = '';
            if (schedules.length === 0) {
                scheduleUl.innerHTML = '<li class="schedule-item">No upcoming doses.</li>';
            }

            schedules.forEach(s => {
                scheduleMap[s.schedule_id] = s;
                const li = document.createElement('li');
                li.className = 'schedule-item fade-in';
                
                let medName = 'Unknown Medicine';
                let dosageInfo = '';
                
                const pItem = prescriptionItemMap[s.prescription_item_id];
                if (pItem) {
                    const med = medicineMap[pItem.medicine_id];
                    if (med) medName = `${med.medicine_name} (${med.strength})`;
                    dosageInfo = pItem.dosage;
                }

                li.innerHTML = `
                    <div class="schedule-time">${s.scheduled_time}</div>
                    <div class="schedule-details">
                        <div style="font-weight: 600;">${medName} - ${dosageInfo}</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem;">Qty: ${s.quantity_to_dispense} (Schedule #${s.schedule_id})</div>
                    </div>
                `;
                scheduleUl.appendChild(li);
            });
        } catch (e) {
            scheduleUl.innerHTML = `<li class="schedule-item error">Error loading schedules: ${e.message}</li>`;
        }

        // Load History
        try {
            const history = await apiFetch(`/dispensing/history/${patientId}`);
            historyUl.innerHTML = '';
            
            if (history.length === 0) {
                historyUl.innerHTML = '<li class="timeline-item"><div class="timeline-content">No history found.</div></li>';
            }

            history.forEach(l => {
                const li = document.createElement('li');
                
                const s = scheduleMap[l.schedule_id];
                let medName = 'Unknown Medicine';
                if (s) {
                    const pItem = prescriptionItemMap[s.prescription_item_id];
                    if (pItem && medicineMap[pItem.medicine_id]) {
                        medName = medicineMap[pItem.medicine_id].medicine_name;
                    }
                }

                let statusClass = '';
                let badgeClass = '';
                if (l.status === 'SUCCESS') { statusClass = 'success'; badgeClass = 'badge-success'; }
                else if (l.status === 'FAILED') { statusClass = 'missed'; badgeClass = 'badge-danger'; }
                else { badgeClass = 'badge-warning'; }

                const dateStr = l.dispense_datetime ? new Date(l.dispense_datetime).toLocaleString() : 'Unknown Date';

                li.className = `timeline-item ${statusClass} fade-in`;
                li.innerHTML = `
                    <div class="timeline-content">
                        <div class="timeline-date">${dateStr}</div>
                        <div class="timeline-title" style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-weight: bold; color: var(--primary-color);">${medName}</span>
                                <br/>
                                <span style="font-size: 0.9rem;">Dispensed Qty: ${l.quantity_dispensed}</span>
                            </div>
                            <span class="badge ${badgeClass}">${l.status}</span>
                        </div>
                    </div>
                `;
                historyUl.appendChild(li);
            });
        } catch (e) {
            historyUl.innerHTML = `<li class="timeline-item"><div class="timeline-content error">Error loading history: ${e.message}</div></li>`;
        }
    },

    async deletePrescription(rxId, patientId, patientName) {
        if (!confirm(`Are you sure you want to delete Prescription #${rxId}? This will remove all items and schedules.`)) return;
        try {
            await apiFetch(`/prescriptions/${rxId}`, { method: 'DELETE' });
            this.viewPatient(patientId, patientName);
        } catch (e) {
            alert("Error deleting prescription: " + e.message);
        }
    },

    async deletePrescriptionItem(itemId, patientId, patientName) {
        if (!confirm(`Are you sure you want to delete this medicine from the prescription?`)) return;
        try {
            await apiFetch(`/prescriptions/items/${itemId}`, { method: 'DELETE' });
            this.viewPatient(patientId, patientName);
        } catch (e) {
            alert("Error deleting prescription item: " + e.message);
        }
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
    
    const inventoryPayload = {
        expiry_month: parseInt(document.getElementById('cm-expiry-month').value, 10),
        expiry_year: parseInt(document.getElementById('cm-expiry-year').value, 10),
        quantity_to_add: parseInt(document.getElementById('cm-quantity').value, 10),
        minimum_stock_level: parseInt(document.getElementById('cm-min-stock').value, 10)
    };
    
    try {
        const newMed = await apiFetch('/medicines/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        inventoryPayload.medicine_id = newMed.medicine_id;
        
        await apiFetch('/inventory/topup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(inventoryPayload)
        });
        
        alert('Medicine and initial inventory added successfully!');
        document.getElementById('create-medicine-modal').classList.add('hidden');
        document.getElementById('create-medicine-form').reset();
        doctorUI.loadMedicines();
    } catch (err) {
        alert('Failed to add medicine: ' + err.message);
    }
});

document.getElementById('topup-medicine-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        medicine_id: parseInt(document.getElementById('tm-medicine-id').value, 10),
        expiry_month: parseInt(document.getElementById('tm-expiry-month').value, 10),
        expiry_year: parseInt(document.getElementById('tm-expiry-year').value, 10),
        quantity_to_add: parseInt(document.getElementById('tm-quantity').value, 10),
        minimum_stock_level: parseInt(document.getElementById('tm-min-stock').value, 10)
    };
    try {
        await apiFetch('/inventory/topup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        alert('Inventory topped up successfully!');
        document.getElementById('topup-medicine-modal').classList.add('hidden');
        document.getElementById('topup-medicine-form').reset();
        doctorUI.loadMedicines();
    } catch (err) {
        alert('Failed to top up inventory: ' + err.message);
    }
});

document.getElementById('cpr-add-medicine-btn').addEventListener('click', () => {
    const medicineId = parseInt(document.getElementById('cpr-medicine-id').value);
    const dosage = document.getElementById('cpr-dosage').value;
    const durationDays = document.getElementById('cpr-duration').value;

    const checkboxes = document.querySelectorAll('#cpr-schedule-times input[type="checkbox"]:checked');
    const scheduleTimes = Array.from(checkboxes).map(cb => cb.value);
    const scheduleLabels = Array.from(checkboxes).map(cb => cb.parentElement.textContent.trim());

    if (!medicineId || !dosage || scheduleTimes.length === 0 || !durationDays) {
        alert('Please fill out all medicine fields and select at least one schedule time.');
        return;
    }

    const frequencyStr = `${scheduleTimes.length} times a day (${scheduleLabels.join(', ')})`;

    pendingPrescriptionItems.push({
        medicine_id: medicineId,
        dosage: dosage,
        frequency: frequencyStr,
        schedule_times: scheduleTimes,
        duration: durationDays,
    });

    document.getElementById('cpr-medicine-id').value = '';
    document.getElementById('cpr-dosage').value = '';
    document.getElementById('cpr-duration').value = '';
    document.querySelectorAll('#cpr-schedule-times input[type="checkbox"]').forEach(cb => cb.checked = false);

    doctorUI.renderPendingItems();
});

document.getElementById('create-prescription-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (pendingPrescriptionItems.length === 0) {
        alert('Please add at least one medicine to the prescription.');
        return;
    }

    const patientId = parseInt(document.getElementById('cpr-patient-id').value);
    if (!patientId) {
        alert('Please select a patient.');
        return;
    }

    // Use max duration to set the end date of the prescription
    let maxDurationDays = 0;
    pendingPrescriptionItems.forEach(item => {
        if (parseInt(item.duration) > maxDurationDays) {
            maxDurationDays = parseInt(item.duration);
        }
    });

    const startDate = new Date();
    const endDate = new Date();
    endDate.setDate(startDate.getDate() + maxDurationDays);

    const payload = {
        patient_id: patientId,
        doctor_id: currentUser && currentUser.userid ? currentUser.userid : 1, 
        prescription_date: startDate.toISOString().split('T')[0],
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        items: pendingPrescriptionItems.map(item => ({
            medicine_id: item.medicine_id,
            dosage: item.dosage,
            frequency: item.frequency,
            schedule_times: item.schedule_times,
            duration: `${item.duration} days`
        }))
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
        pendingPrescriptionItems = [];
        doctorUI.renderPendingItems();
    } catch (err) {
        alert('Failed to create prescription: ' + err.message);
    }
});

// --- PATIENT UI ---
const patientUI = {
    async loadPrescriptions() {
        try {
            const prescriptions = await apiFetch('/prescriptions/');
            const container = document.getElementById('patient-prescriptions-list');
            container.innerHTML = '';
            
            if (prescriptions.length === 0) {
                container.innerHTML = '<p style="color: var(--text-secondary);">No active prescriptions.</p>';
            }

            prescriptions.forEach(p => {
                let itemsHtml = '';
                if (p.items && p.items.length > 0) {
                    p.items.forEach(item => {
                        prescriptionItemMap[item.prescription_item_id] = item;
                        const med = medicineMap[item.medicine_id];
                        const medName = med ? `${med.medicine_name} (${med.strength})` : `Medicine ID: ${item.medicine_id}`;
                        itemsHtml += `
                            <div class="prescription-body">
                                <div class="prescription-med">${medName}</div>
                                <div class="prescription-sig">Take ${item.dosage}, ${item.frequency} for ${item.duration}</div>
                            </div>
                        `;
                    });
                } else {
                    itemsHtml = '<div class="prescription-sig">No items attached.</div>';
                }

                const div = document.createElement('div');
                div.className = 'prescription-card fade-in';
                div.innerHTML = `
                    <div class="prescription-header">
                        <span>Rx #${p.prescription_id}</span>
                        <span>${p.start_date} to ${p.end_date}</span>
                    </div>
                    ${itemsHtml}
                `;
                container.appendChild(div);
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
            
            if (schedules.length === 0) {
                ul.innerHTML = '<li class="schedule-item">No upcoming doses.</li>';
            }

            schedules.forEach(s => {
                scheduleMap[s.schedule_id] = s;
                const li = document.createElement('li');
                li.className = 'schedule-item fade-in';
                
                let medName = 'Unknown Medicine';
                let dosageInfo = '';
                
                const pItem = prescriptionItemMap[s.prescription_item_id];
                if (pItem) {
                    const med = medicineMap[pItem.medicine_id];
                    if (med) {
                        medName = `${med.medicine_name} (${med.strength})`;
                    }
                    dosageInfo = pItem.dosage;
                }

                li.innerHTML = `
                    <div class="schedule-time">${s.scheduled_time}</div>
                    <div class="schedule-details">
                        <div style="font-weight: 600;">${medName} - ${dosageInfo}</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem;">Qty to dispense: ${s.quantity_to_dispense} (Schedule #${s.schedule_id})</div>
                    </div>
                `;
                ul.appendChild(li);
            });
        } catch (err) {
            console.error('Failed to load schedule', err);
        }
    },
    async loadHistory() {
        if (!currentUser || !currentUser.userid) return;
        try {
            const logs = await apiFetch(`/dispensing/history/${currentUser.userid}`);
            const ul = document.getElementById('patient-dispense-history');
            ul.innerHTML = '';

            if (logs.length === 0) {
                ul.innerHTML = '<p style="color: var(--text-secondary);">No dispense history found.</p>';
            }

            logs.forEach(l => {
                const li = document.createElement('li');
                const isSuccess = l.status === 'COMPLETED' || l.status === 'SUCCESS';
                const statusClass = isSuccess ? 'success' : (l.status === 'MISSED' ? 'missed' : 'pending');
                const badgeClass = isSuccess ? 'badge-success' : (l.status === 'MISSED' ? 'badge-danger' : 'badge-warning');
                
                li.className = `timeline-item ${statusClass} fade-in`;
                
                let medName = 'Unknown';
                const sched = scheduleMap[l.schedule_id];
                if (sched) {
                    const pItem = prescriptionItemMap[sched.prescription_item_id];
                    if (pItem && medicineMap[pItem.medicine_id]) {
                        medName = medicineMap[pItem.medicine_id].medicine_name;
                    }
                }
                
                // Use dispense_datetime instead of dispensed_at
                const dateStr = l.dispense_datetime ? new Date(l.dispense_datetime).toLocaleString() : 'Unknown Date';

                li.innerHTML = `
                    <div class="timeline-content">
                        <div class="timeline-date">${dateStr}</div>
                        <div class="timeline-title" style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-weight: bold; color: var(--primary-color);">${medName}</span>
                                <br/>
                                <span style="font-size: 0.9rem;">Dispensed Qty: ${l.quantity_dispensed}</span>
                            </div>
                            <span class="badge ${badgeClass}">${l.status}</span>
                        </div>
                    </div>
                `;
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
                    <td><span class="badge badge-primary">${u.role || '-'}</span></td>
                    <td><button class="outline" onclick="caregiverUI.selectPatient(${u.userid || u.id}, '${u.first_name} ${u.last_name}')">View Records</button></td>
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
            // Caregiver needs prescriptions loaded to populate prescriptionItemMap for this patient
            try {
                const prescriptions = await apiFetch(`/patients/${patientId}/prescriptions`);
                prescriptions.forEach(p => {
                    p.items.forEach(item => {
                        prescriptionItemMap[item.prescription_item_id] = {
                            prescription_id: p.prescription_id,
                            medicine_id: item.medicine_id,
                            dosage: item.dosage,
                            frequency: item.frequency
                        };
                    });
                });
            } catch(e) {
                console.warn("Could not load prescriptions for mapping", e);
            }

            const schedules = await apiFetch(`/schedules/?patient_id=${patientId}`);
            const ulSchedule = document.getElementById('caregiver-patient-schedule');
            ulSchedule.innerHTML = '';
            
            if (schedules.length === 0) {
                ulSchedule.innerHTML = '<li class="schedule-item">No upcoming doses.</li>';
            }

            schedules.forEach(s => {
                scheduleMap[s.schedule_id] = s;
                const li = document.createElement('li');
                li.className = 'schedule-item';
                
                let medName = 'Unknown Medicine';
                let dosageInfo = '';
                
                // To get medName for caregiver, we'd need prescriptions fetched.
                // Assuming caregiver dashboard calls loadPrescriptions first or we just show ID if unknown.
                const pItem = prescriptionItemMap[s.prescription_item_id];
                if (pItem) {
                    const med = medicineMap[pItem.medicine_id];
                    if (med) {
                        medName = `${med.medicine_name} (${med.strength})`;
                    }
                    dosageInfo = pItem.dosage;
                }

                li.innerHTML = `
                    <div class="schedule-time">${s.scheduled_time}</div>
                    <div class="schedule-details">
                        <div style="font-weight: 600;">${medName} - ${dosageInfo}</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem;">Qty to dispense: ${s.quantity_to_dispense} (Schedule #${s.schedule_id})</div>
                    </div>
                `;
                ulSchedule.appendChild(li);
            });
            
            const logs = await apiFetch(`/dispensing/history/${patientId}`);
            const ulHistory = document.getElementById('caregiver-patient-history');
            ulHistory.innerHTML = '';

            if (logs.length === 0) {
                ulHistory.innerHTML = '<p style="color: var(--text-secondary);">No dispense history found.</p>';
            }

            logs.forEach(l => {
                const li = document.createElement('li');
                const isSuccess = l.status === 'COMPLETED' || l.status === 'SUCCESS';
                const statusClass = isSuccess ? 'success' : (l.status === 'MISSED' ? 'missed' : 'pending');
                const badgeClass = isSuccess ? 'badge-success' : (l.status === 'MISSED' ? 'badge-danger' : 'badge-warning');
                
                let medName = 'Unknown';
                // For caregiver view, we'll try our best if scheduleMap has it (we need to populate scheduleMap in caregiver load schedule too)
                const sched = scheduleMap[l.schedule_id];
                if (sched) {
                    const pItem = prescriptionItemMap[sched.prescription_item_id];
                    if (pItem && medicineMap[pItem.medicine_id]) {
                        medName = medicineMap[pItem.medicine_id].medicine_name;
                    }
                }

                const dateStr = l.dispense_datetime ? new Date(l.dispense_datetime).toLocaleString() : 'Unknown Date';

                li.className = `timeline-item ${statusClass}`;
                li.innerHTML = `
                    <div class="timeline-content">
                        <div class="timeline-date">${dateStr}</div>
                        <div class="timeline-title" style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-weight: bold; color: var(--primary-color);">${medName}</span>
                                <br/>
                                <span style="font-size: 0.9rem;">Dispensed Qty: ${l.quantity_dispensed}</span>
                            </div>
                            <span class="badge ${badgeClass}">${l.status}</span>
                        </div>
                    </div>
                `;
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
        const nfcUid = document.getElementById('sim-nfc-uid').value;
        out.textContent = 'Checking due medicine...';
        
        let url = '/dispensing/due';
        if (nfcUid) {
            url += `?nfc_uid=${nfcUid}`;
        } else {
            out.textContent = "Error: Please enter a Simulated NFC UID.";
            return;
        }

        try {
            const due = await apiFetch(url, { headers: { 'X-Hardware-Api-Key': 'esp32-default-secret-key' } });
            if (due && due.length > 0) {
                this.currentDue = due[0];
                out.textContent = `Medicine Due!\nSchedule ID: ${this.currentDue.schedule_id}\nQuantity: ${this.currentDue.quantity_to_dispense}\nMedicine: ${this.currentDue.medicine_name || this.currentDue.medicine_id || 'Unknown'}`;
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
        const out = document.getElementById('sim-output');
        if (!this.currentDue) {
            out.textContent = "No schedule selected. Please 'Check Due' first.";
            return;
        }
        out.textContent = 'Dispensing in progress...';
        document.getElementById('sim-dispense-btn').disabled = true;

        const nfcUid = document.getElementById('sim-nfc-uid').value;
        if (!nfcUid) {
            out.textContent = "Error: Please enter a Simulated NFC UID.";
            return;
        }
        
        try {
            const payload = {
                schedule_id: this.currentDue.schedule_id,
                nfc_uid: nfcUid
            };
            const result = await apiFetch('/dispensing/dispense', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-Hardware-Api-Key': 'esp32-default-secret-key'
                },
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
