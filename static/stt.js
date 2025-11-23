// STT Page Functions

let currentAudioFile = null;
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let socket = null;
let audioContext, analyser, dataArray, visualizerFrame;

function showSTTSettings() {
    document.getElementById('stt-settings-modal').style.display = 'flex';
}

function closeSTTSettings() {
    document.getElementById('stt-settings-modal').style.display = 'none';
}

async function initializeSTT() {
    const size = document.getElementById('model-size').value;
    const device = document.getElementById('device').value;
    const computeType = document.getElementById('compute-type').value;
    
    closeSTTSettings();
    
    await initializeModel('stt', {
        size: size,
        device: device,
        compute_type: computeType
    });
}

function switchTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Find and activate the clicked tab button
    const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(btn => {
        return btn.textContent.toLowerCase().includes(tab);
    });
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
    
    // Update tab content
    document.getElementById('file-tab').style.display = tab === 'file' ? 'block' : 'none';
    document.getElementById('live-tab').style.display = tab === 'live' ? 'block' : 'none';
    
    if (tab === 'live') {
        populateAudioSources();
    }
}

async function populateAudioSources() {
    const select = document.getElementById('audio-source');
    if (!select) return;
    
    // Keep default option
    select.innerHTML = '<option value="default">Default Microphone</option>';
    
    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return;
    
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        devices.forEach(device => {
            if (device.kind === 'audioinput') {
                const option = document.createElement('option');
                option.value = device.deviceId;
                option.textContent = device.label || `Microphone ${select.length + 1}`;
                select.appendChild(option);
            }
        });
    } catch (err) {
        console.error('Error enumerating devices:', err);
    }
}

async function handleAudioUpload(input) {
    const file = input.files[0];
    if (!file) return;
    
    currentAudioFile = file;
    
    // Update UI
    document.querySelector('#audio-upload-area .upload-placeholder').style.display = 'none';
    document.querySelector('#audio-upload-area .upload-success').style.display = 'block';
    document.getElementById('audio-filename').textContent = file.name;
}

async function transcribeFile() {
    if (!currentAudioFile) {
        showNotification('Please upload an audio file first', 'error');
        return;
    }
    
    // Check if STT is loaded
    const status = await updateStatus();
    if (!status || !status.stt) {
        showNotification('Please initialize STT model first', 'error');
        return;
    }
    
    showLoading('Transcribing audio...');
    
    try {
        const data = await uploadFile(currentAudioFile, '/api/stt/transcribe');
        hideLoading();
        
        if (data.success) {
            displayTranscript(data.text, data.language, data.language_probability);
            showNotification('Transcription completed!', 'success');
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        hideLoading();
        showNotification(error.message, 'error');
    }
}

function displayTranscript(text, language, confidence) {
    const panel = document.getElementById('transcript-panel');
    panel.style.display = 'block';
    
    document.getElementById('transcript-text').textContent = text;
    document.getElementById('language-info').innerHTML = `<i class="fas fa-language" style="color: var(--primary-color);"></i> Language: <strong>${language.toUpperCase()}</strong>`;
    document.getElementById('confidence-info').innerHTML = `<i class="fas fa-percentage" style="color: var(--success-color);"></i> Confidence: <strong>${(confidence * 100).toFixed(1)}%</strong>`;
    
    panel.scrollIntoView({ behavior: 'smooth' });
    
    addToRecentSTT(text, language);
}

function copyTranscript() {
    const text = document.getElementById('transcript-text').textContent;
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Transcript copied to clipboard!', 'success');
    }).catch(err => {
        showNotification('Failed to copy transcript', 'error');
    });
}

let recordingStartTime;
let recordingTimerInterval;

async function toggleRecording() {
    if (!isRecording) {
        await startRecording();
    } else {
        stopRecording();
    }
}

async function startRecording() {
    // Check if STT is loaded
    const status = await updateStatus();
    if (!status || !status.stt) {
        showNotification('Please initialize STT model first', 'error');
        return;
    }
    
    // Check if getUserMedia is supported
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        if (window.location.hostname !== 'localhost' && window.location.protocol !== 'https:') {
            showNotification('Audio recording requires HTTPS or localhost.', 'error');
            return;
        }
        showNotification('Your browser does not support audio recording.', 'error');
        return;
    }
    
    const deviceId = document.getElementById('audio-source').value;
    const constraints = { 
        audio: {
            deviceId: deviceId !== 'default' ? { exact: deviceId } : undefined,
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
        } 
    };
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            const audioFile = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });
            
            showLoading('Transcribing recording...');
            const startTime = performance.now();
            
            try {
                const data = await uploadFile(audioFile, '/api/stt/transcribe');
                const endTime = performance.now();
                hideLoading();
                
                if (data.success) {
                    displayTranscript(data.text, data.language, data.language_probability);
                    showNotification('Recording transcribed!', 'success');
                    
                    // Update stats
                    document.getElementById('stt-latency').textContent = `${Math.round(endTime - startTime)}ms`;
                } else {
                    showNotification(data.message, 'error');
                }
            } catch (error) {
                hideLoading();
                showNotification(error.message, 'error');
            }
            
            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
            stopVisualizer();
            
            // Reset stats
            document.getElementById('vad-status').textContent = 'IDLE';
            document.getElementById('vad-status').style.color = 'var(--text-secondary)';
        };
        
        mediaRecorder.start();
        isRecording = true;
        
        // Update UI
        const recordBtn = document.getElementById('record-btn');
        recordBtn.classList.add('recording');
        recordBtn.innerHTML = '<i class="fas fa-stop"></i>';
        
        document.getElementById('record-ring').style.opacity = '1';
        document.getElementById('recording-status-text').textContent = 'RECORDING IN PROGRESS...';
        document.getElementById('recording-status-text').style.color = 'var(--danger-color)';
        
        document.getElementById('vad-status').textContent = 'LISTENING';
        document.getElementById('vad-status').style.color = 'var(--success-color)';
        
        // Start Timer
        recordingStartTime = Date.now();
        recordingTimerInterval = setInterval(updateRecordingTimer, 1000);
        
        startVisualizer(stream);
        startVADStats(); 
        
        showNotification('Recording started...', 'info');
        
    } catch (error) {
        showNotification('Failed to access microphone: ' + error.message, 'error');
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        // Update UI
        const recordBtn = document.getElementById('record-btn');
        recordBtn.classList.remove('recording');
        recordBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        
        document.getElementById('record-ring').style.opacity = '0';
        document.getElementById('recording-status-text').textContent = 'READY TO RECORD';
        document.getElementById('recording-status-text').style.color = 'var(--text-secondary)';
        
        // Stop Timer
        clearInterval(recordingTimerInterval);
        document.getElementById('recording-timer').textContent = '00:00';
        
        stopVADStats();
    }
}

