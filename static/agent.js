// Agent Mode JavaScript
let agentInitialized = false;
let currentModel = null;
let updateInterval = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    updateStatus();
    
    // Start status polling
    updateInterval = setInterval(updateStatus, 3000);
});

function setupEventListeners() {
    // Setup buttons
    document.getElementById('init-btn').addEventListener('click', initializeAgent);
    document.getElementById('refresh-models-btn').addEventListener('click', refreshModels);
    document.getElementById('model-select').addEventListener('change', selectModel);
    document.getElementById('save-permissions-btn').addEventListener('click', savePermissions);
    document.getElementById('analyze-screen-btn').addEventListener('click', analyzeScreen);
    document.getElementById('execute-task-btn').addEventListener('click', executeTask);
    document.getElementById('send-message-btn').addEventListener('click', sendMessage);
    document.getElementById('clear-chat-btn').addEventListener('click', clearChat);
    document.getElementById('emergency-stop-btn').addEventListener('click', emergencyStop);
    
    // Enter key in chat
    document.getElementById('agent-chat-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Quick actions
    document.querySelectorAll('.quick-action').forEach(btn => {
        btn.addEventListener('click', () => executeQuickAction(btn));
    });
    
    // Example tasks
    document.querySelectorAll('.example-task').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('task-input').value = btn.dataset.task;
            executeTask();
        });
    });
    
    // Permission checkboxes
    document.querySelectorAll('.permission-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            document.getElementById('save-permissions-btn').disabled = false;
        });
    });
}

async function updateStatus() {
    try {
        const response = await fetch('/api/agent/status');
        const data = await response.json();
        
        // Update status badges
        const agentStatus = document.getElementById('agent-status');
        const ollamaStatus = document.getElementById('ollama-status');
        const modelStatus = document.getElementById('model-status');
        const screenInfo = document.getElementById('screen-info');
        
        if (data.initialized) {
            agentStatus.textContent = 'Initialized';
            agentStatus.className = 'status-badge badge-success';
            agentInitialized = true;
        } else {
            agentStatus.textContent = 'Not Initialized';
            agentStatus.className = 'status-badge badge-secondary';
            agentInitialized = false;
        }
        
        if (data.ollama_connected) {
            ollamaStatus.textContent = 'Connected';
            ollamaStatus.className = 'status-badge badge-success';
            
            // Update models dropdown
            const modelSelect = document.getElementById('model-select');
            const currentSelection = modelSelect.value;
            modelSelect.innerHTML = '<option value="">Select a model...</option>';
            
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
            
            // Restore selection or set current model
            if (data.current_model) {
                modelSelect.value = data.current_model;
                currentModel = data.current_model;
            } else if (currentSelection) {
                modelSelect.value = currentSelection;
            }
            
            // Enable model selection
            modelSelect.disabled = false;
        } else {
            ollamaStatus.textContent = 'Disconnected';
            ollamaStatus.className = 'status-badge badge-danger';
            document.getElementById('model-select').disabled = true;
        }
        
        modelStatus.textContent = data.current_model || 'None';
        
        if (data.screen_info) {
            screenInfo.textContent = `${data.screen_info.width}x${data.screen_info.height}`;
        }
        
        // Update permissions
        if (data.permissions) {
            document.getElementById('perm-mouse').checked = data.permissions.mouse_click;
            document.getElementById('perm-keyboard').checked = data.permissions.keyboard_type;
            document.getElementById('perm-files').checked = data.permissions.file_operations;
            document.getElementById('perm-system').checked = data.permissions.system_commands;
        }
        
        // Update button states based on requirements
        updateButtonStates();
        
    } catch (error) {
        console.error('Status update failed:', error);
    }
}

