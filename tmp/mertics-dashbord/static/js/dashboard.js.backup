/**
 * Robot Framework Metrics Dashboard
 * JavaScript utilities and helpers
 */

// Global configuration
const CONFIG = {
    refreshInterval: 30000, // 30 seconds
    apiBaseUrl: '',
    chartColors: {
        primary: '#3b82f6',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#06b6d4'
    }
};

// Auto-refresh functionality
let autoRefreshInterval = null;

function startAutoRefresh(callback, interval = CONFIG.refreshInterval) {
    stopAutoRefresh();
    autoRefreshInterval = setInterval(callback, interval);
    console.log(`Auto-refresh started (${interval}ms)`);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        console.log('Auto-refresh stopped');
    }
}

// API helper functions
async function apiGet(endpoint) {
    try {
        const response = await fetch(CONFIG.apiBaseUrl + endpoint);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`API GET error (${endpoint}):`, error);
        throw error;
    }
}

async function apiPost(endpoint, data = {}) {
    try {
        const response = await fetch(CONFIG.apiBaseUrl + endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`API POST error (${endpoint}):`, error);
        throw error;
    }
}

async function apiDelete(endpoint) {
    try {
        const response = await fetch(CONFIG.apiBaseUrl + endpoint, {
            method: 'DELETE'
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`API DELETE error (${endpoint}):`, error);
        throw error;
    }
}

// Utility functions
function formatTimestamp(timestamp) {
    if (!timestamp) return '-';
    
    try {
        // Parse ISO 8601 format
        const date = new Date(timestamp);
        
        if (isNaN(date.getTime())) {
            return timestamp;
        }
        
        // Use browser's local timezone
        return date.toLocaleString('bg-BG', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        console.error('Error parsing timestamp:', timestamp, error);
        return timestamp;
    }
}

function formatDuration(seconds) {
    if (!seconds || seconds < 0) return '0s';
    
    if (seconds < 60) {
        return Math.round(seconds * 10) / 10 + 's';
    }
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.round(seconds % 60);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    }
    
    return `${minutes}m ${secs}s`;
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getStatusBadgeClass(status) {
    const statusMap = {
        'PASS': 'badge-success',
        'FAIL': 'badge-danger',
        'SKIP': 'badge-warning',
        'NOT RUN': 'badge-secondary'
    };
    return statusMap[status] || 'badge-secondary';
}

function getPassRateBadgeClass(passRate) {
    if (passRate >= 80) return 'badge-success';
    if (passRate >= 50) return 'badge-warning';
    return 'badge-danger';
}

// Chart utilities
function createGradient(ctx, color) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, color + 'CC');
    gradient.addColorStop(1, color + '00');
    return gradient;
}

function getChartDefaults() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'bottom'
            },
            tooltip: {
                mode: 'index',
                intersect: false,
            }
        },
        interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
        }
    };
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Loading state management
function showLoading(element) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    if (element) {
        element.innerHTML = '<p class="loading">Loading...</p>';
    }
}

function hideLoading(element) {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    // Content will be replaced by actual data
}

// Local storage helpers
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }
}

function loadFromLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.error('Error loading from localStorage:', error);
        return defaultValue;
    }
}

// Export utilities for use in other scripts
window.DashboardUtils = {
    apiGet,
    apiPost,
    apiDelete,
    formatTimestamp,
    formatDuration,
    formatBytes,
    escapeHtml,
    getStatusBadgeClass,
    getPassRateBadgeClass,
    createGradient,
    getChartDefaults,
    showNotification,
    showLoading,
    hideLoading,
    startAutoRefresh,
    stopAutoRefresh,
    saveToLocalStorage,
    loadFromLocalStorage
};

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🤖 Robot Framework Metrics Dashboard loaded');
    console.log('Version: 1.0.0');
});

// Handle page visibility change for auto-refresh
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        console.log('Page hidden - pausing auto-refresh');
    } else {
        console.log('Page visible - resuming auto-refresh');
    }
});

// Global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
});

// Export for direct use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.DashboardUtils;
}
