// Zeyta AI - Common Functions

// API Base URL
const API_BASE = '';

// Utility Functions
function showLoading(message = 'Processing...') {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        const loadingMessage = document.getElementById('loading-message');
        const loadingText = document.querySelector('.loading-text');
        if (loadingMessage) {
            loadingMessage.textContent = message;
        } else if (loadingText) {
            loadingText.textContent = message;
        }
        overlay.style.display = 'flex';
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add styles if not exists
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 80px;
                right: 20px;
                background: var(--card-bg);
                padding: 1rem 1.5rem;
                border-radius: 8px;
                box-shadow: var(--shadow);
                display: flex;
                align-items: center;
                gap: 1rem;
                z-index: 10000;
                animation: slideIn 0.3s ease;
            }
            .notification-success { border-left: 4px solid var(--success-color); }
            .notification-error { border-left: 4px solid var(--danger-color); }
            .notification-info { border-left: 4px solid var(--primary-color); }
            @keyframes slideIn {
                from { transform: translateX(400px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Update global status
async function updateStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        
        // Update status badges
        updateBadge('tts', data.tts);
        updateBadge('stt', data.stt);
        updateBadge('llm', data.llm);
        updateBadge('gpu', data.cuda_available, data.cuda_available ? 'GPU Available' : 'CPU Only');
        
        return data;
    } catch (error) {
        console.error('Failed to update status:', error);
        return null;
    }
}

function updateBadge(id, loaded, customText = null) {
    const badge = document.getElementById(`badge-${id}`);
    if (badge) {
        if (customText) {
            badge.textContent = customText;
            badge.className = 'status-badge ' + (loaded ? 'loaded' : '');
        } else {
            badge.textContent = loaded ? 'Loaded' : 'Not Loaded';
            badge.className = 'status-badge ' + (loaded ? 'loaded' : '');
        }
    }
    
    const statusBadge = document.getElementById(`${id}-status`);
    if (statusBadge) {
        statusBadge.textContent = loaded ? 'Loaded' : 'Not Loaded';
        statusBadge.className = 'status-badge ' + (loaded ? 'loaded' : '');
    }
}

// Initialize model
async function initializeModel(type, config = {}) {
    showLoading(`Initializing ${type.toUpperCase()} model...`);
    
    try {
        const response = await fetch(`${API_BASE}/api/initialize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type, ...config })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            showNotification(data.message, 'success');
            await updateStatus();
            return true;
        } else {
            showNotification(data.message, 'error');
            return false;
        }
    } catch (error) {
        hideLoading();
        showNotification(`Failed to initialize ${type}: ${error.message}`, 'error');
        return false;
    }
}

// Upload file helper
async function uploadFile(file, endpoint) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            body: formData
        });
        
        return await response.json();
    } catch (error) {
        throw new Error(`Upload failed: ${error.message}`);
    }
}

// Format time
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Check if all models are loaded
async function checkModelsLoaded(required = ['tts', 'stt', 'llm']) {
    const status = await updateStatus();
    if (!status) return false;
    
    const missing = required.filter(model => !status[model]);
    if (missing.length > 0) {
        showNotification(`Please initialize: ${missing.join(', ').toUpperCase()}`, 'error');
        return false;
    }
    
    return true;
}
