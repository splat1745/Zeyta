// Model Management Page JavaScript

// Update status on page load
document.addEventListener('DOMContentLoaded', () => {
    updateStatus();
    setInterval(updateStatus, 5000); // Update every 5 seconds
});

// Update model status
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        if (!response.ok) {
            console.error('Status fetch failed:', response.status);
            return;
        }
        
        const data = await response.json();
        
        // Update TTS status
        const ttsLoaded = data.tts;
        const ttsElement = document.getElementById('badge-tts');
        if (ttsElement) {
            ttsElement.textContent = ttsLoaded ? 'Loaded' : 'Not Loaded';
            ttsElement.className = `status-badge ${ttsLoaded ? 'loaded' : ''}`;
        }
        
        // Update STT status
        const sttLoaded = data.stt;
        const sttElement = document.getElementById('badge-stt');
        if (sttElement) {
            sttElement.textContent = sttLoaded ? 'Loaded' : 'Not Loaded';
            sttElement.className = `status-badge ${sttLoaded ? 'loaded' : ''}`;
        }
        
        // Update LLM status
        const llmLoaded = data.llm;
        const llmElement = document.getElementById('badge-llm');
        if (llmElement) {
            llmElement.textContent = llmLoaded ? 'Loaded' : 'Not Loaded';
            llmElement.className = `status-badge ${llmLoaded ? 'loaded' : ''}`;
        }
        
        // Update GPU status
        const gpuAvailable = data.cuda_available;
        const gpuElement = document.getElementById('badge-gpu');
        if (gpuElement) {
            gpuElement.textContent = gpuAvailable ? `GPU: ${data.cuda_device || 'Available'}` : 'CPU Only';
            gpuElement.className = `status-badge ${gpuAvailable ? 'loaded' : ''}`;
        }
        
        // Update model info
        const ttsInfoElement = document.getElementById('tts-info');
        if (ttsInfoElement) {
            if (ttsLoaded && data.tts_config) {
                const backend = (data.tts_backend || data.tts_config.backend || 'chatterbox').toString();
                const deviceLabel = data.tts_config.device ? data.tts_config.device.toUpperCase() : 'UNKNOWN';
                ttsInfoElement.innerHTML = `
                    <p><strong>Backend:</strong> ${backend}</p>
                    <p><strong>Device:</strong> ${deviceLabel}</p>
                `;
            } else {
                ttsInfoElement.innerHTML = '';
            }
        }
        
        const sttInfoElement = document.getElementById('stt-info');
        if (sttInfoElement) {
            if (sttLoaded && data.stt_config) {
                sttInfoElement.innerHTML = `
                    <p><strong>Model Size:</strong> ${data.stt_config.size || 'base'}</p>
                    <p><strong>Device:</strong> ${data.stt_config.device || 'auto'}</p>
                    <p><strong>Compute Type:</strong> ${data.stt_config.compute_type || 'auto'}</p>
                `;
            } else {
                sttInfoElement.innerHTML = '';
            }
        }
        
        const llmInfoElement = document.getElementById('llm-info');
        if (llmInfoElement) {
            if (llmLoaded) {
                llmInfoElement.innerHTML = `
                    <p><strong>Status:</strong> Ready</p>
                `;
            } else {
                llmInfoElement.innerHTML = '';
            }
        }
        
    } catch (error) {
        console.error('Status update failed:', error);
    }
}

// Load TTS model
async function loadTTS() {
    const device = document.getElementById('tts-device').value;
    const backendSelect = document.getElementById('tts-backend-models');
    const reinstallSelect = document.getElementById('tts-reinstall-models');
    const backend = backendSelect ? backendSelect.value : undefined;
    const allowReinstall = reinstallSelect ? reinstallSelect.value === 'true' : undefined;

    showLoading('Loading TTS model...');

    try {
        const response = await fetch('/api/initialize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'tts', device: device, backend: backend, allow_reinstall: allowReinstall })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            await updateStatus();
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Failed to load TTS: ' + error.message, 'error');
        console.error('TTS load error:', error);
    } finally {
        hideLoading();
    }
}

// Load STT model
async function loadSTT() {
    const size = document.getElementById('stt-size').value;
    const device = document.getElementById('stt-device').value;
    const compute = document.getElementById('stt-compute').value;
    
    showLoading(`Loading STT model (${size}, ${device})... This may take a while on first load.`);
    
    try {
        const response = await fetch('/api/initialize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                type: 'stt', 
                size: size,
                device: device,
                compute_type: compute
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            await updateStatus();
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Failed to load STT: ' + error.message, 'error');
        console.error('STT load error:', error);
    } finally {
        hideLoading();
    }
}

// Load LLM model
async function loadLLM() {
    showLoading('Loading LLM model from core/brain.py...');
    
    try {
        const response = await fetch('/api/initialize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'llm' })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            await updateStatus();
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Failed to load LLM: ' + error.message, 'error');
        console.error('LLM load error:', error);
    } finally {
        hideLoading();
    }
}

// Unload a model
async function unloadModel(type) {
    if (!confirm(`Are you sure you want to unload the ${type.toUpperCase()} model?`)) {
        return;
    }
    
    showLoading(`Unloading ${type.toUpperCase()} model...`);
    
    try {
        const response = await fetch('/api/unload', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: type })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            await updateStatus();
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification(`Failed to unload ${type}: ` + error.message, 'error');
        console.error('Unload error:', error);
    } finally {
        hideLoading();
    }
}

// Load all models
async function loadAll() {
    if (!confirm('This will load all models. This may take several minutes and use significant memory. Continue?')) {
        return;
    }
    
    showLoading('Loading all models... This will take a while.');
    
    try {
        // Load TTS
        const ttsResponse = await fetch('/api/initialize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                type: 'tts', 
                device: document.getElementById('tts-device').value 
            })
        });
        const ttsData = await ttsResponse.json();
        if (!ttsData.success) {
            showNotification('TTS: ' + ttsData.message, 'warning');
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Load STT
        const sttResponse = await fetch('/api/initialize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                type: 'stt', 
                size: document.getElementById('stt-size').value,
                device: document.getElementById('stt-device').value,
                compute_type: document.getElementById('stt-compute').value
            })
        });
        const sttData = await sttResponse.json();
        if (!sttData.success) {
            showNotification('STT: ' + sttData.message, 'warning');
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Load LLM
        const llmResponse = await fetch('/api/initialize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'llm' })
        });
        const llmData = await llmResponse.json();
        if (!llmData.success) {
            showNotification('LLM: ' + llmData.message, 'warning');
        }
        
        showNotification('All models loaded!', 'success');
        updateStatus();
    } catch (error) {
        showNotification('Failed to load all models: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Unload all models
async function unloadAll() {
    if (!confirm('Are you sure you want to unload ALL models? This will free memory.')) {
        return;
    }
    
    showLoading('Unloading all models...');
    
    try {
        const response = await fetch('/api/unload', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'all' })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            await updateStatus();
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Failed to unload all models: ' + error.message, 'error');
        console.error('Unload all error:', error);
    } finally {
        hideLoading();
    }
}
