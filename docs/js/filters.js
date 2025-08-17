// Filter functionality for advanced pages

// Build query parameters from filters
function buildQueryParams() {
    const params = new URLSearchParams();
    
    // Get filter values
    const category = getElementValue('categoryFilter');
    const type = getElementValue('typeFilter');
    const manufacturer = getElementValue('manufacturerFilter');
    const minTorque = getElementValue('minTorqueFilter');
    const minPerformance = getElementValue('minPerformanceFilter');
    const priceRange = getElementValue('priceRangeFilter');

    // Add non-empty values to params
    if (category) params.append('category', category);
    if (type) params.append('type', type);
    if (manufacturer) params.append('manufacturer', manufacturer);
    if (minTorque) params.append('min_torque', minTorque);
    if (minPerformance) params.append('min_performance', minPerformance);
    if (priceRange) params.append('price_range', priceRange);

    return params;
}

// Get element value safely
function getElementValue(id) {
    const element = document.getElementById(id);
    return element ? element.value : '';
}

// Update active filters display
function updateActiveFilters() {
    const params = buildQueryParams();
    const activeFiltersDiv = document.getElementById('activeFilters');
    const filterTagsDiv = document.getElementById('filterTags');

    if (!activeFiltersDiv || !filterTagsDiv) return;

    if (params.toString()) {
        const tags = [];
        for (const [key, value] of params) {
            let displayKey = key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
            tags.push(`<span class="filter-tag">${displayKey}: ${value}</span>`);
        }
        filterTagsDiv.innerHTML = tags.join('');
        activeFiltersDiv.style.display = 'block';
    } else {
        activeFiltersDiv.style.display = 'none';
    }
}

// Clear filters only (don't hide results)
function clearFiltersOnly() {
    const filterIds = [
        'categoryFilter', 'typeFilter', 'manufacturerFilter', 
        'minTorqueFilter', 'minPerformanceFilter', 'priceRangeFilter'
    ];
    
    filterIds.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.value = '';
        }
    });
    
    updateActiveFilters();
}

// Clear all filters and results
function clearFilters() {
    clearFiltersOnly();
    hideResults();
    
    const statusDiv = document.getElementById('status');
    if (statusDiv) {
        statusDiv.style.display = 'none';
    }
    
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.style.display = 'none';
    }
    
    // Clear current results
    if (typeof window.currentResults !== 'undefined') {
        window.currentResults = null;
    }
}

// Add filter event listeners
function addFilterEventListeners() {
    // Filter change listeners
    const filterElements = [
        'categoryFilter', 'typeFilter', 'manufacturerFilter', 
        'minTorqueFilter', 'minPerformanceFilter', 'priceRangeFilter'
    ];
    
    filterElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', updateActiveFilters);
            element.addEventListener('input', updateActiveFilters);
        }
    });

    // Enter key support for input fields
    const inputElements = ['manufacturerFilter', 'minTorqueFilter', 'minPerformanceFilter'];
    inputElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    if (typeof applyFilters === 'function') {
                        applyFilters();
                    }
                }
            });
        }
    });
}