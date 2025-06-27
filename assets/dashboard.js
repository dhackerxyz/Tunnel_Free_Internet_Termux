// AI Auto Tunneler Dashboard - Enhanced JavaScript
// Comprehensive dashboard functionality with Termux API integration

class TunnelerDashboard {
    constructor() {
        this.isTermux = this.detectTermux();
        this.currentTab = 'overview';
        this.systemData = {};
        this.charts = {};
        this.refreshIntervals = {};
        this.notifications = [];
        
        this.init();
    }

    async init() {
        console.log('🤖 AI Auto Tunneler Dashboard initializing...');
        
        // Initialize components
        this.setupTabNavigation();
        this.setupEventListeners();
        this.initializeCharts();
        
        // Start data collection
        await this.loadInitialData();
        this.startRealTimeUpdates();
        
        // Setup Termux API if available
        if (this.isTermux) {
            await this.initializeTermuxAPI();
        }
        
        console.log('✅ Dashboard initialization completed');
        this.addNotification('success', 'Dashboard initialized successfully');
    }

    detectTermux() {
        return (
            navigator.userAgent.includes('wv') ||
            window.location.hostname === 'localhost' ||
            typeof Android !== 'undefined'
        );
    }

    setupTabNavigation() {
        const menuItems = document.querySelectorAll('.menu-item');
        
        menuItems.forEach(item => {
            item.addEventListener('click', () => {
                const tabName = item.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }

    switchTab(tabName) {
        // Update menu items
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}Tab`).classList.add('active');
        
        // Update page title
        const titles = {
            overview: 'Dashboard Overview',
            monitor: 'System Monitor',
            tunnels: 'Tunnel Management',
            scanner: 'Network Scanner',
            settings: 'Settings & Configuration',
            device: 'Device Information'
        };
        
        document.getElementById('currentPageTitle').textContent = titles[tabName] || 'Dashboard';
        document.getElementById('currentBreadcrumb').textContent = titles[tabName] || 'Dashboard';
        
        this.currentTab = tabName;
        
        // Load tab-specific data
        this.loadTabData(tabName);
    }

    setupEventListeners() {
        // Range input updates
        const ranges = document.querySelectorAll('.form-range');
        ranges.forEach(range => {
            const valueSpan = document.getElementById(range.id + 'Value');
            if (valueSpan) {
                range.addEventListener('input', () => {
                    valueSpan.textContent = range.value;
                });
            }
        });
    }

    async loadInitialData() {
        try {
            // Load system status
            const status = await this.apiCall('/api/status');
            this.updateSystemStatus(status);
            
            // Load system info
            const info = await this.apiCall('/api/info');
            this.updateSystemInfo(info);
            
            // Load scan results
            const results = await this.apiCall('/api/results');
            this.updateScanResults(results);
            
            // Load health data
            const health = await this.apiCall('/health');
            this.updateHealthMetrics(health);
            
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.addNotification('error', 'Failed to load system data');
        }
    }

    async loadTabData(tabName) {
        switch (tabName) {
            case 'device':
                await this.loadDeviceInfo();
                break;
            case 'monitor':
                await this.loadMonitoringData();
                break;
            case 'settings':
                await this.loadSettings();
                break;
        }
    }

    startRealTimeUpdates() {
        // Update system status every 5 seconds
        this.refreshIntervals.status = setInterval(() => {
            this.updateSystemStatusReal();
        }, 5000);
        
        // Update device info every 30 seconds
        this.refreshIntervals.device = setInterval(() => {
            if (this.currentTab === 'device') {
                this.updateDeviceInfoReal();
            }
        }, 30000);
        
        // Update charts every 10 seconds
        this.refreshIntervals.charts = setInterval(() => {
            if (this.currentTab === 'monitor') {
                this.updateChartsReal();
            }
        }, 10000);
        
        // Update uptime every second
        this.refreshIntervals.uptime = setInterval(() => {
            this.updateUptime();
        }, 1000);
    }

    async initializeTermuxAPI() {
        console.log('🔧 Initializing Termux API integration...');
        
        try {
            // Test Termux API availability
            await this.getTermuxBatteryStatus();
            await this.getTermuxDeviceInfo();
            await this.getTermuxLocationInfo();
            
            console.log('✅ Termux API integration successful');
            this.addNotification('success', 'Termux API connected successfully');
        } catch (error) {
            console.warn('⚠️ Termux API not available:', error);
            this.addNotification('warning', 'Termux API not available - using fallback methods');
        }
    }

    async getTermuxBatteryStatus() {
        try {
            const response = await fetch('/api/termux/battery');
            if (response.ok) {
                const batteryData = await response.json();
                this.updateBatteryInfo(batteryData);
                return batteryData;
            }
        } catch (error) {
            // Fallback to estimated battery info
            return { level: 100, status: 'Unknown', temperature: 'Unknown' };
        }
    }

    async getTermuxDeviceInfo() {
        try {
            const response = await fetch('/api/termux/device');
            if (response.ok) {
                const deviceData = await response.json();
                this.updateDeviceInfoDisplay(deviceData);
                return deviceData;
            }
        } catch (error) {
            console.warn('Termux device info not available');
        }
    }

    async getTermuxLocationInfo() {
        try {
            const response = await fetch('/api/termux/location');
            if (response.ok) {
                const locationData = await response.json();
                this.updateLocationInfo(locationData);
                return locationData;
            }
        } catch (error) {
            console.warn('Termux location info not available');
        }
    }

    initializeCharts() {
        // Connection Performance Chart
        const connectionCtx = document.getElementById('connectionChart');
        if (connectionCtx) {
            this.charts.connection = new Chart(connectionCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Response Time (ms)',
                        data: [],
                        borderColor: '#00d4aa',
                        backgroundColor: 'rgba(0, 212, 170, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#b0b0b0'
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#b0b0b0' },
                            grid: { color: '#333' }
                        },
                        y: {
                            ticks: { color: '#b0b0b0' },
                            grid: { color: '#333' }
                        }
                    }
                }
            });
        }
    }

    async updateSystemStatusReal() {
        try {
            const status = await this.apiCall('/api/status');
            this.updateSystemStatus(status);
        } catch (error) {
            console.error('Failed to update system status:', error);
        }
    }

    async updateDeviceInfoReal() {
        try {
            if (this.isTermux) {
                await this.getTermuxBatteryStatus();
                await this.getTermuxDeviceInfo();
            }
            
            const info = await this.apiCall('/api/info');
            this.updateSystemInfo(info);
        } catch (error) {
            console.error('Failed to update device info:', error);
        }
    }

    async updateChartsReal() {
        try {
            // Add new data point to connection chart
            if (this.charts.connection) {
                const now = new Date().toLocaleTimeString();
                const responseTime = Math.random() * 1000 + 200; // Simulated data
                
                this.charts.connection.data.labels.push(now);
                this.charts.connection.data.datasets[0].data.push(responseTime);
                
                // Keep only last 20 data points
                if (this.charts.connection.data.labels.length > 20) {
                    this.charts.connection.data.labels.shift();
                    this.charts.connection.data.datasets[0].data.shift();
                }
                
                this.charts.connection.update('none');
            }
        } catch (error) {
            console.error('Failed to update charts:', error);
        }
    }

    updateUptime() {
        const uptimeElement = document.getElementById('systemUptime');
        if (uptimeElement && this.systemData.startTime) {
            const now = new Date();
            const uptime = now - this.systemData.startTime;
            
            const hours = Math.floor(uptime / (1000 * 60 * 60));
            const minutes = Math.floor((uptime % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((uptime % (1000 * 60)) / 1000);
            
            uptimeElement.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }

    updateSystemStatus(status) {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        const tunnelStatus = document.getElementById('tunnelStatus');
        
        if (status.tunnel_active) {
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'Connected';
            tunnelStatus.textContent = 'Connected';
            tunnelStatus.style.color = '#4caf50';
        } else {
            statusDot.className = 'status-dot';
            statusText.textContent = 'Disconnected';
            tunnelStatus.textContent = 'Disconnected';
            tunnelStatus.style.color = '#f44336';
        }
        
        // Store start time for uptime calculation
        if (!this.systemData.startTime && status.uptime) {
            this.systemData.startTime = new Date(Date.now() - (status.uptime * 1000));
        }
    }

    updateSystemInfo(info) {
        if (info.system) {
            const totalScans = document.getElementById('totalScans');
            if (totalScans && info.database_stats) {
                const total = (info.database_stats.sni_domains || 0) + (info.database_stats.ssh_servers || 0);
                totalScans.textContent = total;
            }
            
            const workingCombos = document.getElementById('workingCombos');
            if (workingCombos && info.database_stats) {
                workingCombos.textContent = info.database_stats.working_combinations || 0;
            }
        }
    }

    updateScanResults(results) {
        // Update recent activity
        const activityList = document.getElementById('recentActivity');
        if (activityList && results.statistics) {
            const stats = results.statistics;
            let activityHtml = '';
            
            if (stats.last_scan) {
                const scanTime = new Date(stats.last_scan).toLocaleTimeString();
                activityHtml += `
                    <div class="activity-item">
                        <span class="activity-time">${scanTime}</span>
                        <span class="activity-desc">Last scan completed</span>
                    </div>
                `;
            }
            
            if (stats.sni_active > 0) {
                activityHtml += `
                    <div class="activity-item">
                        <span class="activity-time">Recent</span>
                        <span class="activity-desc">${stats.sni_active} SNI domains found</span>
                    </div>
                `;
            }
            
            if (stats.ssh_active > 0) {
                activityHtml += `
                    <div class="activity-item">
                        <span class="activity-time">Recent</span>
                        <span class="activity-desc">${stats.ssh_active} SSH servers found</span>
                    </div>
                `;
            }
            
            if (activityHtml) {
                activityList.innerHTML = activityHtml;
            }
        }
    }

    updateHealthMetrics(health) {
        // Simulate CPU and memory usage
        const cpuUsage = Math.random() * 50 + 10; // 10-60%
        const memoryUsage = Math.random() * 40 + 20; // 20-60%
        
        this.updateProgressBar('cpuProgress', 'cpuValue', cpuUsage);
        this.updateProgressBar('memoryProgress', 'memoryValue', memoryUsage);
    }

    updateProgressBar(progressId, valueId, percentage) {
        const progressBar = document.getElementById(progressId);
        const valueSpan = document.getElementById(valueId);
        
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }
        
        if (valueSpan) {
            valueSpan.textContent = `${Math.round(percentage)}%`;
        }
    }

    updateBatteryInfo(batteryData) {
        const batteryProgress = document.getElementById('batteryProgress');
        const batteryValue = document.getElementById('batteryValue');
        const batteryLevel = document.getElementById('batteryLevel');
        const batteryStatus = document.getElementById('batteryStatus');
        const batteryTemp = document.getElementById('batteryTemp');
        
        const level = batteryData.level || batteryData.percentage || 100;
        
        if (batteryProgress) {
            batteryProgress.style.width = `${level}%`;
            
            // Change color based on battery level
            if (level < 20) {
                batteryProgress.style.background = '#f44336';
            } else if (level < 50) {
                batteryProgress.style.background = '#ff9800';
            } else {
                batteryProgress.style.background = 'var(--gradient-primary)';
            }
        }
        
        if (batteryValue) batteryValue.textContent = `${level}%`;
        if (batteryLevel) batteryLevel.textContent = `${level}%`;
        if (batteryStatus) batteryStatus.textContent = batteryData.status || 'Unknown';
        if (batteryTemp) batteryTemp.textContent = batteryData.temperature ? `${batteryData.temperature}°C` : 'Unknown';
    }

    updateDeviceInfoDisplay(deviceData) {
        const deviceModel = document.getElementById('deviceModel');
        const androidVersion = document.getElementById('androidVersion');
        const deviceArch = document.getElementById('deviceArch');
        const termuxVersion = document.getElementById('termuxVersion');
        
        if (deviceModel) deviceModel.textContent = deviceData.model || 'Unknown';
        if (androidVersion) androidVersion.textContent = deviceData.android_version || 'Unknown';
        if (deviceArch) deviceArch.textContent = deviceData.architecture || 'Unknown';
        if (termuxVersion) termuxVersion.textContent = deviceData.termux_version || 'Unknown';
    }

    updateLocationInfo(locationData) {
        const locationInfo = document.getElementById('locationInfo');
        if (locationInfo && locationData) {
            locationInfo.textContent = `${locationData.city || 'Unknown'}, ${locationData.country || 'Unknown'}`;
        }
    }

    async loadDeviceInfo() {
        try {
            const info = await this.apiCall('/api/info');
            
            if (info.system) {
                this.updateDeviceInfoDisplay(info.system);
            }
            
            // Update network info
            await this.updateNetworkInfo();
            
        } catch (error) {
            console.error('Failed to load device info:', error);
        }
    }

    async loadMonitoringData() {
        try {
            // Update network status
            await this.updateNetworkInfo();
            
            // Initialize or update charts
            if (!this.charts.connection) {
                this.initializeCharts();
            }
            
        } catch (error) {
            console.error('Failed to load monitoring data:', error);
        }
    }

    async updateNetworkInfo() {
        try {
            // Get public IP and location
            const ipResponse = await fetch('https://ipapi.co/json/');
            if (ipResponse.ok) {
                const ipData = await ipResponse.json();
                
                const publicIp = document.getElementById('publicIp');
                const ispInfo = document.getElementById('ispInfo');
                const locationInfo = document.getElementById('locationInfo');
                const operatorInfo = document.getElementById('operatorInfo');
                
                if (publicIp) publicIp.textContent = ipData.ip || 'Unknown';
                if (ispInfo) ispInfo.textContent = ipData.org || 'Unknown';
                if (locationInfo) locationInfo.textContent = `${ipData.city || 'Unknown'}, ${ipData.country_name || 'Unknown'}`;
                
                // Detect Indonesian operator
                if (operatorInfo) {
                    const operator = this.detectIndonesianOperator(ipData.org || '');
                    operatorInfo.textContent = operator;
                }
            }
        } catch (error) {
            console.warn('Failed to get network info:', error);
        }
    }

    detectIndonesianOperator(isp) {
        const ispLower = isp.toLowerCase();
        
        if (ispLower.includes('telkomsel') || ispLower.includes('telkom')) return 'Telkomsel';
        if (ispLower.includes('indosat') || ispLower.includes('ooredoo') || ispLower.includes('im3')) return 'Indosat';
        if (ispLower.includes('xl') || ispLower.includes('axis')) return 'XL/Axis';
        if (ispLower.includes('smartfren')) return 'Smartfren';
        if (ispLower.includes('tri') || ispLower.includes('hutchison') || ispLower.includes('3')) return '3 (Tri)';
        
        return 'Unknown / International';
    }

    async loadSettings() {
        // Load current settings from localStorage or API
        const settings = this.getStoredSettings();
        
        // Update UI with current settings
        Object.keys(settings).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = settings[key];
                } else if (element.type === 'range') {
                    element.value = settings[key];
                    const valueSpan = document.getElementById(key + 'Value');
                    if (valueSpan) valueSpan.textContent = settings[key];
                } else {
                    element.value = settings[key];
                }
            }
        });
    }

    getStoredSettings() {
        const defaultSettings = {
            maxConcurrentScans: 5,
            scanTimeout: 10,
            retryAttempts: 3,
            notifySuccess: true,
            notifyFailure: true,
            notifyBattery: false,
            notifyUpdates: true,
            debugMode: 'off',
            logLevel: 'info'
        };
        
        try {
            const stored = localStorage.getItem('tunnelerSettings');
            return stored ? { ...defaultSettings, ...JSON.parse(stored) } : defaultSettings;
        } catch {
            return defaultSettings;
        }
    }

    saveStoredSettings(settings) {
        try {
            localStorage.setItem('tunnelerSettings', JSON.stringify(settings));
            return true;
        } catch {
            return false;
        }
    }

    addNotification(type, message) {
        const notification = {
            id: Date.now(),
            type: type,
            message: message,
            timestamp: new Date()
        };
        
        this.notifications.unshift(notification);
        
        // Keep only last 50 notifications
        if (this.notifications.length > 50) {
            this.notifications = this.notifications.slice(0, 50);
        }
        
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        // Show toast notification
        this.showToast(type, message);
    }

    showToast(type, message) {
        // Simple toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#ff9800'};
            color: white;
            border-radius: 8px;
            z-index: 10000;
            opacity: 0;
            transform: translateX(100px);
            transition: all 0.3s ease;
            max-width: 300px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        `;
        
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after 5 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100px)';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 5000);
    }

    async apiCall(endpoint, options = {}) {
        try {
            const response = await fetch(endpoint, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API call failed for ${endpoint}:`, error);
            throw error;
        }
    }

    showLoading(text = 'Loading...') {
        const overlay = document.getElementById('loadingOverlay');
        const loadingText = document.getElementById('loadingText');
        
        if (loadingText) loadingText.textContent = text;
        if (overlay) overlay.style.display = 'flex';
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) overlay.style.display = 'none';
    }
}

// Global functions for UI interactions
let dashboard;

document.addEventListener('DOMContentLoaded', () => {
    dashboard = new TunnelerDashboard();
});

// Auto Configuration Functions
async function runAutoConfig() {
    dashboard.showLoading('Running auto-configuration...');
    dashboard.addNotification('info', 'Starting auto-configuration...');
    
    try {
        const response = await fetch('/api/auto-config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // Update UI with configuration results
            const configStatus = document.getElementById('autoConfigStatus');
            const configResults = document.getElementById('autoConfigResults');
            const configDetails = document.getElementById('configDetails');
            
            if (configStatus) {
                configStatus.innerHTML = `
                    <span class="config-indicator">✅</span>
                    <span>Auto-configuration completed successfully</span>
                    <button class="btn btn-secondary" onclick="runAutoConfig()">
                        🔄 Run Again
                    </button>
                `;
            }
            
            if (configResults && configDetails) {
                configResults.style.display = 'block';
                configDetails.innerHTML = `
                    <p><strong>Detected Operator:</strong> ${result.operator?.detected_operator || 'Unknown'}</p>
                    <p><strong>Recommended SNI Domains:</strong> ${result.optimal_settings?.recommended_sni_domains?.length || 0}</p>
                    <p><strong>Performance Score:</strong> ${result.test_results?.overall_score || 0}/100</p>
                    <p><strong>Configuration Applied:</strong> ${result.auto_apply ? 'Yes' : 'No'}</p>
                `;
            }
            
            dashboard.addNotification('success', 'Auto-configuration completed successfully');
        } else {
            throw new Error('Auto-configuration failed');
        }
    } catch (error) {
        dashboard.addNotification('error', `Auto-configuration failed: ${error.message}`);
    } finally {
        dashboard.hideLoading();
    }
}

// Quick Action Functions
async function quickScan(type) {
    dashboard.showLoading(`Starting ${type.toUpperCase()} scan...`);
    
    try {
        const response = await fetch('/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scan_type: type, limit: 5 })
        });
        
        if (response.ok) {
            const result = await response.json();
            dashboard.addNotification('success', result.message);
            
            // Auto-refresh results after scan
            setTimeout(() => {
                dashboard.loadInitialData();
            }, result.estimated_duration ? parseInt(result.estimated_duration) * 1000 : 10000);
        } else {
            throw new Error('Scan failed to start');
        }
    } catch (error) {
        dashboard.addNotification('error', `Quick scan failed: ${error.message}`);
    } finally {
        dashboard.hideLoading();
    }
}

async function testBestCombo() {
    dashboard.showLoading('Testing best configuration...');
    
    try {
        const results = await dashboard.apiCall('/api/results');
        
        if (results.working_combinations && results.working_combinations.length > 0) {
            const bestCombo = results.working_combinations[0];
            
            const config = {
                sni_domain: bestCombo.sni_domain,
                ssh_host: bestCombo.ssh_host,
                ssh_port: bestCombo.ssh_port,
                ssh_user: bestCombo.ssh_user,
                ssh_pass: bestCombo.ssh_pass
            };
            
            const response = await fetch('/api/tunnel/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            
            if (response.ok) {
                const result = await response.json();
                dashboard.addNotification('success', 'Best configuration connected successfully');
                dashboard.updateSystemStatusReal();
            } else {
                throw new Error('Failed to connect with best configuration');
            }
        } else {
            dashboard.addNotification('warning', 'No working configurations found. Run a bypass test first.');
        }
    } catch (error) {
        dashboard.addNotification('error', `Test failed: ${error.message}`);
    } finally {
        dashboard.hideLoading();
    }
}

async function emergencyStop() {
    dashboard.showLoading('Stopping all tunnels...');
    
    try {
        const response = await fetch('/api/tunnel/stop', { method: 'POST' });
        
        if (response.ok) {
            dashboard.addNotification('success', 'All tunnels stopped successfully');
            dashboard.updateSystemStatusReal();
        } else {
            throw new Error('Failed to stop tunnels');
        }
    } catch (error) {
        dashboard.addNotification('error', `Emergency stop failed: ${error.message}`);
    } finally {
        dashboard.hideLoading();
    }
}

// Settings Functions
function saveSettings() {
    const settings = {};
    
    // Collect all form values
    const formElements = document.querySelectorAll('#settingsTab input, #settingsTab select');
    formElements.forEach(element => {
        if (element.type === 'checkbox') {
            settings[element.id] = element.checked;
        } else if (element.type === 'range') {
            settings[element.id] = parseInt(element.value);
        } else {
            settings[element.id] = element.value;
        }
    });
    
    // Save to localStorage
    if (dashboard.saveStoredSettings(settings)) {
        dashboard.addNotification('success', 'Settings saved successfully');
    } else {
        dashboard.addNotification('error', 'Failed to save settings');
    }
}

function resetSettings() {
    if (confirm('Are you sure you want to reset all settings to default?')) {
        localStorage.removeItem('tunnelerSettings');
        dashboard.loadSettings();
        dashboard.addNotification('success', 'Settings reset to default');
    }
}

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (dashboard && dashboard.refreshIntervals) {
        Object.values(dashboard.refreshIntervals).forEach(interval => {
            if (interval) clearInterval(interval);
        });
    }
});
