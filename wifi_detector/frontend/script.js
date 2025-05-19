// API endpoint
const API_BASE_URL = 'http://localhost:8001';

// DOM elements
const devicesList = document.getElementById('devicesList');
const addDeviceForm = document.getElementById('addDeviceForm');
const deviceName = document.getElementById('deviceName');
const deviceMac = document.getElementById('deviceMac');
const loginForm = document.getElementById('loginForm');
const username = document.getElementById('username');
const password = document.getElementById('password');
const loginError = document.getElementById('loginError');
const authSection = document.getElementById('authSection');
const mainContent = document.getElementById('mainContent');
const logoutBtn = document.getElementById('logoutBtn');
const themeToggle = document.getElementById('themeToggle');
const changePasswordBtn = document.getElementById('changePasswordBtn');
const changePasswordForm = document.getElementById('changePasswordForm');
const newUsername = document.getElementById('newUsername');
const newPassword = document.getElementById('newPassword');
const confirmPassword = document.getElementById('confirmPassword');
const passwordError = document.getElementById('passwordError');
const statsContainer = document.getElementById('statsContainer');

// State variables
let credentials = null;
let darkMode = localStorage.getItem('darkMode') === 'true';

// Initialize the application
function init() {
    // Check for saved credentials
    const savedCredentials = localStorage.getItem('credentials');
    if (savedCredentials) {
        credentials = JSON.parse(savedCredentials);
        showMainContent();
        loadDevices();
        loadNetworkStats();
    } else {
        showAuthSection();
    }
    
    // Set initial theme
    updateTheme();
}

// Authentication functions
function showAuthSection() {
    authSection.style.display = 'block';
    mainContent.style.display = 'none';
}

function showMainContent() {
    authSection.style.display = 'none';
    mainContent.style.display = 'block';
}

function login(event) {
    event.preventDefault();
    
    const auth = btoa(`${username.value}:${password.value}`);
    
    fetch(`${API_BASE_URL}/devices`, {
        headers: {
            'Authorization': `Basic ${auth}`
        }
    })
    .then(response => {
        if (response.ok) {
            credentials = {
                username: username.value,
                auth: auth
            };
            localStorage.setItem('credentials', JSON.stringify(credentials));
            showMainContent();
            loadDevices();
            loadNetworkStats();
            loginForm.reset();
            loginError.textContent = '';
        } else {
            throw new Error('Invalid credentials');
        }
    })
    .catch(error => {
        loginError.textContent = error.message;
    });
}

function logout() {
    credentials = null;
    localStorage.removeItem('credentials');
    showAuthSection();
    devicesList.innerHTML = '';
}

function changePassword(event) {
    event.preventDefault();
    
    if (newPassword.value !== confirmPassword.value) {
        passwordError.textContent = 'Passwords do not match';
        return;
    }
    
    fetch(`${API_BASE_URL}/credentials`, {
        method: 'PUT',
        headers: {
            'Authorization': `Basic ${credentials.auth}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: newUsername.value,
            password: newPassword.value
        })
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to update credentials');
        }
    })
    .then(data => {
        // Update credentials
        const auth = btoa(`${newUsername.value}:${newPassword.value}`);
        credentials = {
            username: newUsername.value,
            auth: auth
        };
        localStorage.setItem('credentials', JSON.stringify(credentials));
        
        // Hide form and show success message
        changePasswordForm.style.display = 'none';
        passwordError.textContent = '';
        alert('Credentials updated successfully. You will need to use the new credentials next time you log in.');
    })
    .catch(error => {
        passwordError.textContent = error.message;
    });
}

// Device management functions
function loadDevices() {
    fetch(`${API_BASE_URL}/devices`, {
        headers: {
            'Authorization': `Basic ${credentials.auth}`
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to load devices');
        }
    })
    .then(data => {
        renderDevices(data.devices);
    })
    .catch(error => {
        console.error('Error loading devices:', error);
    });
}

function renderDevices(devices) {
    devicesList.innerHTML = '';
    
    if (devices.length === 0) {
        devicesList.innerHTML = '<tr><td colspan="5" class="text-center">No devices added yet</td></tr>';
        return;
    }
    
    devices.forEach(device => {
        const row = document.createElement('tr');
        row.className = device.online ? 'online' : 'offline';
        
        row.innerHTML = `
            <td>${device.id}</td>
            <td>${device.name}</td>
            <td>${device.mac}</td>
            <td>${device.manufacturer || 'Unknown'}</td>
            <td>${device.online ? 'Online' : 'Offline'}</td>
            <td>
                <button class="btn btn-edit" data-id="${device.id}" data-name="${device.name}" data-mac="${device.mac}">Edit</button>
                <button class="btn btn-delete" data-id="${device.id}">Delete</button>
            </td>
        `;
        
        devicesList.appendChild(row);
    });
    
    // Add event listeners to edit and delete buttons
    document.querySelectorAll('.btn-edit').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.getAttribute('data-id');
            const name = button.getAttribute('data-name');
            const mac = button.getAttribute('data-mac');
            
            // Populate form with device data
            deviceName.value = name;
            deviceMac.value = mac;
            
            // Change form submit action
            addDeviceForm.onsubmit = (event) => {
                event.preventDefault();
                updateDevice(id);
            };
            
            // Change button text
            document.querySelector('#addDeviceForm button[type="submit"]').textContent = 'Update Device';
        });
    });
    
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.getAttribute('data-id');
            if (confirm('Are you sure you want to delete this device?')) {
                deleteDevice(id);
            }
        });
    });
}

function addDevice(event) {
    event.preventDefault();
    
    fetch(`${API_BASE_URL}/devices`, {
        method: 'POST',
        headers: {
            'Authorization': `Basic ${credentials.auth}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: deviceName.value,
            mac: deviceMac.value
        })
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then(data => {
                throw new Error(data.detail || 'Failed to add device');
            });
        }
    })
    .then(data => {
        addDeviceForm.reset();
        loadDevices();
        loadNetworkStats();
    })
    .catch(error => {
        alert(error.message);
    });
}

