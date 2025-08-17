// Step 1: Connection testing functionality

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    addConfigurationListeners();
    
    // Load stored configuration
    loadStoredConfiguration();
    updateConfigDisplay();
});

// Update configuration display
function updateConfigDisplay() {
    const currentEndpoint = document.getElementById('currentEndpoint');
    const currentApiKey = document.getElementById('currentApiKey');
    
    if (currentEndpoint) {
        currentEndpoint.textContent = apiEndpoint || 'Not configured';
    }
    if (currentApiKey) {
        currentApiKey.textContent = apiKey ? '••••••••' : 'Not set';
    }
}

// Test API connection
async function testConnection() {
    if (!validateApiConfiguration()) {
        return;
    }

    // Store current configuration
    storeConfiguration();

    showStatus('loading', '🔄 Testing connection to API endpoint...');

    try {
        console.log('Testing connection to:', apiEndpoint);
        
        const data = await makeApiCall(apiEndpoint);
        
        showStatus('success', `✅ Connection successful! Found ${data.summary?.total_items || 0} items in catalog.`);
        
        // Show next step button
        const nextStep = document.getElementById('nextStep');
        if (nextStep) {
            nextStep.style.display = 'inline-block';
        }

    } catch (error) {
        console.error('Connection test failed:', error);
        showStatus('error', `❌ Connection failed: ${error.message}`);
    }
}

// Add event listeners for configuration inputs
function addConfigurationListeners() {
    const endpointInput = document.getElementById('apiEndpoint');
    const keyInput = document.getElementById('apiKey');
    
    if (endpointInput) {
        endpointInput.addEventListener('change', function() {
            storeConfiguration();
            updateConfigDisplay();
        });
        endpointInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                testConnection();
            }
        });
    }
    
    if (keyInput) {
        keyInput.addEventListener('change', function() {
            storeConfiguration();
            updateConfigDisplay();
        });
        keyInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                testConnection();
            }
        });
    }
}