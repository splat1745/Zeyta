// TTS Page Functions

let currentReferenceFile = null;
let cloneMediaRecorder = null;
let cloneAudioChunks = [];
let cloneAudioBlob = null;

async function initializeTTS() {
    const backendSelect = document.getElementById('tts-backend');
    const deviceSelect = document.getElementById('tts-device');
    const reinstallSelect = document.getElementById('tts-reinstall');

    const backend = backendSelect ? backendSelect.value : undefined;
    const device = deviceSelect ? deviceSelect.value : 'auto';
    const allowReinstall = reinstallSelect ? reinstallSelect.value === 'true' : undefined;

    await initializeModel('tts', {
        device: device,
        backend: backend,
        allow_reinstall: allowReinstall
    });
}

async function handleReferenceUpload(input) {
    const file = input.files[0];
    if (!file) return;
    
    showLoading('Uploading reference audio...');
    
    try {
        const data = await uploadFile(file, '/api/upload/reference');
        hideLoading();
        
        if (data.success) {
            currentReferenceFile = data.filename;
            
            // Update UI
            document.querySelector('#ref-upload-area .upload-placeholder').style.display = 'none';
            document.querySelector('#ref-upload-area .upload-success').style.display = 'block';
            document.getElementById('ref-filename').textContent = data.filename;
            
            showNotification('Reference audio uploaded successfully', 'success');
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        hideLoading();
        showNotification(error.message, 'error');
    }
}

function clearReference() {
    currentReferenceFile = null;
    document.getElementById('ref-audio').value = '';
    document.querySelector('#ref-upload-area .upload-placeholder').style.display = 'block';
    document.querySelector('#ref-upload-area .upload-success').style.display = 'none';
    document.getElementById('ref-filename').textContent = '';
}

// Voice Cloning Modal Functions
function openCloneModal() {
    document.getElementById('clone-modal').classList.add('active');
}

function closeCloneModal() {
    document.getElementById('clone-modal').classList.remove('active');
    stopCloneRecording(); // Ensure recording stops if modal closed
}

async function startCloneRecording() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showNotification('Microphone access not supported', 'error');
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        cloneMediaRecorder = new MediaRecorder(stream);
        cloneAudioChunks = [];

        cloneMediaRecorder.ondataavailable = (e) => {
            cloneAudioChunks.push(e.data);
        };

        cloneMediaRecorder.onstop = () => {
            cloneAudioBlob = new Blob(cloneAudioChunks, { type: 'audio/wav' });
            document.getElementById('use-recording-btn').disabled = false;
            
            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };

        cloneMediaRecorder.start();
        
        // Update UI
        document.getElementById('start-record-btn').disabled = true;
        document.getElementById('stop-record-btn').disabled = false;
        document.getElementById('use-recording-btn').disabled = true;
        
        // Start visualizer
        startVisualizer(stream, 'clone-visualizer');
        
    } catch (err) {
        showNotification('Failed to access microphone: ' + err.message, 'error');
    }
}

function stopCloneRecording() {
    if (cloneMediaRecorder && cloneMediaRecorder.state !== 'inactive') {
        cloneMediaRecorder.stop();
        document.getElementById('start-record-btn').disabled = false;
        document.getElementById('stop-record-btn').disabled = true;
        stopVisualizer();
    }
}

async function useCloneRecording() {
    if (!cloneAudioBlob) return;
    
    const file = new File([cloneAudioBlob], "voice_sample.wav", { type: "audio/wav" });
    
    // Simulate file upload
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    document.getElementById('ref-audio').files = dataTransfer.files;
    
    // Trigger upload handler
    await handleReferenceUpload(document.getElementById('ref-audio'));
    
    closeCloneModal();
}

// Visualizer Logic
let audioContext, analyser, dataArray, visualizerFrame;

function startVisualizer(stream, elementId) {
    const container = document.getElementById(elementId);
    container.innerHTML = ''; // Clear previous
    
    // Create bars
    for (let i = 0; i < 20; i++) {
        const bar = document.createElement('div');
        bar.className = 'visualizer-bar';
        bar.style.height = '5px';
        container.appendChild(bar);
    }
    
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioContext.createMediaStreamSource(stream);
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 64;
    source.connect(analyser);
    
    const bufferLength = analyser.frequencyBinCount;
    dataArray = new Uint8Array(bufferLength);
    
    const bars = container.querySelectorAll('.visualizer-bar');
    
    function draw() {
        visualizerFrame = requestAnimationFrame(draw);
        analyser.getByteFrequencyData(dataArray);
        
        bars.forEach((bar, index) => {
            const value = dataArray[index] || 0;
            const height = Math.max(5, (value / 255) * 100);
            bar.style.height = `${height}%`;
        });
    }
    
    draw();
}

