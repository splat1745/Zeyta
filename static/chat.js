// Chat Page Functions

let sessions = []; // { id: string, title: string, history: [], personality: string, date: string }
let currentSessionId = null;
let chatHistory = [];
let currentPersonality = 'helpful_assistant';
let currentChatTitle = null;

const personalities = {
    'helpful_assistant': {
        name: 'Helpful Assistant',
        system_prompt: 'You are a helpful AI assistant. Answer questions clearly and concisely.'
    },
    'coding_expert': {
        name: 'Coding Expert',
        system_prompt: 'You are an expert programmer. Provide code examples and technical explanations.'
    },
    'creative_writer': {
        name: 'Creative Writer',
        system_prompt: 'You are a creative writer. Use evocative language and storytelling techniques.'
    },
    'concise_bot': {
        name: 'Concise Bot',
        system_prompt: 'You are a concise bot. Answer in as few words as possible.'
    }
};

function showChatSettings() {
    document.getElementById('chat-settings-modal').style.display = 'flex';
}

function closeChatSettings() {
    document.getElementById('chat-settings-modal').style.display = 'none';
}

async function initializeChat() {
    const model = document.getElementById('model-select').value;
    const quant = document.getElementById('quant-select').value;
    
    closeChatSettings();
    
    await initializeModel('llm', {
        model_path: model,
        quantization: quant
    });
}

function changePersonality() {
    const select = document.getElementById('personality-select');
    const newPersonality = select.value;
    
    if (!personalities[newPersonality]) {
        console.error(`Personality ${newPersonality} not found`);
        return;
    }
    
    currentPersonality = newPersonality;
    
    // Add system message to chat
    const personality = personalities[currentPersonality];
    addMessageToChat('system', `Switched to ${personality.name} personality.`);
    
    // In a real app, we would send this to the backend
    console.log(`Switched personality to: ${currentPersonality}`);
}

function togglePlugin(plugin, enabled) {
    console.log(`Plugin ${plugin} ${enabled ? 'enabled' : 'disabled'}`);
    showNotification(`${plugin.charAt(0).toUpperCase() + plugin.slice(1)} plugin ${enabled ? 'enabled' : 'disabled'}`, 'info');
}

function exportChat() {
    if (chatHistory.length === 0) {
        showNotification('No chat history to export', 'warning');
        return;
    }
    
    const exportData = {
        title: currentChatTitle || 'Untitled Chat',
        date: new Date().toISOString(),
        personality: currentPersonality,
        history: chatHistory
    };
    
    const json = JSON.stringify(exportData, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat_export_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Chat history exported as JSON', 'success');
}

async function newChat() {
    if (chatHistory.length > 0) {
        // Save current session before clearing
        saveCurrentSession();
        
        // Only ask if there's substantial history
        if (chatHistory.length > 2 && !confirm('Start a new chat?')) {
            return;
        }
    }
    
    try {
        const response = await fetch('/api/chat/clear', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            // Reset state
            currentSessionId = null;
            chatHistory = [];
            currentChatTitle = null;
            
            // Create new session immediately
            saveCurrentSession();
            
            document.getElementById('chat-messages').innerHTML = `
                <div class="message assistant-message">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-header">Zeyta AI</div>
                        <div class="message-text">Hello! I'm Zeyta, your AI assistant. How can I help you today?</div>
                    </div>
                </div>
            `;
            
            updateHistorySidebar();
            showNotification('New chat started', 'info');
        } else {
            showNotification('Failed to clear chat context: ' + data.message, 'error');
        }
    } catch (error) {
        showNotification('Error starting new chat: ' + error.message, 'error');
    }
}

function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        document.getElementById('chat-messages').innerHTML = `
            <div class="message system-message">
                <div class="message-content">
                    Chat history cleared. Start a new conversation.
                </div>
            </div>
        `;
        chatHistory = [];
        currentChatTitle = null;
        showNotification('Chat cleared', 'info');
    }
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Check if LLM is loaded
    const status = await updateStatus();
    if (!status || !status.llm) {
        showNotification('Please initialize LLM model first', 'error');
        return;
    }
    
    // Add user message
    addMessageToChat('user', message);
    input.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Get active plugins
    const plugins = [];
    if (document.getElementById('plugin-calc').checked) plugins.push('calc');
    if (document.getElementById('plugin-vision').checked) plugins.push('vision');
    
    try {
        const response = await fetch('/api/chat/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: message,
                history: chatHistory,
                system_prompt: personalities[currentPersonality].system_prompt,
                plugins: plugins
            })
        });
        
        const data = await response.json();
        
        hideTypingIndicator();
        
        if (data.success) {
            addMessageToChat('assistant', data.response, data.plugins_used);
            
            // Generate title if this is the first exchange (2 messages: user + assistant)
            // Relaxed condition: if no title yet and we have at least 2 messages
            if (!currentChatTitle && chatHistory.length >= 2) {
                generateChatTitle();
            }
        } else {
            showNotification(data.message, 'error');
            addMessageToChat('system', 'Error: ' + data.message);
        }
    } catch (error) {
        hideTypingIndicator();
        showNotification(error.message, 'error');
        addMessageToChat('system', 'Error: ' + error.message);
    }
}