function updateRecordingTimer() {
    const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
    const seconds = (elapsed % 60).toString().padStart(2, '0');
    document.getElementById('recording-timer').textContent = `${minutes}:${seconds}`;
}

function startVisualizer(stream) {
    const container = document.getElementById('live-visualizer');
    container.innerHTML = ''; // Clear previous
    
    // Calculate number of bars based on width
    // Bar width = 8px, Gap = 4px (from CSS) -> Total 12px per bar
    const containerWidth = container.clientWidth || 300;
    const barWidth = 12;
    const barCount = Math.floor(containerWidth / barWidth);
    
    // Create bars dynamically
    for (let i = 0; i < barCount; i++) {
        const bar = document.createElement('div');
        bar.className = 'visualizer-bar';
        bar.style.height = '4px';
        container.appendChild(bar);
    }
    
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioContext.createMediaStreamSource(stream);
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 256; // Increased FFT size to ensure enough data points
    source.connect(analyser);
    
    const bufferLength = analyser.frequencyBinCount;
    dataArray = new Uint8Array(bufferLength);
    
    const bars = container.querySelectorAll('.visualizer-bar');
    
    function draw() {
        visualizerFrame = requestAnimationFrame(draw);
        analyser.getByteFrequencyData(dataArray);
        
        bars.forEach((bar, index) => {
            // Map index to dataArray
            // If we have more bars than data, we might get 0, which is fine.
            // If we have fewer bars, we just show the lower frequencies.
            const value = dataArray[index] || 0;
            const height = Math.max(4, (value / 255) * 100);
            bar.style.height = `${height}%`;
            
            // Color based on intensity
            if (value > 200) {
                bar.style.background = 'var(--danger-color)';
                bar.style.boxShadow = '0 0 10px var(--danger-color)';
            } else if (value > 100) {
                bar.style.background = 'var(--warning-color)';
                bar.style.boxShadow = '0 0 5px var(--warning-color)';
            } else {
                bar.style.background = 'var(--primary-color)';
                bar.style.boxShadow = 'none';
            }
        });
    }
    
    draw();
}

function stopVisualizer() {
    if (visualizerFrame) cancelAnimationFrame(visualizerFrame);
    if (audioContext) audioContext.close();
}

// Initialize status on page load
window.addEventListener('DOMContentLoaded', () => {
    updateStatus();
    populateAudioSources();
});

let vadInterval;
function startVADStats() {
    vadInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/status`);
            const data = await response.json();
            if (data.cpu_usage !== undefined) {
                document.getElementById('vad-status').textContent = `Active (CPU: ${data.cpu_usage}%)`;
            }
        } catch (e) { console.error(e); }
    }, 1000);
}

function stopVADStats() {
    if (vadInterval) clearInterval(vadInterval);
}

function saveTranscript() {
    const text = document.getElementById('transcript-text').textContent;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcript_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function addToRecentSTT(text, language) {
    const list = document.getElementById('recent-stt-list');
    const emptyState = list.querySelector('.empty-state');
    
    if (emptyState) {
        list.innerHTML = '';
    }
    
    const item = document.createElement('div');
    item.className = 'history-item';
    item.style.display = 'flex';
    item.style.justifyContent = 'space-between';
    item.style.alignItems = 'center';
    item.style.padding = '0.75rem';
    item.style.background = 'rgba(255,255,255,0.05)';
    item.style.borderRadius = '8px';
    item.style.marginBottom = '0.5rem';
    
    const preview = text.length > 50 ? text.substring(0, 50) + '...' : text;
    
    item.innerHTML = `
        <div style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-right: 1rem;">
            <i class="fas fa-quote-left" style="color: var(--secondary-color); margin-right: 0.5rem;"></i>
            ${preview}
        </div>
        <div style="font-size: 0.8rem; color: var(--text-secondary); background: rgba(255,255,255,0.1); padding: 0.2rem 0.5rem; border-radius: 4px;">
            ${language.toUpperCase()}
        </div>
    `;
    
    list.insertBefore(item, list.firstChild);
    
    // Limit to 5 items
    if (list.children.length > 5) {
        list.removeChild(list.lastChild);
    }
}

