// Pipeline Builder Logic

const pipelineState = {
    blocks: [],
    isRunning: false
};

document.addEventListener('DOMContentLoaded', () => {
    initializeDragAndDrop();
});

function initializeDragAndDrop() {
    const draggables = document.querySelectorAll('.draggable-block');
    const dropzone = document.getElementById('pipeline-dropzone');

    draggables.forEach(draggable => {
        // Desktop Drag
        draggable.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', draggable.dataset.type);
            e.dataTransfer.effectAllowed = 'copy';
        });
        
        // Mobile Click/Tap
        draggable.addEventListener('click', (e) => {
            // Only trigger if it's a touch device or small screen, or just always allow click to add
            // Always allowing click to add is more accessible
            const type = draggable.dataset.type;
            if (type) {
                addBlock(type);
            }
        });
    });

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('drag-over');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('drag-over');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('drag-over');
        const type = e.dataTransfer.getData('text/plain');
        if (type) {
            addBlock(type);
        }
    });
}

function addBlock(type) {
    const dropzone = document.getElementById('pipeline-dropzone');
    const placeholder = dropzone.querySelector('.placeholder-text');
    if (placeholder) placeholder.style.display = 'none';

    const blockId = Date.now();
    const blockConfig = getBlockConfig(type);
    
    const blockEl = document.createElement('div');
    blockEl.className = 'pipeline-block';
    blockEl.id = `block-${blockId}`;
    blockEl.dataset.id = blockId;
    blockEl.dataset.type = type;
    
    blockEl.innerHTML = `
        <div class="block-content">
            <div class="block-icon">
                <i class="${blockConfig.icon}"></i>
            </div>
            <div class="block-info">
                <h4>${blockConfig.title}</h4>
                <p>${blockConfig.description}</p>
            </div>
        </div>
        <div class="block-actions">
            <button class="block-btn" onclick="toggleConfig(${blockId})">
                <i class="fas fa-cog"></i>
            </button>
            <button class="block-btn" onclick="removeBlock(${blockId})">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="block-config" id="config-${blockId}">
            ${generateConfigHTML(type, blockId)}
        </div>
    `;

    // Add connector if not the first block
    if (pipelineState.blocks.length > 0) {
        const connector = document.createElement('div');
        connector.className = 'connector';
        connector.innerHTML = '<i class="fas fa-arrow-down"></i>';
        dropzone.appendChild(connector);
    }

    dropzone.appendChild(blockEl);
    
    pipelineState.blocks.push({
        id: blockId,
        type: type,
        config: {},
        element: blockEl
    });

    log(`Added block: ${blockConfig.title}`, 'info');
    
    // Scroll to end
    setTimeout(() => {
        dropzone.scrollTop = dropzone.scrollHeight;
    }, 100);
}

function getBlockConfig(type) {
    const configs = {
        'input-mic': { title: 'Microphone', icon: 'fas fa-microphone', description: 'Record audio from microphone' },
        'input-file': { title: 'Audio File', icon: 'fas fa-file-audio', description: 'Upload an audio file' },
        'input-text': { title: 'Text Input', icon: 'fas fa-keyboard', description: 'Enter text manually' },
        'stt': { title: 'Speech to Text', icon: 'fas fa-language', description: 'Convert audio to text (Whisper)' },
        'llm': { title: 'LLM Chat', icon: 'fas fa-brain', description: 'Process text with AI' },
        'tts': { title: 'Text to Speech', icon: 'fas fa-volume-up', description: 'Convert text to audio' },
        'output-audio': { title: 'Audio Player', icon: 'fas fa-headphones', description: 'Play generated audio' },
        'output-text': { title: 'Text Display', icon: 'fas fa-file-alt', description: 'Show text output' }
    };
    return configs[type] || { title: 'Unknown', icon: 'fas fa-question', description: 'Unknown block' };
}

function generateConfigHTML(type, blockId) {
    switch(type) {
        case 'input-text':
            return `<textarea class="form-control" id="input-${blockId}" placeholder="Enter text here..." onchange="updateBlockConfig(${blockId}, 'text', this.value)"></textarea>`;
        case 'input-file':
            return `
                <button class="btn btn-secondary btn-sm" onclick="triggerFileUpload(${blockId})">Select File</button>
                <span id="filename-${blockId}" style="margin-left: 10px; font-size: 0.8rem; color: var(--text-secondary)">No file selected</span>
            `;
        case 'llm':
            return `
                <select class="form-control" onchange="updateBlockConfig(${blockId}, 'provider', this.value)">
                    <option value="ollama">Ollama</option>
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                </select>
            `;
        default:
            return '<p style="font-size: 0.8rem; color: var(--text-secondary)">No configuration needed</p>';
    }
}

function toggleConfig(blockId) {
    const block = document.getElementById(`block-${blockId}`);
    block.classList.toggle('expanded');
}

function removeBlock(blockId) {
    const index = pipelineState.blocks.findIndex(b => b.id === blockId);
    if (index === -1) return;

    // Remove block element
    const block = document.getElementById(`block-${blockId}`);
    block.remove();

    // Remove connector (previous sibling if it exists and is a connector)
    // This logic is simplified; a robust implementation would track connectors better
    // For now, we'll just rebuild the UI or accept minor visual glitches on delete
    // Better approach: Clear and Re-render or just reload page for MVP
    
    pipelineState.blocks.splice(index, 1);
    
    // Re-render to fix connectors
    // For this demo, we'll just reload the page content logic if needed, 
    // but let's just hide the connector for now if we can find it.
    // A simple way is to clear the dropzone and re-render all blocks from state.
    reRenderPipeline();
}

