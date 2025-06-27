// AI Auto Tunneler - Frontend JavaScript
// Real-time Web UI Controller

class AutoTunneler {
    constructor() {
        this.isConnected = false;
        this.currentConfig = null;
        this.refreshInterval = null;
        this.logsRefreshInterval = null;
        
        this.init();
    }

    async init() {
        console.log('🚀 AI Auto Tunneler Web UI initialized');
        
        // Start status monitoring
        this.startStatusMonitoring();
        
        // Start logs monitoring
        this.startLogsMonitoring();
        
        // Load initial data
        await this.refreshResults();
        await this.refreshStatus();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Show welcome message
        this.addLog('🤖 AI Auto Tunneler Web UI ready!', 'success');
        this.addLog('💡 Click "Scan SNI Domains" or "Scan SSH Servers" to start', 'info');
    }

    setupEventListeners() {
        // Handle page visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                this.refreshStatus();
                this.refreshResults();
            }
        });

        // Handle connection test periodically when connected
        setInterval(() => {
            if (this.isConnected) {
                this.testConnectionSilent();
            }
        }, 30000); // Every 30 seconds
    }

    startStatusMonitoring() {
        this.refreshInterval = setInterval(async () => {
            await this.refreshStatus();
        }, 5000); // Every 5 seconds
    }

    startLogsMonitoring() {
        this.logsRefreshInterval = setInterval(async () => {
            await this.refreshLogs();
        }, 3000); // Every 3 seconds
    }

    async refreshStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            this.updateStatusIndicator(status.tunnel_active);
            
            if (status.tunnel_active && status.config) {
                this.isConnected = true;
                this.currentConfig = status.config;
                this.showConnectionInfo(status);
                this.updateButtonStates(true);
            } else {
                this.isConnected = false;
                this.currentConfig = null;
                this.hideConnectionInfo();
                this.updateButtonStates(false);
            }
        } catch (error) {
            console.error('Status refresh error:', error);
        }
    }

    updateStatusIndicator(isConnected) {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        if (isConnected) {
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'Connected';
        } else {
            statusDot.className = 'status-dot';
            statusText.textContent = 'Disconnected';
        }
    }

    updateButtonStates(isConnected) {
        const startBtn = document.getElementById('startTunnelBtn');
        const stopBtn = document.getElementById('stopTunnelBtn');
        const testBtn = document.getElementById('testConnBtn');
        
        startBtn.disabled = isConnected;
        stopBtn.disabled = !isConnected;
        testBtn.disabled = !isConnected;
        
        // Update scan buttons state
        const scanButtons = ['scanSniBtn', 'scanSshBtn', 'testBypassBtn'];
        scanButtons.forEach(btnId => {
            const btn = document.getElementById(btnId);
            if (btn) {
                btn.disabled = false; // Always allow scanning
            }
        });
    }

    showConnectionInfo(status) {
        const connectionInfo = document.getElementById('connectionInfo');
        const socksInfo = document.getElementById('socksInfo');
        const connStatus = document.getElementById('connStatus');
        
        connectionInfo.style.display = 'block';
        socksInfo.textContent = `127.0.0.1:${status.socks_port || 9092}`;
        connStatus.textContent = 'Connected';
        
        // Update current IP
        this.updateCurrentIP();
    }

    hideConnectionInfo() {
        const connectionInfo = document.getElementById('connectionInfo');
        connectionInfo.style.display = 'none';
    }

    async updateCurrentIP() {
        try {
            // This would need to be implemented via backend proxy
            const currentIp = document.getElementById('currentIp');
            currentIp.textContent = 'Checking...';
            
            // Simulate IP check
            setTimeout(() => {
                if (this.isConnected) {
                    currentIp.textContent = 'Tunneled IP';
                }
            }, 2000);
        } catch (error) {
            document.getElementById('currentIp').textContent = 'Error';
        }
    }

    async refreshResults() {
        try {
            const response = await fetch('/api/results');
            const results = await response.json();
            
            this.displaySNIResults(results.sni_domains || []);
            this.displaySSHResults(results.ssh_servers || []);
            this.displayWorkingCombinations(results.working_combinations || []);
            
        } catch (error) {
            console.error('Results refresh error:', error);
        }
    }

    displaySNIResults(sniDomains) {
        const container = document.getElementById('sniResults');
        
        if (sniDomains.length === 0) {
            container.innerHTML = '<div class="no-results">No SNI domains scanned yet. Click "Scan SNI Domains" to start.</div>';
            return;
        }

        const html = sniDomains.map(domain => `
            <div class="result-card" onclick="selectSNIDomain('${domain.domain}')">
                <h4>🌐 ${domain.domain}</h4>
                <p><strong>Status:</strong> <span class="result-status ${domain.status}">${domain.status}</span></p>
                <p><strong>Response Time:</strong> ${domain.response_time || 'N/A'}ms</p>
                <p><strong>Scanned:</strong> ${new Date(domain.timestamp).toLocaleString()}</p>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }

    displaySSHResults(sshServers) {
        const container = document.getElementById('sshResults');
        
        if (sshServers.length === 0) {
            container.innerHTML = '<div class="no-results">No SSH servers scanned yet. Click "Scan SSH Servers" to start.</div>';
            return;
        }

        const html = sshServers.map(server => `
            <div class="result-card" onclick="selectSSHServer('${server.host}', ${server.port}, '${server.username}', '${server.password}')">
                <h4>🔐 ${server.host}:${server.port}</h4>
                <p><strong>Username:</strong> ${server.username}</p>
                <p><strong>Password:</strong> ${'*'.repeat(server.password.length)}</p>
                <p><strong>Status:</strong> <span class="result-status ${server.status}">${server.status}</span></p>
                <p><strong>Scanned:</strong> ${new Date(server.timestamp).toLocaleString()}</p>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }

    displayWorkingCombinations(workingCombos) {
        const container = document.getElementById('workingResults');
        
        if (workingCombos.length === 0) {
            container.innerHTML = '<div class="no-results">No working combinations found yet. Click "Test Bypass" to start.</div>';
            return;
        }

        const html = workingCombos.map(combo => `
            <div class="result-card" onclick="useWorkingCombo('${combo.sni_domain}', '${combo.ssh_host}', ${combo.ssh_port}, '${combo.ssh_user}', '${combo.ssh_pass}')">
                <h4>⭐ Working Combination</h4>
                <p><strong>SNI:</strong> ${combo.sni_domain}</p>
                <p><strong>SSH:</strong> ${combo.ssh_host}:${combo.ssh_port}</p>
                <p><strong>User:</strong> ${combo.ssh_user}</p>
                <p><strong>Speed:</strong> ${combo.speed || 'Good'}</p>
                <p><strong>Found:</strong> ${new Date(combo.timestamp).toLocaleString()}</p>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }

    async refreshLogs() {
        try {
            const response = await fetch('/api/logs');
            const data = await response.json();
            
            if (data.logs && data.logs.length > 0) {
                const logsContent = document.getElementById('logsContent');
                const currentLogs = logsContent.innerHTML;
                const newLogsHtml = data.logs.map(log => `<div class="log-entry">${log.trim()}</div>`).join('');
                
                // Only update if logs changed
                if (currentLogs !== newLogsHtml) {
                    logsContent.innerHTML = newLogsHtml;
                    logsContent.scrollTop = logsContent.scrollHeight;
                }
            }
        } catch (error) {
            console.error('Logs refresh error:', error);
        }
    }

    addLog(message, type = 'info') {
        const logsContent = document.getElementById('logsContent');
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.textContent = `[${timestamp}] ${message}`;
        
        logsContent.appendChild(logEntry);
        logsContent.scrollTop = logsContent.scrollHeight;
    }

    showLoading(text = 'Processing...') {
        const overlay = document.getElementById('loadingOverlay');
        const loadingText = document.getElementById('loadingText');
        
        loadingText.textContent = text;
        overlay.style.display = 'flex';
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'none';
    }

    async testConnectionSilent() {
        try {
            const response = await fetch('/api/tunnel/test');
            const result = await response.json();
            
            if (result.status === 'success') {
                const connSpeed = document.getElementById('connSpeed');
                if (connSpeed) {
                    connSpeed.textContent = result.speed || 'Good';
                }
            }
        } catch (error) {
            console.error('Silent connection test error:', error);
        }
    }
}

// Global functions for UI interactions
let autoTunneler;

document.addEventListener('DOMContentLoaded', () => {
    autoTunneler = new AutoTunneler();
});

async function startScan(scanType) {
    const scanNames = {
        'sni': 'SNI Domains',
        'ssh': 'SSH Servers', 
        'bypass': 'Bypass Combinations'
    };
    
    autoTunneler.showLoading(`Scanning ${scanNames[scanType]}...`);
    autoTunneler.addLog(`🔍 Starting ${scanNames[scanType]} scan...`, 'info');
    
    try {
        const response = await fetch('/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scan_type: scanType, limit: 10 })
        });
        
        const result = await response.json();
        
        if (result.status === 'started') {
            autoTunneler.addLog(`✅ ${result.message}`, 'success');
            
            // Auto-refresh results after a delay
            setTimeout(() => {
                autoTunneler.refreshResults();
            }, 5000);
        } else {
            autoTunneler.addLog(`❌ Scan failed: ${result.message}`, 'error');
        }
        
    } catch (error) {
        autoTunneler.addLog(`❌ Scan error: ${error.message}`, 'error');
    } finally {
        autoTunneler.hideLoading();
    }
}

async function startTunnel() {
    const sniDomain = document.getElementById('sniDomain').value.trim();
    const sshHost = document.getElementById('sshHost').value.trim();
    const sshPort = parseInt(document.getElementById('sshPort').value) || 22;
    const sshUser = document.getElementById('sshUser').value.trim();
    const sshPass = document.getElementById('sshPass').value.trim();
    
    if (!sniDomain || !sshHost || !sshUser || !sshPass) {
        autoTunneler.addLog('❌ Please fill all fields', 'error');
        return;
    }
    
    autoTunneler.showLoading('Starting tunnel...');
    autoTunneler.addLog('🚀 Starting tunnel connection...', 'info');
    
    try {
        const config = {
            sni_domain: sniDomain,
            ssh_host: sshHost,
            ssh_port: sshPort,
            ssh_user: sshUser,
            ssh_pass: sshPass,
            local_port: 9092
        };
        
        const response = await fetch('/api/tunnel/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            autoTunneler.addLog(`✅ ${result.message}`, 'success');
            autoTunneler.addLog(`🌐 SOCKS proxy active on port ${result.socks_port}`, 'success');
            
            // Refresh status
            setTimeout(() => {
                autoTunneler.refreshStatus();
            }, 2000);
        } else {
            autoTunneler.addLog(`❌ ${result.message}`, 'error');
        }
        
    } catch (error) {
        autoTunneler.addLog(`❌ Connection error: ${error.message}`, 'error');
    } finally {
        autoTunneler.hideLoading();
    }
}

async function stopTunnel() {
    autoTunneler.showLoading('Stopping tunnel...');
    autoTunneler.addLog('⏹️ Stopping tunnel...', 'warning');
    
    try {
        const response = await fetch('/api/tunnel/stop', { method: 'POST' });
        const result = await response.json();
        
        if (result.status === 'success') {
            autoTunneler.addLog(`✅ ${result.message}`, 'success');
            autoTunneler.refreshStatus();
        } else {
            autoTunneler.addLog(`❌ ${result.message}`, 'error');
        }
        
    } catch (error) {
        autoTunneler.addLog(`❌ Stop error: ${error.message}`, 'error');
    } finally {
        autoTunneler.hideLoading();
    }
}

async function testConnection() {
    autoTunneler.showLoading('Testing connection...');
    autoTunneler.addLog('🔗 Testing tunnel connection...', 'info');
    
    try {
        const response = await fetch('/api/tunnel/test');
        const result = await response.json();
        
        if (result.status === 'success') {
            autoTunneler.addLog(`✅ Connection test passed`, 'success');
            if (result.ip) {
                autoTunneler.addLog(`🌐 Current IP: ${result.ip}`, 'info');
                document.getElementById('currentIp').textContent = result.ip;
            }
            if (result.speed) {
                document.getElementById('connSpeed').textContent = result.speed;
            }
        } else {
            autoTunneler.addLog(`❌ Connection test failed: ${result.message}`, 'error');
        }
        
    } catch (error) {
        autoTunneler.addLog(`❌ Test error: ${error.message}`, 'error');
    } finally {
        autoTunneler.hideLoading();
    }
}

async function useBestConfig() {
    autoTunneler.addLog('🔍 Looking for best configuration...', 'info');
    
    try {
        const response = await fetch('/api/results');
        const results = await response.json();
        
        if (results.working_combinations && results.working_combinations.length > 0) {
            const bestCombo = results.working_combinations[results.working_combinations.length - 1];
            
            // Fill form with best combination
            document.getElementById('sniDomain').value = bestCombo.sni_domain;
            document.getElementById('sshHost').value = bestCombo.ssh_host;
            document.getElementById('sshPort').value = bestCombo.ssh_port;
            document.getElementById('sshUser').value = bestCombo.ssh_user;
            document.getElementById('sshPass').value = bestCombo.ssh_pass;
            
            autoTunneler.addLog(`✅ Best configuration loaded: ${bestCombo.sni_domain} + ${bestCombo.ssh_host}`, 'success');
            autoTunneler.addLog('🚀 Click "Start Tunnel" to connect', 'info');
        } else {
            autoTunneler.addLog('❌ No working configurations found. Run "Test Bypass" first.', 'error');
        }
        
    } catch (error) {
        autoTunneler.addLog(`❌ Error loading best config: ${error.message}`, 'error');
    }
}

function showTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Hide all tab buttons
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(`${tabName}Tab`).classList.add('active');
    event.target.classList.add('active');
}

function selectSNIDomain(domain) {
    document.getElementById('sniDomain').value = domain;
    autoTunneler.addLog(`📋 SNI domain selected: ${domain}`, 'info');
}

function selectSSHServer(host, port, username, password) {
    document.getElementById('sshHost').value = host;
    document.getElementById('sshPort').value = port;
    document.getElementById('sshUser').value = username;
    document.getElementById('sshPass').value = password;
    autoTunneler.addLog(`📋 SSH server selected: ${host}:${port}`, 'info');
}

function useWorkingCombo(sniDomain, sshHost, sshPort, sshUser, sshPass) {
    document.getElementById('sniDomain').value = sniDomain;
    document.getElementById('sshHost').value = sshHost;
    document.getElementById('sshPort').value = sshPort;
    document.getElementById('sshUser').value = sshUser;
    document.getElementById('sshPass').value = sshPass;
    
    autoTunneler.addLog(`⭐ Working combination selected: ${sniDomain} + ${sshHost}`, 'success');
    autoTunneler.addLog('🚀 Click "Start Tunnel" to connect', 'info');
}

function clearLogs() {
    const logsContent = document.getElementById('logsContent');
    logsContent.innerHTML = '<div class="log-entry">Logs cleared</div>';
}

function refreshLogs() {
    autoTunneler.refreshLogs();
    autoTunneler.addLog('🔄 Logs refreshed', 'info');
}

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (autoTunneler.refreshInterval) {
        clearInterval(autoTunneler.refreshInterval);
    }
    if (autoTunneler.logsRefreshInterval) {
        clearInterval(autoTunneler.logsRefreshInterval);
    }
});