function addMessageToChat(role, content, plugins = []) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    
    messageDiv.className = `message ${role}-message`;
    
    let icon = 'user';
    if (role === 'assistant') icon = 'robot';
    if (role === 'system') icon = 'info-circle';
    
    // Format content using marked.js if available, otherwise fallback to simple parsing
    let formattedContent;
    if (typeof marked !== 'undefined') {
        // Configure marked to handle line breaks correctly
        marked.setOptions({
            breaks: true,
            gfm: true
        });
        formattedContent = marked.parse(content);
    } else {
        formattedContent = content
            .replace(/\n/g, '<br>')
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>');
    }
    
    // Render plugins if any
    let pluginsHtml = '';
    if (plugins && plugins.length > 0) {
        pluginsHtml = `
            <div class="message-footer">
                ${plugins.map(p => `
                    <div class="plugin-badge">
                        <i class="fas fa-plug"></i> ${p}
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-${icon}"></i>
        </div>
        <div class="message-content">
            ${formattedContent}
            ${pluginsHtml}
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Add to history (except system messages)
    if (role !== 'system') {
        chatHistory.push({ role, content, plugins });
        updateHistorySidebar();
    }
}

function updateHistorySidebar() {
    const list = document.getElementById('history-list');
    if (!list) return;
    
    list.innerHTML = '';
    
    // If no sessions, create one
    if (sessions.length === 0 && chatHistory.length > 0) {
        saveCurrentSession();
    }
    
    // Render sessions
    sessions.forEach(session => {
        const item = document.createElement('div');
        item.className = `history-item ${session.id === currentSessionId ? 'active' : ''}`;
        item.onclick = () => loadSession(session.id);
        
        const date = new Date(session.date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        item.innerHTML = `
            <div class="history-title">${session.title || 'New Chat'}</div>
            <div class="history-date">${date}</div>
        `;
        list.appendChild(item);
    });
}

function saveCurrentSession() {
    if (!currentSessionId) {
        currentSessionId = Date.now().toString();
        sessions.unshift({
            id: currentSessionId,
            title: currentChatTitle || 'New Chat',
            history: [...chatHistory],
            personality: currentPersonality,
            date: new Date().toISOString()
        });
    } else {
        const session = sessions.find(s => s.id === currentSessionId);
        if (session) {
            session.history = [...chatHistory];
            session.title = currentChatTitle || session.title;
            session.personality = currentPersonality;
        }
    }
}

function loadSession(id) {
    if (currentSessionId === id) return;
    
    // Save current before switching
    saveCurrentSession();
    
    const session = sessions.find(s => s.id === id);
    if (session) {
        currentSessionId = session.id;
        chatHistory = [...session.history];
        currentChatTitle = session.title;
        currentPersonality = session.personality;
        
        // Update UI
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = '';
        
        // Re-render messages
        if (chatHistory.length === 0) {
             chatMessages.innerHTML = `
                <div class="message assistant-message">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-header">Zeyta AI</div>
                        <div class="message-text">Hello! I'm Zeyta, your AI assistant. How can I help you today?</div>
                    </div>
                </div>
            `;
        } else {
            chatHistory.forEach(msg => {
                // Manually add to DOM without pushing to history again
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${msg.role}-message`;
                
                let icon = 'user';
                if (msg.role === 'assistant') icon = 'robot';
                if (msg.role === 'system') icon = 'info-circle';
                
                let formattedContent;
                if (typeof marked !== 'undefined') {
                    formattedContent = marked.parse(msg.content);
                } else {
                    formattedContent = msg.content;
                }
                
                // Render plugins if any
                let pluginsHtml = '';
                if (msg.plugins && msg.plugins.length > 0) {
                    pluginsHtml = `
                        <div class="message-footer">
                            ${msg.plugins.map(p => `
                                <div class="plugin-badge">
                                    <i class="fas fa-plug"></i> ${p}
                                </div>
                            `).join('')}
                        </div>
                    `;
                }
                
                messageDiv.innerHTML = `
                    <div class="message-avatar">
                        <i class="fas fa-${icon}"></i>
                    </div>
                    <div class="message-content">
                        ${formattedContent}
                        ${pluginsHtml}
                    </div>
                `;
                chatMessages.appendChild(messageDiv);
            });
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        updateHistorySidebar();
        
        // Sync backend context
        // In a real app, we'd send the full history to backend here
        // For now, we just clear backend and let next message send full history
        fetch('/api/chat/clear', { method: 'POST' });
    }
}

async function generateChatTitle() {
    try {
        // Don't show typing indicator for this background task
        const response = await fetch('/api/chat/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: "Generate a short, relevant title (max 5 words) for this conversation based on the history. Do not use quotes. Do not say 'Requesting a title'. Just the title.",
                history: chatHistory,
                system_prompt: "You are a helpful assistant. You are generating a title for a chat log.",
                temporary: true
            })
        });
        
        const data = await response.json();
        if (data.success) {
            currentChatTitle = data.response.replace(/^["']|["']$/g, '').trim();
            saveCurrentSession(); // Save title to session
            updateHistorySidebar();
        }
    } catch (error) {
        console.error('Failed to generate title:', error);
    }
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'message assistant-message';
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

function updateModelList() {
    const provider = document.getElementById('llm-provider').value;
    const modelSelect = document.getElementById('llm-model');
    
    modelSelect.innerHTML = '<option value="" disabled selected>Loading...</option>';
    modelSelect.disabled = true;
    
    fetch(`${API_BASE}/api/llm/models?provider=${provider}`)
        .then(response => response.json())
        .then(data => {
            modelSelect.innerHTML = '<option value="" disabled selected>Select Model</option>';
            if (data.success && data.models.length > 0) {
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model;
                    modelSelect.appendChild(option);
                });
                modelSelect.disabled = false;
                
                // Auto-select first model if available
                if (data.models.length > 0) {
                    modelSelect.value = data.models[0];
                    checkModelCapabilities(); // Check capabilities of initial model
                }
                
                // Add change listener
                modelSelect.onchange = checkModelCapabilities;
            } else {
                const option = document.createElement('option');
                option.textContent = 'No models found';
                modelSelect.appendChild(option);
            }
        })
        .catch(error => {
            console.error('Error fetching models:', error);
            modelSelect.innerHTML = '<option value="" disabled selected>Error loading models</option>';
        });
}

function checkModelCapabilities() {
    const modelSelect = document.getElementById('llm-model');
    if (!modelSelect || !modelSelect.value) return;
    
    const model = modelSelect.value.toLowerCase();
    const visionCheckbox = document.getElementById('plugin-vision');
    
    if (!visionCheckbox) return;
    
    const visionLabel = visionCheckbox.parentElement;
    
    // Heuristic: Check for vision-related keywords
    // This is a simple client-side check. Ideally, the backend would provide capabilities.
    const isVisionCapable = model.includes('vision') || 
                           model.includes('llava') || 
                           model.includes('bakllava') ||
                           model.includes('moondream') ||
                           model.includes('minicpm');
                           
    if (isVisionCapable) {
        visionCheckbox.disabled = false;
        visionLabel.title = "Enable Vision Plugin";
        visionLabel.style.opacity = "1";
        visionLabel.style.cursor = "pointer";
    } else {
        visionCheckbox.disabled = true;
        visionCheckbox.checked = false;
        visionLabel.title = "This model does not support vision capabilities";
        visionLabel.style.opacity = "0.5";
        visionLabel.style.cursor = "not-allowed";
        
        // Notify user if they had it checked
        if (visionCheckbox.checked) {
            showNotification('Vision plugin disabled (model not supported)', 'warning');
        }
    }
}

function toggleSidebar() {
    const sidebar = document.querySelector('.chat-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (sidebar.classList.contains('active')) {
        sidebar.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
    } else {
        sidebar.classList.add('active');
        if (overlay) overlay.classList.add('active');
    }
}

function initializeLLM() {
    const provider = document.getElementById('llm-provider').value;
    const model = document.getElementById('llm-model').value;
    
    if (!model) {
        showNotification('Please select a model first', 'error');
        return;
    }
    
    initializeModel('llm', {
        provider: provider,
        model: model
    });
}

function handleChatKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

// Initialize status on page load
window.addEventListener('DOMContentLoaded', () => {
    updateStatus();
    updateModelList(); // Fetch initial models
});