function reRenderPipeline() {
    const dropzone = document.getElementById('pipeline-dropzone');
    dropzone.innerHTML = '<div class="placeholder-text" style="display: ' + (pipelineState.blocks.length ? 'none' : 'block') + '">Drag blocks here to build your pipeline</div>';
    
    pipelineState.blocks.forEach((block, index) => {
        if (index > 0) {
            const connector = document.createElement('div');
            connector.className = 'connector';
            connector.innerHTML = '<i class="fas fa-arrow-down"></i>';
            dropzone.appendChild(connector);
        }
        dropzone.appendChild(block.element);
    });
}

function updateBlockConfig(blockId, key, value) {
    const block = pipelineState.blocks.find(b => b.id === blockId);
    if (block) {
        block.config[key] = value;
    }
}

function triggerFileUpload(blockId) {
    const input = document.getElementById('hidden-file-input');
    input.onchange = (e) => {
        if (e.target.files[0]) {
            const file = e.target.files[0];
            updateBlockConfig(blockId, 'file', file);
            document.getElementById(`filename-${blockId}`).textContent = file.name;
        }
    };
    input.click();
}

function clearPipeline() {
    pipelineState.blocks = [];
    reRenderPipeline();
    log('Pipeline cleared', 'info');
}

function log(message, type = 'info') {
    const logContainer = document.getElementById('execution-log');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

async function executePipeline() {
    if (pipelineState.blocks.length === 0) {
        log('Pipeline is empty!', 'error');
        return;
    }

    if (pipelineState.isRunning) return;
    pipelineState.isRunning = true;
    
    const statusBadge = document.getElementById('pipeline-status');
    statusBadge.textContent = 'Running...';
    statusBadge.className = 'status-badge warning'; // Assuming warning style is yellow/orange

    log('Starting pipeline execution...', 'info');

    let currentData = null; // Data passed between blocks

    try {
        for (const block of pipelineState.blocks) {
            log(`Executing block: ${getBlockConfig(block.type).title}...`, 'info');
            
            // Highlight current block
            block.element.style.borderColor = 'var(--success-color)';
            
            currentData = await processBlock(block, currentData);
            
            // Reset border
            setTimeout(() => {
                block.element.style.borderColor = 'var(--primary-color)';
            }, 1000);
        }
        log('Pipeline execution completed successfully!', 'success');
        statusBadge.textContent = 'Completed';
        statusBadge.className = 'status-badge success';
    } catch (error) {
        log(`Pipeline error: ${error.message}`, 'error');
        statusBadge.textContent = 'Error';
        statusBadge.className = 'status-badge error';
    } finally {
        pipelineState.isRunning = false;
    }
}

async function processBlock(block, inputData) {
    switch (block.type) {
        case 'input-text':
            if (!block.config.text) throw new Error('No text provided in input block');
            return { type: 'text', content: block.config.text };
            
        case 'input-file':
            if (!block.config.file) throw new Error('No file selected');
            return { type: 'audio', content: block.config.file };
            
        case 'stt':
            if (!inputData || inputData.type !== 'audio') throw new Error('STT requires audio input');
            const formData = new FormData();
            formData.append('file', inputData.content);
            
            const sttRes = await fetch('/api/stt/transcribe', {
                method: 'POST',
                body: formData
            });
            const sttData = await sttRes.json();
            if (!sttData.success) throw new Error(sttData.message);
            log(`Transcription: "${sttData.text.substring(0, 50)}..."`, 'success');
            return { type: 'text', content: sttData.text };
            
        case 'llm':
            if (!inputData || inputData.type !== 'text') throw new Error('LLM requires text input');
            const llmRes = await fetch('/api/chat/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: inputData.content,
                    provider: block.config.provider || 'ollama'
                })
            });
            const llmData = await llmRes.json();
            if (!llmData.success) throw new Error(llmData.message);
            log(`AI Response: "${llmData.response.substring(0, 50)}..."`, 'success');
            return { type: 'text', content: llmData.response };
            
        case 'tts':
            if (!inputData || inputData.type !== 'text') throw new Error('TTS requires text input');
            const ttsRes = await fetch('/api/tts/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: inputData.content })
            });
            const ttsData = await ttsRes.json();
            if (!ttsData.success) throw new Error(ttsData.message);
            return { type: 'audio_url', content: ttsData.url };
            
        case 'output-text':
            if (!inputData || inputData.type !== 'text') throw new Error('Text Output requires text input');
            // In a real app, we might update the DOM of this block to show the text
            log(`Output: ${inputData.content}`, 'success');
            return inputData;
            
        case 'output-audio':
            if (!inputData || inputData.type !== 'audio_url') throw new Error('Audio Output requires audio URL input');
            const audio = new Audio(inputData.content);
            audio.play();
            log('Playing audio...', 'success');
            return inputData;
            
        default:
            return inputData;
    }
}