async function initializeAgent() {
    const initBtn = document.getElementById('init-btn');
    const originalText = initBtn.innerHTML;
    
    initBtn.disabled = true;
    initBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Initializing...';
    
    try {
        // Show detailed progress
        showNotification('Checking Ollama connection...', 'info');
        
        const response = await fetch('/api/agent/initialize', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Agent initialized! Now select an Ollama model.', 'success');
            agentInitialized = true;
            initBtn.innerHTML = '<i class="fas fa-check"></i> Initialized';
            initBtn.className = 'btn btn-success';
            
            // Wait a moment then update status
            setTimeout(() => {
                updateStatus();
            }, 500);
        } else {
            showNotification(data.message || 'Initialization failed. Is Ollama running?', 'error');
            initBtn.disabled = false;
            initBtn.innerHTML = originalText;
        }
    } catch (error) {
        showNotification('Failed to initialize agent: ' + error.message, 'error');
        initBtn.disabled = false;
        initBtn.innerHTML = originalText;
    }
}

async function refreshModels() {
    await updateStatus();
    showNotification('Models refreshed', 'success');
}

async function selectModel() {
    const model = document.getElementById('model-select').value;
    if (!model) {
        currentModel = null;
        updateButtonStates();
        return;
    }
    
    showLoading('Loading model: ' + model + '...');
    
    try {
        const response = await fetch('/api/agent/set-model', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({model: model})
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentModel = model;
            showNotification(`✅ Model loaded: ${model}. Agent is ready!`, 'success');
            updateButtonStates();
        } else {
            showNotification(data.error || 'Failed to set model', 'error');
            document.getElementById('model-select').value = '';
            currentModel = null;
            updateButtonStates();
        }
    } catch (error) {
        showNotification('Failed to set model: ' + error.message, 'error');
        document.getElementById('model-select').value = '';
        currentModel = null;
        updateButtonStates();
    } finally {
        hideLoading();
    }
}

async function savePermissions() {
    const permissions = {
        mouse_click: document.getElementById('perm-mouse').checked,
        keyboard_type: document.getElementById('perm-keyboard').checked,
        file_operations: document.getElementById('perm-files').checked,
        system_commands: document.getElementById('perm-system').checked
    };
    
    try {
        const response = await fetch('/api/agent/set-permissions', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({permissions: permissions})
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Permissions saved', 'success');
            // Don't disable the button, just show success
            // document.getElementById('save-permissions-btn').disabled = true;
            
            // Update local state if needed or force a status update
            updateStatus();
        } else {
            showNotification('Failed to save permissions', 'error');
        }
    } catch (error) {
        showNotification('Failed to save permissions: ' + error.message, 'error');
    }
}

async function analyzeScreen() {
    const prompt = document.getElementById('analysis-prompt').value;
    
    // Show permission prompt
    const proceed = await showPermissionPrompt(
        'Analyze Screen?',
        `Analysis: "${prompt}"`,
        'The agent will capture your current screen and analyze it using AI vision.',
        [
            '📸 Capture current screen',
            '🤖 Analyze with AI vision model',
            '📋 Provide detailed description'
        ]
    );
    
    if (proceed === null) return; // User cancelled
    
    // Start blue glow overlay instead of loading circle
    await fetch('/api/agent/overlay/start', { method: 'POST' });
    await fetch('/api/agent/overlay/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reasoning: '📸 Capturing screen...' })
    });
    
    try {
        await fetch('/api/agent/overlay/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reasoning: '🤔 Analyzing screen with AI...' })
        });
        
        const response = await fetch('/api/agent/analyze-screen', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({prompt: prompt})
        });
        
        const data = await response.json();
        
        if (data.success) {
            await fetch('/api/agent/overlay/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reasoning: '✅ Analysis complete!' })
            });
            
            // Brief delay to show completion
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            const analysisText = document.getElementById('analysis-text');
            analysisText.textContent = data.analysis;
            
            const resultBox = document.getElementById('screen-analysis-result');
            resultBox.style.display = 'block';
            resultBox.scrollIntoView({ behavior: 'smooth' });
            
            if (data.screenshot) {
                const img = document.getElementById('screenshot-img');
                img.src = `/api/agent/screenshots/${data.screenshot}`;
                document.getElementById('screenshot-container').style.display = 'block';
            }
            
            showNotification('✅ Screen analyzed successfully', 'success');
        } else {
            showNotification('❌ ' + (data.error || 'Analysis failed'), 'error');
        }
    } catch (error) {
        showNotification('❌ Analysis failed: ' + error.message, 'error');
    } finally {
        // Stop overlay instead of loading circle
        await fetch('/api/agent/overlay/stop', { method: 'POST' });
    }
}

