// Display functions for rendering API data

// Display search results
function displayResults(data) {
    const resultsSection = document.getElementById('results');
    const resultsTitle = document.getElementById('resultsTitle');
    const summaryDiv = document.getElementById('summary');
    const categoriesList = document.getElementById('categoriesList');
    const gearboxesList = document.getElementById('gearboxesList');
    const categoriesSection = document.getElementById('categoriesSection');
    const gearboxesSection = document.getElementById('gearboxesSection');

    if (!resultsSection) return;

    // Update title
    if (resultsTitle) {
        resultsTitle.textContent = data.message || 'Search Results';
    }
    
    // Update summary
    if (summaryDiv) {
        const summary = data.summary || {};
        let summaryContent = `
            <strong>Results Summary:</strong>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 0.5rem;">
                <div>📊 Total Items: <strong>${summary.total_items || 0}</strong></div>
                <div>📂 Categories: <strong>${summary.categories || 0}</strong></div>
                <div>⚙️ Gearboxes: <strong>${summary.gearbox_products || 0}</strong></div>
            </div>
        `;
        
        if (data.filters_applied) {
            summaryContent += `<p style="margin-top: 1rem;"><strong>Filters Applied:</strong> ${Object.entries(data.filters_applied).map(([k,v]) => `${k}: ${v}`).join(', ')}</p>`;
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
                    ${category.PK ? `<p><strong>ID:</strong> ${category.PK}</p>` : ''}
                    ${category.created_at ? `<p><strong>Created:</strong> ${category.created_at}</p>` : ''}
                </div>
            `).join('');
            categoriesSection.style.display = 'block';
        } else {
            categoriesSection.style.display = 'none';
        }
    }

    // Display gearboxes
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
            gearboxesList.innerHTML = '<div class="no-data">No gearboxes found matching your criteria.</div>';
            gearboxesSection.style.display = 'block';
        }
    }

    // Show no results message if nothing found
    if (categories.length === 0 && gearboxes.length === 0 && summaryDiv) {
        summaryDiv.innerHTML += '<div class="no-data">No results found. Try adjusting your filters.</div>';
    }

    resultsSection.style.display = 'block';
}

// Display data for step 2 (slightly different format)
function displayData(data) {
    const resultsDiv = document.getElementById('results');
    const summaryDiv = document.getElementById('summary');
    const categoriesList = document.getElementById('categoriesList');
    const gearboxesList = document.getElementById('gearboxesList');
    const categoriesSection = document.getElementById('categoriesSection');
    const gearboxesSection = document.getElementById('gearboxesSection');

    if (!resultsDiv) return;

    // Display summary
    if (summaryDiv) {
        const summary = data.summary || {};
        summaryDiv.innerHTML = `
            <h3>${data.message || 'Catalog Data Retrieved'}</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem;">
                <div><strong>📊 Total Items:</strong> ${summary.total_items || 0}</div>
                <div><strong>📂 Categories:</strong> ${summary.categories || 0}</div>
                <div><strong>⚙️ Gearboxes:</strong> ${summary.gearbox_products || 0}</div>
            </div>
            ${data.filters_applied ? `<p style="margin-top: 1rem;"><strong>Filters Applied:</strong> ${JSON.stringify(data.filters_applied)}</p>` : ''}
        `;
    }

    // Display categories
    const categories = data.categories || [];
    if (categoriesSection && categoriesList) {
        if (categories.length > 0) {
            categoriesList.innerHTML = categories.map((category, index) => `
                <div class="data-item">
                    <h4>${category.category_name || 'Unknown Category'}</h4>
                    <p><strong>Description:</strong> ${category.description || 'No description available'}</p>
                    <p><strong>ID:</strong> ${category.PK || 'N/A'}</p>
                    ${category.created_at ? `<p><strong>Created:</strong> ${category.created_at}</p>` : ''}
                </div>
            `).join('');
            categoriesSection.style.display = 'block';
        } else {
            categoriesList.innerHTML = '<div class="no-data">No categories found in the data.</div>';
            categoriesSection.style.display = 'block';
        }
    }

    // Display gearboxes
    const gearboxes = data.gearboxes || [];
    if (gearboxesSection && gearboxesList) {
        if (gearboxes.length > 0) {
            gearboxesList.innerHTML = gearboxes.map((gearbox, index) => `
                <div class="data-item">
                    <h4>${gearbox.model_name || 'Unknown Model'}</h4>
                    <p><strong>Manufacturer:</strong> ${gearbox.manufacturer || 'Unknown'}</p>
                    <div class="data-specs">
                        <div class="spec-item"><strong>🔧 Type:</strong> ${gearbox.gearbox_type || 'N/A'}</div>
                        <div class="spec-item"><strong>💪 Torque:</strong> ${gearbox.torque_rating || 'N/A'} Nm</div>
                        <div class="spec-item"><strong>⚡ Performance:</strong> ${gearbox.performance_rating || 'N/A'}%</div>
                        <div class="spec-item"><strong>🎯 Application:</strong> ${gearbox.application_type || 'N/A'}</div>
                        <div class="spec-item"><strong>💰 Price Range:</strong> ${gearbox.price_range || 'N/A'}</div>
                        <div class="spec-item"><strong>🆔 ID:</strong> ${gearbox.gearbox_id || 'N/A'}</div>
                    </div>
                </div>
            `).join('');
            gearboxesSection.style.display = 'block';
        } else {
            gearboxesList.innerHTML = '<div class="no-data">No gearboxes found in the data.</div>';
            gearboxesSection.style.display = 'block';
        }
    }

    // Show no results message if nothing found
    if (categories.length === 0 && gearboxes.length === 0 && summaryDiv) {
        summaryDiv.innerHTML += '<div class="no-data">No data found. The API may be empty or there may be an issue with the response format.</div>';
    }

    resultsDiv.style.display = 'block';
}