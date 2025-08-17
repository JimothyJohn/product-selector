// Step 3: Basic filtering functionality

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    loadConfiguration();
    addEventListeners();
});

// Load configuration
function loadConfiguration() {
    apiEndpoint = localStorage.getItem('apiEndpoint') || '';
    apiKey = localStorage.getItem('apiKey') || '';

    if (!apiEndpoint) {
        showStatus('error', '❌ No API configuration found. Please go back to Step 1 to configure your API endpoint.');
        return;
    }
}

// Add event listeners
function addEventListeners() {
    // Add change listeners for dropdowns
    const categoryFilter = document.getElementById('categoryFilter');
    const typeFilter = document.getElementById('typeFilter');
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', updateActiveFilters);
    }
    if (typeFilter) {
        typeFilter.addEventListener('change', updateActiveFilters);
    }
}

// Build query parameters from basic filters
function buildQueryParams() {
    const params = new URLSearchParams();
    
    const category = getElementValue('categoryFilter');
    const type = getElementValue('typeFilter');

    if (category) params.append('category', category);
    if (type) params.append('type', type);

    return params;
}

// Update active filters display (simplified for step 3)
function updateActiveFilters() {
    const params = buildQueryParams();
    const activeFiltersDiv = document.getElementById('activeFilters');
    const filterTagsDiv = document.getElementById('filterTags');

    if (!activeFiltersDiv || !filterTagsDiv) return;

    if (params.toString()) {
        const tags = [];
        for (const [key, value] of params) {
            tags.push(`<span class="filter-tag">${key}: ${value}</span>`);
        }
        filterTagsDiv.innerHTML = tags.join('');
        activeFiltersDiv.style.display = 'block';
    } else {
        activeFiltersDiv.style.display = 'none';
    }
}

// Apply filters
async function applyFilters() {
    if (!validateApiConfiguration()) {
        return;
    }

    const params = buildQueryParams();
    
    if (!params.toString()) {
        showStatus('error', '⚠️ Please select at least one filter to apply.');
        return;
    }

    showStatus('loading', '🔄 Applying filters and fetching data...');
    hideResults();

    try {
        // Build URL with query parameters
        const url = `${apiEndpoint}?${params}`;
        console.log('Fetching filtered data from:', url);

        const data = await makeApiCall(url);
        
        showStatus('success', '✅ Filters applied successfully!');
        displayResults(data);

    } catch (error) {
        console.error('Error applying filters:', error);
        showStatus('error', `❌ Failed to apply filters: ${error.message}`);
    }
}

// Show all data (no filters)
async function showAllData() {
    showStatus('loading', '🔄 Fetching all data...');
    hideResults();

    try {
        const data = await makeApiCall(apiEndpoint);
        
        showStatus('success', '✅ All data fetched successfully!');
        displayResults(data);

    } catch (error) {
        console.error('Error fetching all data:', error);
        showStatus('error', `❌ Failed to fetch data: ${error.message}`);
    }
}

// Clear all filters (step 3 specific)
function clearFilters() {
    const categoryFilter = document.getElementById('categoryFilter');
    const typeFilter = document.getElementById('typeFilter');
    
    if (categoryFilter) categoryFilter.value = '';
    if (typeFilter) typeFilter.value = '';
    
    updateActiveFilters();
    hideResults();
    
    const statusDiv = document.getElementById('status');
    if (statusDiv) {
        statusDiv.style.display = 'none';
    }
}