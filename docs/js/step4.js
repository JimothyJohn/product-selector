// Step 4: Advanced filtering functionality

// Global variables
let currentResults = null;

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
    addFilterEventListeners();

    // Add enter key support for input fields
    const inputElements = ['manufacturerFilter', 'minTorqueFilter', 'minPerformanceFilter'];
    inputElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') applyFilters();
            });
        }
    });
}

// Apply preset filters
function applyPreset(preset) {
    // Clear current filters first
    clearFiltersOnly();

    switch(preset) {
        case 'high-performance':
            const perfElement = document.getElementById('minPerformanceFilter');
            if (perfElement) perfElement.value = '90';
            break;
        case 'heavy-duty':
            const torqueElement = document.getElementById('minTorqueFilter');
            if (torqueElement) torqueElement.value = '3000';
            break;
        case 'automotive-planetary':
            const catElement = document.getElementById('categoryFilter');
            const typeElement = document.getElementById('typeFilter');
            if (catElement) catElement.value = 'automotive';
            if (typeElement) typeElement.value = 'planetary';
            break;
        case 'budget-friendly':
            const priceElement = document.getElementById('priceRangeFilter');
            if (priceElement) priceElement.value = 'low';
            break;
        case 'industrial-helical':
            const indCatElement = document.getElementById('categoryFilter');
            const indTypeElement = document.getElementById('typeFilter');
            if (indCatElement) indCatElement.value = 'industrial';
            if (indTypeElement) indTypeElement.value = 'helical';
            break;
    }
    
    updateActiveFilters();
    applyFilters();
}

// Apply filters
async function applyFilters() {
    if (!validateApiConfiguration()) {
        return;
    }

    const params = buildQueryParams();
    showStatus('loading', '🔄 Applying filters and fetching data...');
    hideResults();

    try {
        // Build URL with query parameters
        const url = params.toString() ? `${apiEndpoint}?${params}` : apiEndpoint;
        console.log('Fetching filtered data from:', url);

        const data = await makeApiCall(url);
        currentResults = data;
        
        const filterCount = Array.from(params).length;
        const successMessage = filterCount > 0 ? 
            `✅ Filters applied successfully! (${filterCount} filter${filterCount > 1 ? 's' : ''} active)` : 
            '✅ All data fetched successfully!';
        
        showStatus('success', successMessage);
        displayResults(data);

        // Show export button if there are results
        const exportBtn = document.getElementById('exportBtn');
        if (exportBtn) {
            exportBtn.style.display = 'inline-block';
        }

    } catch (error) {
        console.error('Error applying filters:', error);
        showStatus('error', `❌ Failed to apply filters: ${error.message}`);
    }
}

// Show all data (no filters)
async function showAllData() {
    clearFiltersOnly();
    await applyFilters();
}

// Export results to JSON
function exportResults() {
    if (!currentResults) {
        showStatus('error', '❌ No results to export. Please run a search first.');
        return;
    }

    const dataStr = JSON.stringify(currentResults, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `gearbox-search-results-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    showStatus('success', '✅ Results exported successfully!');
}

// Enhanced display results with emojis (step 4 specific)
function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    const resultsTitle = document.getElementById('resultsTitle');
    const summaryDiv = document.getElementById('summary');
    const categoriesList = document.getElementById('categoriesList');
    const gearboxesList = document.getElementById('gearboxesList');
    const categoriesSection = document.getElementById('categoriesSection');
    const gearboxesSection = document.getElementById('gearboxesSection');

    if (!resultsDiv) return;

    // Update title and summary
    if (resultsTitle) {
        resultsTitle.textContent = data.message || 'Search Results';
    }
    
    if (summaryDiv) {
        const summary = data.summary || {};
        let summaryContent = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                <div><strong>📊 Total Items:</strong> ${summary.total_items || 0}</div>
                <div><strong>📂 Categories:</strong> ${summary.categories || 0}</div>
                <div><strong>⚙️ Gearboxes:</strong> ${summary.gearbox_products || 0}</div>
            </div>
        `;

        if (data.filters_applied) {
            summaryContent += `<div style="margin-top: 1rem; padding: 0.75rem; background: rgba(102, 126, 234, 0.1); border-radius: 5px; border-left: 4px solid #667eea;">
                <strong>🔍 Active Filters:</strong> ${Object.entries(data.filters_applied).map(([k,v]) => `${k}: ${v}`).join(', ')}
            </div>`;
        }

        summaryDiv.innerHTML = summaryContent;
    }

    // Display categories
    const categories = data.categories || [];
    if (categoriesSection && categoriesList) {
        if (categories.length > 0) {
            categoriesList.innerHTML = categories.map(category => `
                <div class="data-item">
                    <h4>📂 ${category.category_name || 'Unknown Category'}</h4>
                    <p><strong>Description:</strong> ${category.description || 'No description available'}</p>
                </div>
            `).join('');
            categoriesSection.style.display = 'block';
        } else {
            categoriesSection.style.display = 'none';
        }
    }

    // Display gearboxes with enhanced formatting
    const gearboxes = data.gearboxes || [];
    if (gearboxesSection && gearboxesList) {
        if (gearboxes.length > 0) {
            gearboxesList.innerHTML = gearboxes.map(gearbox => `
                <div class="data-item">
                    <h4>⚙️ ${gearbox.model_name || 'Unknown Model'}</h4>
                    <p><strong>🏢 Manufacturer:</strong> ${gearbox.manufacturer || 'Unknown'}</p>
                    <div class="data-specs">
                        <div class="spec-item"><strong>🔧 Type:</strong> ${gearbox.gearbox_type || 'N/A'}</div>
                        <div class="spec-item"><strong>💪 Torque:</strong> ${gearbox.torque_rating || 'N/A'} Nm</div>
                        <div class="spec-item"><strong>⚡ Performance:</strong> ${gearbox.performance_rating || 'N/A'}%</div>
                        <div class="spec-item"><strong>🎯 Application:</strong> ${gearbox.application_type || 'N/A'}</div>
                        <div class="spec-item"><strong>💰 Price:</strong> ${gearbox.price_range || 'N/A'}</div>
                        <div class="spec-item"><strong>🆔 ID:</strong> ${gearbox.gearbox_id || 'N/A'}</div>
                    </div>
                </div>
            `).join('');
            gearboxesSection.style.display = 'block';
        } else {
            gearboxesList.innerHTML = '<div class="no-data">No gearboxes found matching your criteria. Try adjusting your filters or using preset searches.</div>';
            gearboxesSection.style.display = 'block';
        }
    }

    resultsDiv.style.display = 'block';
    updateActiveFilters();
}

// Clear all filters and results (step 4 specific)
function clearFilters() {
    clearFiltersOnly();
    hideResults();
    
    const statusDiv = document.getElementById('status');
    const exportBtn = document.getElementById('exportBtn');
    
    if (statusDiv) statusDiv.style.display = 'none';
    if (exportBtn) exportBtn.style.display = 'none';
    
    currentResults = null;
}