async function executeTask() {
    const task = document.getElementById('task-input').value.trim();
    if (!task) {
        showNotification('⚠️ Please enter a task description', 'warning');
        return;
    }
    
    // Show permission prompt overlay
    const autoExecute = await showPermissionPrompt(
        'Execute Task Autonomously?',
        `Task: "${task}"`,
        'The agent will analyze your screen and autonomously perform all necessary actions to complete this task.',
        [
            '🔍 Analyze screen at each step',
            '🖱️ Control mouse and keyboard',
            '📋 Execute up to 15 steps automatically'
        ]
    );
    
    if (autoExecute === null) return; // User cancelled
    
    // Start blue glow overlay with reasoning display
    await fetch('/api/agent/overlay/start', { method: 'POST' });
    await fetch('/api/agent/overlay/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            reasoning: `${autoExecute ? '🤖 Starting autonomous execution' : '📋 Planning task'}...\n\nTask: ${task}` 
        })
    });
    
    // Poll for reasoning updates during execution
    const updateInterval = setInterval(async () => {
        try {
            const statusResponse = await fetch('/api/agent/overlay/status');
            // Reasoning is being updated by backend
        } catch (e) {
            // Ignore polling errors
        }
    }, 500);
    
    try {
        const response = await fetch('/api/agent/execute-task', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                task: task,
                auto_execute: autoExecute
            })
        });
        
        clearInterval(updateInterval);
        
        const data = await response.json();
        
        if (data.success) {
            await fetch('/api/agent/overlay/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reasoning: '✅ Task completed successfully!' })
            });
            
            // Brief delay to show completion message
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            const taskResult = document.getElementById('task-result');
            const taskAnalysis = document.getElementById('task-analysis');
            
            // Show execution log with formatting
            let logText = `✅ Task: ${task}\n${'='.repeat(60)}\n\n`;
            
            if (data.execution_log && data.execution_log.length > 0) {
                logText += '📋 Execution Steps:\n';
                data.execution_log.forEach((log, i) => {
                    logText += `  ${i + 1}. ${log}\n`;
                });
                logText += `\n✨ Total steps completed: ${data.steps_completed || 0}`;
            } else {
                logText += '⚠️ No execution steps recorded';
            }
            
            taskAnalysis.textContent = logText;
            taskResult.style.display = 'block';
            taskResult.scrollIntoView({ behavior: 'smooth' });
            
            if (data.requires_confirmation) {
                // Show action plan for confirmation
                const actionsDiv = document.getElementById('task-actions');
                const actionsList = document.getElementById('actions-list');
                
                actionsList.innerHTML = `
                    <div class="action-plan">
                        <p><strong>🎯 Action:</strong> ${data.action_plan.action}</p>
                        <p><strong>💭 Reasoning:</strong> ${data.action_plan.reasoning}</p>
                        <p><strong>⚙️ Parameters:</strong> ${JSON.stringify(data.action_plan.parameters, null, 2)}</p>
                    </div>
                `;
                
                actionsDiv.style.display = 'block';
                showNotification('✅ Action plan ready for confirmation', 'success');
            } else {
                showNotification(data.message || '✅ Task execution complete!', 'success');
            }
        } else {
            await fetch('/api/agent/overlay/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reasoning: '❌ Task failed: ' + (data.error || 'Unknown error') })
            });
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            showNotification('❌ ' + (data.error || 'Task execution failed'), 'error');
            if (data.execution_log) {
                console.error('Execution log:', data.execution_log);
            }
        }
    } catch (error) {
        showNotification('❌ Task execution failed: ' + error.message, 'error');
    } finally {
        clearInterval(updateInterval);
        // Stop overlay instead of loading circle
        await fetch('/api/agent/overlay/stop', { method: 'POST' });
    }
}

