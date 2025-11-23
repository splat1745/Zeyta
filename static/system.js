// System Info Page Functions

let dependenciesLoaded = false;

async function refreshSystemInfo(isFirstLoad = false) {
    if (isFirstLoad) showLoading('Fetching system information...');
    
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        
        if (isFirstLoad) hideLoading();
        
        if (!data) {
            if (isFirstLoad) showNotification('Failed to fetch system info', 'error');
            return;
        }
        
        // Update hardware info
        document.getElementById('gpu-available').innerHTML = data.cuda_available 
            ? '<i class="fas fa-check-circle" style="color: var(--success-color);"></i> Yes'
            : '<i class="fas fa-times-circle" style="color: var(--danger-color);"></i> No';
        
        document.getElementById('gpu-device').textContent = data.cuda_device || 'N/A';
        
        // Update model status
        document.getElementById('model-tts').innerHTML = data.tts 
            ? '<i class="fas fa-check-circle" style="color: var(--success-color);"></i> Loaded'
            : '<i class="fas fa-times-circle" style="color: var(--danger-color);"></i> Not Loaded';
        
        document.getElementById('model-stt').innerHTML = data.stt 
            ? '<i class="fas fa-check-circle" style="color: var(--success-color);"></i> Loaded'
            : '<i class="fas fa-times-circle" style="color: var(--danger-color);"></i> Not Loaded';
        
        document.getElementById('model-llm').innerHTML = data.llm 
            ? '<i class="fas fa-check-circle" style="color: var(--success-color);"></i> Loaded'
            : '<i class="fas fa-times-circle" style="color: var(--danger-color);"></i> Not Loaded';
        
        // Update model configs
        if (data.tts_config) {
            document.getElementById('tts-device').textContent = data.tts_config.device || 'N/A';
        }
        
        if (data.stt_config) {
            document.getElementById('stt-size').textContent = data.stt_config.size || 'N/A';
            document.getElementById('stt-device').textContent = data.stt_config.device || 'N/A';
            document.getElementById('stt-compute').textContent = data.stt_config.compute_type || 'N/A';
        }
        
        // Update output count
        document.getElementById('output-count').textContent = data.output_files || 0;

        // Update real-time resources
        if (data.cpu_usage !== undefined) {
            updateProgressBar('cpu-bar', 'cpu-usage', data.cpu_usage);
        }
        if (data.ram_usage !== undefined) {
            updateProgressBar('ram-bar', 'ram-usage', data.ram_usage);
        }
        if (data.gpu_memory_percent !== undefined) {
            updateProgressBar('gpu-bar', 'gpu-usage', Math.round(data.gpu_memory_percent));
        }
        
        // Update dependencies (Terminal View) - Only once
        if (data.dependencies && !dependenciesLoaded) {
            const terminal = document.getElementById('dependencies-grid');
            terminal.innerHTML = '';
            
            // Add header
            addTerminalLine(terminal, 'System diagnostics started...', 'info');
            addTerminalLine(terminal, `Checking ${Object.keys(data.dependencies).length} packages...`, 'info');
            
            for (const [pkg, installed] of Object.entries(data.dependencies)) {
                const status = installed ? 'INSTALLED' : 'MISSING';
                const level = installed ? 'info' : 'error';
                addTerminalLine(terminal, `Package [${pkg}] ... ${status}`, level);
            }
            
            addTerminalLine(terminal, 'Diagnostics complete.', 'info');
            dependenciesLoaded = true;
        }
        
        if (isFirstLoad) showNotification('System info updated', 'success');
        
    } catch (error) {
        if (isFirstLoad) hideLoading();
        console.error(error);
        if (isFirstLoad) showNotification(`Failed to fetch system info: ${error.message}`, 'error');
    }
}

function addTerminalLine(container, text, level) {
    const line = document.createElement('div');
    line.className = 'terminal-line';
    const timestamp = new Date().toLocaleTimeString();
    
    let colorClass = 'level-info';
    if (level === 'warn') colorClass = 'level-warn';
    if (level === 'error') colorClass = 'level-error';
    
    line.innerHTML = `
        <span class="timestamp">[${timestamp}]</span>
        <span class="${colorClass}">${text}</span>
    `;
    container.appendChild(line);
    container.scrollTop = container.scrollHeight;
}

// Simulate Real-time Resources
function startResourceSimulation() {
    setInterval(() => {
        // Simulate CPU (10-40%)
        const cpu = Math.floor(Math.random() * 30) + 10;
        updateProgressBar('cpu-bar', 'cpu-usage', cpu);
        
        // Simulate RAM (40-60%)
        const ram = Math.floor(Math.random() * 20) + 40;
        updateProgressBar('ram-bar', 'ram-usage', ram);
        
        // Simulate GPU Memory (if GPU available, else 0)
        const gpuAvailable = document.getElementById('gpu-available').textContent.includes('Yes');
        const gpu = gpuAvailable ? Math.floor(Math.random() * 20) + 5 : 0;
        updateProgressBar('gpu-bar', 'gpu-usage', gpu);
        
    }, 2000);
}

function updateProgressBar(barId, textId, value) {
    const bar = document.getElementById(barId);
    const text = document.getElementById(textId);
    if (bar && text) {
        bar.style.width = `${value}%`;
        text.textContent = `${value}%`;
        
        // Color change based on load
        if (value > 80) bar.style.backgroundColor = 'var(--danger-color)';
        else if (value > 50) bar.style.backgroundColor = 'var(--warning-color)';
        else bar.style.backgroundColor = barId.includes('gpu') ? 'var(--success-color)' : (barId.includes('ram') ? 'var(--secondary-color)' : 'var(--primary-color)');
    }
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    refreshSystemInfo(true);
    // Refresh every 2 seconds
    setInterval(() => refreshSystemInfo(false), 2000);
});