function updateDevice(id) {
    fetch(`${API_BASE_URL}/devices/${id}`, {
        method: 'PUT',
        headers: {
            'Authorization': `Basic ${credentials.auth}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: deviceName.value,
            mac: deviceMac.value
        })
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then(data => {
                throw new Error(data.detail || 'Failed to update device');
            });
        }
    })
    .then(data => {
        // Reset form
        addDeviceForm.reset();
        
        // Change form submit action back to add
        addDeviceForm.onsubmit = addDevice;
        
        // Change button text back
        document.querySelector('#addDeviceForm button[type="submit"]').textContent = 'Add Device';
        
        // Reload devices
        loadDevices();
        loadNetworkStats();
    })
    .catch(error => {
        alert(error.message);
    });
}

function deleteDevice(id) {
    fetch(`${API_BASE_URL}/devices/${id}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Basic ${credentials.auth}`
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to delete device');
        }
    })
    .then(data => {
        loadDevices();
        loadNetworkStats();
    })
    .catch(error => {
        alert(error.message);
    });
}

// Network stats functions
function loadNetworkStats() {
    fetch(`${API_BASE_URL}/network-stats`, {
        headers: {
            'Authorization': `Basic ${credentials.auth}`
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to load network stats');
        }
    })
    .then(data => {
        renderNetworkStats(data);
    })
    .catch(error => {
        console.error('Error loading network stats:', error);
    });
}

function renderNetworkStats(stats) {
    statsContainer.innerHTML = `
        <div class="stats-card">
            <h3>Device Status</h3>
            <div class="stats-content">
                <div class="stat-item">
                    <span class="stat-label">Total Devices:</span>
                    <span class="stat-value">${stats.total_devices}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Online:</span>
                    <span class="stat-value online-text">${stats.online_devices}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Offline:</span>
                    <span class="stat-value offline-text">${stats.offline_devices}</span>
                </div>
            </div>
        </div>
        
        <div class="stats-card">
            <h3>Manufacturer Distribution</h3>
            <div class="stats-content">
                ${stats.manufacturers.map(m => `
                    <div class="stat-item">
                        <span class="stat-label">${m.name}:</span>
                        <span class="stat-value">${m.count} (${m.online} online)</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Theme functions
function toggleTheme() {
    darkMode = !darkMode;
    localStorage.setItem('darkMode', darkMode);
    updateTheme();
}

function updateTheme() {
    if (darkMode) {
        document.body.classList.add('dark-mode');
        themeToggle.textContent = '☀️ Light Mode';
    } else {
        document.body.classList.remove('dark-mode');
        themeToggle.textContent = '🌙 Dark Mode';
    }
}

// Password change functions
function showChangePasswordForm() {
    chpyenv shell 3.12.8
[200~echo "Creating WiFi detector frontend script.js..."
cat > all_in_one/wifi_detector/frontend/script.js << 'EOF'
// API endpoint
const API_BASE_URL = 'http://localhost:8001';

// DOM elements
const devicesList = document.getElementById('devicesList');
const addDeviceForm = document.getElementById('addDeviceForm');
const deviceName = document.getElementById('deviceName');
const deviceMac = document.getElementById('deviceMac');
const loginForm = document.getElementById('loginForm');
const username = document.getElementById('username');
const password = document.getElementById('password');
const loginError = document.getElementById('loginError');
const authSection = document.getElementById('authSection');
const mainContent = document.getElementById('mainContent');
const logoutBtn = document.getElementById('logoutBtn');
const themeToggle = document.getElementById('themeToggle');

// State variables
let credentials = null;
let darkMode = localStorage.getItem('darkMode') === 'true';

// Initialize the application
function init() {
    const savedCredentials = localStorage.getItem('credentials');
    if (savedCredentials) {
        credentials = JSON.parse(savedCredentials);
        showMainContent();
        loadDevices();
    } else {
        showAuthSection();
    }
    updateTheme();
}

// Authentication functions
function showAuthSection() {
    authSection.style.display = 'block';
    mainContent.style.display = 'none';
}

function showMainContent() {
    authSection.style.display = 'none';
    mainContent.style.display = 'block';
}

function login(event) {
    event.preventDefault();
    const auth = btoa(`${username.value}:${password.value}`);
    fetch(`${API_BASE_URL}/devices`, {
        headers: { 'Authorization': `Basic ${auth}` }
    })
    .then(response => {
        if (response.ok) {
            credentials = { username: username.value, auth: auth };
            localStorage.setItem('credentials', JSON.stringify(credentials));
            showMainContent();
            loadDevices();
            loginForm.reset();
            loginError.textContent = '';
        } else {
            throw new Error('Invalid credentials');
        }
    })
    .catch(error => {
        loginError.textContent = error.message;
    });
}

function logout() {
    credentials = null;
    localStorage.removeItem('credentials');
    showAuthSection();
    devicesList.innerHTML = '';
}

// Device management functions
function loadDevices() {
    fetch(`${API_BASE_URL}/devices`, {
        headers: { 'Authorization': `Basic ${credentials.auth}` }
    })
    .then(response => response.ok ? response.json() : Promise.reject('Failed to load devices'))
    .then(data => renderDevices(data.devices))
    .catch(error => console.error('Error:', error));
}

function renderDevices(devices) {
    devicesList.innerHTML = '';
    if (devices.length === 0) {
        devicesList.innerHTML = '<tr><td colspan="5" class="text-center">No devices added yet</td></tr>';
        return;
    }
    
    devices.forEach(device => {
        const row = document.createElement('tr');
        row.className = device.online ? 'online' : 'offline';
        row.innerHTML = `
            <td>${device.id}</td>
            <td>${device.name}</td>
            <td>${device.mac}</td>
            <td>${device.manufacturer || 'Unknown'}</td>
            <td>${device.online ? 'Online' : 'Offline'}</td>
            <td>
                <button class="btn btn-edit" data-id="${device.id}" data-name="${device.name}" data-mac="${device.mac}">Edit</button>
                <button class="btn btn-delete" data-id="${device.id}">Delete</button>
            </td>
        `;
        devicesList.appendChild(row);
    });
    
    // Add event listeners
    document.querySelectorAll('.btn-edit').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.getAttribute('data-id');
            const name = button.getAttribute('data-name');
            const mac = button.getAttribute('data-mac');
            deviceName.value = name;
            deviceMac.value = mac;
            addDeviceForm.onsubmit = (e) => { e.preventDefault(); updateDevice(id); };
            document.querySelector('#addDeviceForm button[type="submit"]').textContent = 'Update Device';
        });
    });
    
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.getAttribute('data-id');
            if (confirm('Are you sure you want to delete this device?')) {
                deleteDevice(id);
            }
        });
    });
}

// Theme functions
function toggleTheme() {
    darkMode = !darkMode;
    localStorage.setItem('darkMode', darkMode);
    updateTheme();
}

function updateTheme() {
    if (darkMode) {
        document.body.classList.add('dark-mode');
        themeToggle.textContent = '☀️ Light Mode';
    } else {
        document.body.classList.remove('dark-mode');
        themeToggle.textContent = '🌙 Dark Mode';
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', init);
loginForm.addEventListener('submit', login);
addDeviceForm.addEventListener('submit', addDevice);
logoutBtn.addEventListener('click', logout);
themeToggle.addEventListener('click', toggleTheme);

// Refresh data periodically
setInterval(loadDevices, 30000);


if (loginForm) {
  loginForm.addEventListener('submit', function (e) {
    e.preventDefault();
    fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username.value,
        password: password.value
      })
    })
    .then(response => {
      if (!response.ok) throw new Error("Login failed");
      return response.json();
    })
    .then(data => {
      localStorage.setItem("authenticated", "true");
      location.reload();
    })
    .catch(error => {
      loginError.textContent = "Invalid credentials";
    });
  });
}