async function sendMessage() {
    const input = document.getElementById('agent-chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    const includeScreen = document.getElementById('include-screen-check').checked;
    
    // Add user message to chat
    addChatMessage('user', message);
    input.value = '';
    
    showLoading(includeScreen ? 'Analyzing screen and generating response...' : 'Generating response...');
    
    try {
        const response = await fetch('/api/agent/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: message,
                include_screen: includeScreen
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addChatMessage('agent', data.response, data.screenshot);
        } else {
            addChatMessage('error', data.error || 'Failed to get response');
        }
    } catch (error) {
        addChatMessage('error', 'Chat failed: ' + error.message);
    } finally {
        hideLoading();
    }
}

async function clearChat() {
    if (!confirm('Clear all chat history?')) return;
    
    try {
        const response = await fetch('/api/agent/clear-history', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('agent-messages').innerHTML = '';
            showNotification('Chat history cleared', 'success');
        }
    } catch (error) {
        showNotification('Failed to clear history: ' + error.message, 'error');
    }
}

async function executeQuickAction(button) {
    const action = button.dataset.action;
    const params = JSON.parse(button.dataset.params);
    
    const actionData = {
        type: action,
        ...params
    };
    
    showLoading('Executing action...');
    
    try {
        const response = await fetch('/api/agent/execute-action', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({action: actionData})
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Action executed successfully', 'success');
        } else {
            showNotification(data.error || 'Action failed', 'error');
        }
    } catch (error) {
        showNotification('Action failed: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function addChatMessage(role, content, screenshot = null) {
    const container = document.getElementById('agent-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${role}`;
    
    const icon = role === 'user' ? '👤' : role === 'agent' ? '🤖' : '❌';
    
    let html = `
        <div class="message-header">
            <span class="message-icon">${icon}</span>
            <span class="message-time">${new Date().toLocaleTimeString()}</span>
        </div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    if (screenshot) {
        html += `<img src="/api/agent/screenshots/${screenshot}" class="message-screenshot" alt="Screenshot">`;
    }
    
    messageDiv.innerHTML = html;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function updateButtonStates() {
    // Always enable these basic controls
    document.getElementById('refresh-models-btn').disabled = false;
    document.getElementById('save-permissions-btn').disabled = false;
    
    // These require agent initialization
    const requiresInit = agentInitialized;
    
    // These require both agent init AND model selection
    const requiresModel = agentInitialized && currentModel;
    
    // Emergency stop button - enable when agent is active
    const emergencyBtn = document.getElementById('emergency-stop-btn');
    const emergencyInfo = document.getElementById('emergency-stop-info');
    if (requiresModel) {
        emergencyBtn.disabled = false;
        emergencyInfo.style.display = 'flex';
    } else {
        emergencyBtn.disabled = true;
        emergencyInfo.style.display = 'none';
    }
    
    // Analyze screen button
    const analyzeBtn = document.getElementById('analyze-screen-btn');
    if (!requiresModel) {
        analyzeBtn.disabled = true;
        analyzeBtn.title = !agentInitialized ? 
            '⚠️ Please initialize agent first' : 
            '⚠️ Please select an Ollama model (e.g., llava)';
    } else {
        analyzeBtn.disabled = false;
        analyzeBtn.title = 'Click to analyze current screen';
    }
    
    // Execute task button
    const executeBtn = document.getElementById('execute-task-btn');
    if (!requiresModel) {
        executeBtn.disabled = true;
        executeBtn.title = !agentInitialized ? 
            '⚠️ Please initialize agent first' : 
            '⚠️ Please select an Ollama model with vision (e.g., llava)';
    } else {
        executeBtn.disabled = false;
        executeBtn.title = 'Agent will autonomously execute multi-step tasks';
    }
    
    // Chat controls
    const chatInput = document.getElementById('agent-chat-input');
    const sendBtn = document.getElementById('send-message-btn');
    const clearBtn = document.getElementById('clear-chat-btn');
    
    if (!requiresModel) {
        chatInput.disabled = true;
        chatInput.placeholder = !agentInitialized ? 
            'Initialize agent and select model first...' : 
            'Select an Ollama model to start chatting...';
        sendBtn.disabled = true;
        sendBtn.title = !agentInitialized ? 
            '⚠️ Initialize agent first' : 
            '⚠️ Select an Ollama model';
        clearBtn.disabled = true;
    } else {
        chatInput.disabled = false;
        chatInput.placeholder = 'Chat with the agent...';
        sendBtn.disabled = false;
        sendBtn.title = 'Send message to agent';
        clearBtn.disabled = false;
    }
    
    // Quick actions and examples - require both init and model
    document.querySelectorAll('.quick-action').forEach(btn => {
        if (!requiresModel) {
            btn.disabled = true;
            btn.title = !agentInitialized ? 
                '⚠️ Initialize agent first' : 
                '⚠️ Select model and grant permissions';
        } else {
            btn.disabled = false;
            btn.title = 'Execute quick action';
        }
    });
    
    document.querySelectorAll('.example-task').forEach(btn => {
        if (!requiresModel) {
            btn.disabled = true;
            btn.title = !agentInitialized ? 
                '⚠️ Initialize agent first' : 
                '⚠️ Select an Ollama model (e.g., llava)';
        } else {
            btn.disabled = false;
            btn.title = 'Click to execute example task';
        }
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show VS Code-style permission prompt
function showPermissionPrompt(title, task, description, capabilities) {
    return new Promise((resolve) => {
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'permission-overlay';
        overlay.innerHTML = `
            <div class="permission-dialog">
                <div class="permission-header">
                    <i class="fas fa-shield-alt"></i>
                    <h3>${title}</h3>
                </div>
                <div class="permission-content">
                    <div class="permission-task">
                        <strong>Task:</strong>
                        <p>${task}</p>
                    </div>
                    <div class="permission-description">
                        ${description}
                    </div>
                    <div class="permission-capabilities">
                        <strong>The agent will:</strong>
                        <ul>
                            ${capabilities.map(cap => `<li>${cap}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="permission-warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>The agent will have access to your screen and input controls during execution.</span>
                    </div>
                </div>
                <div class="permission-actions">
                    <button class="btn btn-secondary" id="permission-cancel">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                    <button class="btn btn-warning" id="permission-manual">
                        <i class="fas fa-hand-paper"></i> Manual Approval
                    </button>
                    <button class="btn btn-success" id="permission-auto">
                        <i class="fas fa-check"></i> Execute Autonomously
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        // Add event listeners
        document.getElementById('permission-cancel').onclick = () => {
            overlay.remove();
            resolve(null);
        };
        
        document.getElementById('permission-manual').onclick = () => {
            overlay.remove();
            resolve(false);
        };
        
        document.getElementById('permission-auto').onclick = () => {
            overlay.remove();
            resolve(true);
        };
        
        // ESC key to cancel
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                overlay.remove();
                resolve(null);
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    });
}

async function emergencyStop() {
    if (!confirm('⚠️ EMERGENCY STOP\n\nThis will immediately:\n• Cancel any running operation\n• Unload the model from VRAM\n• Stop all agent activity\n\nAre you sure?')) {
        return;
    }
    
    const stopBtn = document.getElementById('emergency-stop-btn');
    const originalText = stopBtn.innerHTML;
    stopBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> STOPPING...';
    stopBtn.disabled = true;
    
    try {
        const response = await fetch('/api/agent/cancel', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Force stop overlay
            await fetch('/api/agent/overlay/stop', { method: 'POST' });
            
            showNotification('🛑 Emergency stop successful - Model unloaded', 'success');
            
            // Re-enable buttons after brief delay
            setTimeout(() => {
                stopBtn.innerHTML = originalText;
                updateButtonStates();
            }, 1000);
        } else {
            showNotification('❌ Emergency stop failed: ' + (data.error || 'Unknown error'), 'error');
            stopBtn.innerHTML = originalText;
            stopBtn.disabled = false;
        }
    } catch (error) {
        showNotification('❌ Emergency stop error: ' + error.message, 'error');
        stopBtn.innerHTML = originalText;
        stopBtn.disabled = false;
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});
