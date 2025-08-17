// Common utilities and functions shared across all pages

// Global configuration
let apiEndpoint = '';
let apiKey = '';

// Initialize common functionality
document.addEventListener('DOMContentLoaded', function() {
    loadStoredConfiguration();
});

// Load stored configuration from localStorage
function loadStoredConfiguration() {
    apiEndpoint = localStorage.getItem('apiEndpoint') || '';
    apiKey = localStorage.getItem('apiKey') || '';
    
    // Update UI elements if they exist
    const endpointInput = document.getElementById('apiEndpoint');
    const keyInput = document.getElementById('apiKey');
    
    if (endpointInput && apiEndpoint) {
        endpointInput.value = apiEndpoint;
    }
    if (keyInput && apiKey) {
        keyInput.value = apiKey;
    }
}

// Store configuration to localStorage
function storeConfiguration() {
    const endpointInput = document.getElementById('apiEndpoint');
    const keyInput = document.getElementById('apiKey');
    
    if (endpointInput) {
        apiEndpoint = endpointInput.value;
        localStorage.setItem('apiEndpoint', apiEndpoint);
    }
    if (keyInput) {
        apiKey = keyInput.value;
        localStorage.setItem('apiKey', apiKey);
    }
}

// Show status message
function showStatus(type, message) {
    const statusDiv = document.getElementById('status');
    if (statusDiv) {
        statusDiv.className = `status ${type}`;
        statusDiv.textContent = message;
        statusDiv.style.display = 'block';
    }
}

// Show loading state
function showLoading(show) {
    const loadingDiv = document.getElementById('loading');
    if (loadingDiv) {
        loadingDiv.style.display = show ? 'block' : 'none';
    }
}

// Show/hide error
function showError(message) {
    const errorDiv = document.getElementById('error');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}

function hideError() {
    const errorDiv = document.getElementById('error');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

// Hide results
function hideResults() {
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.style.display = 'none';
    }
}

// Make API call with proper headers
async function makeApiCall(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (apiKey) {
        headers['x-api-key'] = apiKey;
    }
    
    const response = await fetch(url, {
        method: 'GET',
        headers: headers,
        ...options
    });
    
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
}

// Validate API configuration
function validateApiConfiguration() {
    if (!apiEndpoint) {
        showStatus('error', '❌ API endpoint not configured. Please configure your API endpoint first.');
        return false;
    }
    return true;
}

// Add event listeners for configuration changes
function addConfigurationListeners() {
    const endpointInput = document.getElementById('apiEndpoint');
    const keyInput = document.getElementById('apiKey');
    
    if (endpointInput) {
        endpointInput.addEventListener('change', storeConfiguration);
    }
    if (keyInput) {
        keyInput.addEventListener('change', storeConfiguration);
    }
}