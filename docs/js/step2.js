// Step 2: Data querying functionality

// Global variables
let currentData = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    loadConfiguration();
});

// Load configuration from localStorage
function loadConfiguration() {
    apiEndpoint = localStorage.getItem('apiEndpoint') || '';
    apiKey = localStorage.getItem('apiKey') || '';

    const currentEndpoint = document.getElementById('currentEndpoint');
    const currentApiKey = document.getElementById('currentApiKey');
    
    if (currentEndpoint) {
        currentEndpoint.textContent = apiEndpoint || 'Not configured';
    }
    if (currentApiKey) {
        currentApiKey.textContent = apiKey ? '••••••••' : 'Not set';
    }

    if (!apiEndpoint) {
        showStatus('error', '❌ No API configuration found. Please go back to Step 1 to configure your API endpoint.');
        return;
    }
}

// Fetch all data from API
async function fetchAllData() {
    if (!validateApiConfiguration()) {
        return;
    }

    showStatus('loading', '🔄 Fetching all data from API...');
    hideResults();

    try {
        console.log('Fetching data from:', apiEndpoint);
        
        const data = await makeApiCall(apiEndpoint);
        currentData = data;

        showStatus('success', '✅ Data fetched successfully!');
        displayData(data);

        // Show next step button
        const nextStep = document.getElementById('nextStep');
        if (nextStep) {
            nextStep.style.display = 'inline-block';
        }

    } catch (error) {
        console.error('Error fetching data:', error);
        showStatus('error', `❌ Failed to fetch data: ${error.message}`);
    }
}

// Clear all data
function clearData() {
    const statusDiv = document.getElementById('status');
    const resultsDiv = document.getElementById('results');
    const nextStep = document.getElementById('nextStep');
    
    if (statusDiv) statusDiv.style.display = 'none';
    if (resultsDiv) resultsDiv.style.display = 'none';
    if (nextStep) nextStep.style.display = 'none';
    
    currentData = null;
}

// Store data for next steps
window.addEventListener('beforeunload', function() {
    if (currentData) {
        localStorage.setItem('sampleData', JSON.stringify(currentData));
    }
});