function stopVisualizer() {
    if (visualizerFrame) cancelAnimationFrame(visualizerFrame);
    if (audioContext) audioContext.close();
}

async function generateTTS() {
    const text = document.getElementById('tts-text').value.trim();
    
    if (!text) {
        showNotification('Please enter text to synthesize', 'error');
        return;
    }
    
    // Check if TTS is loaded
    const status = await updateStatus();
    if (!status || !status.tts) {
        showNotification('Please initialize TTS model first', 'error');
        return;
    }
    
    showLoading('Generating speech...');
    const startTime = performance.now();
    
    try {
        const requestData = {
            text: text,
            temperature: parseFloat(document.getElementById('temperature').value),
            exaggeration: parseFloat(document.getElementById('exaggeration').value),
            cfg_weight: parseFloat(document.getElementById('cfg-weight').value),
            format: document.getElementById('tts-format').value
        };
        
        if (currentReferenceFile) {
            requestData.reference_audio = currentReferenceFile;
        }
        
        const response = await fetch(`${API_BASE}/api/tts/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        const endTime = performance.now();
        const latency = Math.round(endTime - startTime);
        
        hideLoading();
        
        if (data.success) {
            // Show output panel
            const outputPanel = document.getElementById('output-panel');
            outputPanel.style.display = 'block';
            
            // Set audio source
            const audioPlayer = document.getElementById('audio-player');
            audioPlayer.src = data.url;
            
            // Set download link
            const downloadLink = document.getElementById('download-link');
            downloadLink.href = data.url;
            downloadLink.download = data.filename;
            
            // Update stats
            document.getElementById('latency-val').textContent = `${latency}ms`;
            // Estimate RTF (Real Time Factor) - simplified
            const duration = audioPlayer.duration || (text.length / 15); // Rough estimate if duration not ready
            const rtf = (latency / 1000) / duration;
            document.getElementById('rtf-val').textContent = rtf.toFixed(2) + 'x';
            
            renderLatencyGraph(latency);
            
            showNotification('Speech generated successfully!', 'success');
            
            // Scroll to output
            outputPanel.scrollIntoView({ behavior: 'smooth' });
            
            // Add to recent history
            addToRecentTTS(text, data.filename, data.url);
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        hideLoading();
        showNotification(`Generation failed: ${error.message}`, 'error');
    }
}

// Simple Latency Graph
let latencyHistory = [];
function renderLatencyGraph(newLatency) {
    latencyHistory.push(newLatency);
    if (latencyHistory.length > 20) latencyHistory.shift();
    
    const container = document.getElementById('latency-graph');
    container.innerHTML = '';
    
    const max = Math.max(...latencyHistory, 1000);
    const width = container.clientWidth;
    const height = container.clientHeight;
    const step = width / (latencyHistory.length - 1 || 1);
    
    let pathD = `M 0 ${height}`;
    
    latencyHistory.forEach((val, i) => {
        const x = i * step;
        const y = height - ((val / max) * height * 0.8); // 80% height max
        pathD += ` L ${x} ${y}`;
    });
    
    pathD += ` L ${width} ${height} Z`; // Close path
    
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "100%");
    
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", pathD);
    path.setAttribute("fill", "rgba(0, 255, 157, 0.2)");
    path.setAttribute("stroke", "var(--success-color)");
    path.setAttribute("stroke-width", "2");
    
    svg.appendChild(path);
    container.appendChild(svg);
}

// Add to Recent TTS
function addToRecentTTS(text, filename, url) {
    const list = document.getElementById('recent-tts-list');
    if (list.textContent.includes('No recent generations')) {
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
    
    item.innerHTML = `
        <div style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-right: 1rem;">
            <i class="fas fa-comment-alt" style="color: var(--primary-color); margin-right: 0.5rem;"></i>
            ${text}
        </div>
        <div style="display: flex; gap: 0.5rem;">
            <button class="btn btn-sm btn-secondary" onclick="document.getElementById('audio-player').src='${url}'; document.getElementById('audio-player').play();">
                <i class="fas fa-play"></i>
            </button>
            <a href="${url}" download="${filename}" class="btn btn-sm btn-secondary">
                <i class="fas fa-download"></i>
            </a>
        </div>
    `;
    
    list.insertBefore(item, list.firstChild);
    
    // Limit to 5 items
    if (list.children.length > 5) {
        list.removeChild(list.lastChild);
    }
}

// Initialize status on page load
window.addEventListener('DOMContentLoaded', () => {
    updateStatus();
});
