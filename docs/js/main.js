// Main page functionality

// Global variables
let currentData = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    addEventListeners();
});

// Add event listeners
function addEventListeners() {
    // Store configuration on change
    const endpointInput = document.getElementById('apiEndpoint');
    const keyInput = document.getElementById('apiKey');
    
    if (endpointInput) {
        endpointInput.addEventListener('change', storeConfiguration);
    }
    if (keyInput) {
        keyInput.addEventListener('change', storeConfiguration);
    }

    // Add filter event listeners
    addFilterEventListeners();

    // Add enter key support for input filters
    const inputElements = ['manufacturerFilter', 'minTorqueFilter', 'minPerformanceFilter'];
    inputElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchGearboxes();
                }
            });
        }
    });
}

// Search for gearboxes
async function searchGearboxes() {
    const apiEndpointInput = document.getElementById('apiEndpoint');
    const apiKeyInput = document.getElementById('apiKey');
    
    if (!apiEndpointInput) return;
    
    const endpoint = apiEndpointInput.value;
    const key = apiKeyInput ? apiKeyInput.value : '';

    // Validate API endpoint
    if (!endpoint) {
        showError('Please enter an API endpoint URL');
        return;
    }

    // Store configuration
    apiEndpoint = endpoint;
    apiKey = key;
    storeConfiguration();

    // Show loading state
    showLoading(true);
    hideError();
    hideResults();

    try {
        // Build URL with query parameters
        const params = buildQueryParams();
        const url = params.toString() ? `${endpoint}?${params}` : endpoint;

        // Prepare headers
        const headers = {
            'Content-Type': 'application/json'
        };
        if (key) {
            headers['x-api-key'] = key;
        }

        // Make API call
        const response = await fetch(url, {
            method: 'GET',
            headers: headers
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        currentData = data;

        // Update UI
        updateActiveFilters();
        displayResults(data);

    } catch (error) {
        console.error('Error fetching data:', error);
        showError(`Failed to fetch data: ${error.message}`);
    } finally {
        showLoading(false);
    }
}