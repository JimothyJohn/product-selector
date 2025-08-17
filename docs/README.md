# Gearbox Catalog Frontend

A progressive web interface for testing and interacting with the Gearbox Catalog API, split into modular CSS and JavaScript files.

## 🚀 Quick Start

### Using Caddy Web Server
```bash
# Install Caddy (if not already installed)
# On Ubuntu/Debian:
sudo apt install caddy

# Or download from https://caddyserver.com/

# Start the web server
cd docs
caddy run

# Open in browser: http://localhost:8080
```

### Alternative: Simple HTTP Server
```bash
# Python 3
cd docs
python3 -m http.server 8080

# Node.js (if you have npm/npx)
cd docs
npx http-server -p 8080

# Open in browser: http://localhost:8080
```

## 📁 Project Structure

```
docs/
├── css/                    # Stylesheets
│   ├── common.css         # Shared styles across all pages
│   ├── filters.css        # Filter-specific styles
│   ├── main.css          # Main page styles
│   └── steps.css         # Step page styles
├── js/                    # JavaScript modules
│   ├── common.js         # Common utilities and API functions
│   ├── display.js        # Data display and rendering functions
│   ├── filters.js        # Filter management functions
│   ├── main.js          # Main page functionality
│   ├── step1.js         # Connection testing
│   ├── step2.js         # Data querying
│   ├── step3.js         # Basic filtering
│   └── step4.js         # Advanced filtering
├── media/                 # Media assets
│   ├── images/           # Images and graphics
│   ├── icons/           # SVG icons
│   └── fonts/           # Custom fonts
├── index.html            # Main interface (complete functionality)
├── step1-connection.html # Step 1: API connection test
├── step2-querying.html   # Step 2: Data querying
├── step3-filtering.html  # Step 3: Basic filtering
├── step4-advanced.html   # Step 4: Advanced filtering
├── Caddyfile            # Web server configuration
└── README.md            # This file
```

## 🧭 Progressive Tutorial

### For New Users
Start with the step-by-step tutorial to learn and test each feature:

1. **Step 1: Connection Test** (`step1-connection.html`)
   - Configure API endpoint and authentication
   - Test basic connectivity

2. **Step 2: Data Querying** (`step2-querying.html`)
   - Fetch and display all catalog data
   - View categories and gearboxes

3. **Step 3: Basic Filtering** (`step3-filtering.html`)
   - Learn basic filtering with category and type
   - Understand query parameters

4. **Step 4: Advanced Filtering** (`step4-advanced.html`)
   - Complete filtering system with all options
   - Preset searches and export functionality

### For Production Use
Use the main interface (`index.html`) which includes all features in one page.

## 🔧 Configuration

### API Endpoint
Set your AWS API Gateway endpoint URL:
```
https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/Prod/gearboxes
```

### API Key (Optional)
If your API requires authentication, enter your API key in the configuration section.

### Browser Storage
Configuration is automatically saved to localStorage and persists between sessions.

## 🎯 Features

### Filtering Options
- **Category**: automotive, industrial, marine
- **Type**: planetary, helical, worm, spur
- **Manufacturer**: text search
- **Torque Rating**: minimum value in Nm
- **Performance Rating**: minimum percentage
- **Price Range**: low, medium, high

### Preset Searches
- 🚀 High Performance (>90%)
- 💪 Heavy Duty (>3000 Nm)
- 🚗 Automotive Planetary
- 💰 Budget Friendly (Low Price)
- 🏭 Industrial Helical

### Export Functionality
- JSON export of search results
- Timestamped filename
- Complete data structure

## 🔄 API Integration

The frontend makes RESTful API calls to your Lambda function:

```javascript
// Example API call
GET /gearboxes?category=automotive&type=planetary
```

### Headers
- `Content-Type: application/json`
- `x-api-key: your-api-key` (if configured)

### Expected Response Format
```json
{
  "message": "Filtered gearbox catalog data",
  "summary": {
    "total_items": 25,
    "categories": 1,
    "gearbox_products": 24
  },
  "filters_applied": {
    "category": "automotive",
    "type": "planetary"
  },
  "categories": [...],
  "gearboxes": [...]
}
```

## 🎨 Styling

### CSS Architecture
- **common.css**: Base styles, layout, forms, buttons
- **main.css**: Main page specific styles (step links, results)
- **filters.css**: Filter components, preset buttons, active filters
- **steps.css**: Step-specific styles, configuration displays

### Responsive Design
- Mobile-first approach
- CSS Grid and Flexbox layouts
- Responsive breakpoints at 768px

### Color Scheme
- Primary: `#667eea` (purple-blue gradient)
- Secondary: `#6c757d` (gray)
- Success: `#28a745` (green)
- Error: `#721c24` (red)

## 🖥️ Browser Support

### Modern Browsers
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

### Required Features
- ES6+ JavaScript (async/await, arrow functions, destructuring)
- CSS Grid and Flexbox
- Fetch API
- localStorage

## 🔒 Security Considerations

### CORS Configuration
The Caddyfile includes CORS headers for cross-origin requests:
```
Access-Control-Allow-Origin "*"
Access-Control-Allow-Headers "Content-Type, Authorization, x-api-key"
```

### API Key Storage
- API keys stored in browser localStorage
- Keys are masked in the UI display
- Keys are sent only in HTTP headers, never in URLs

### Content Security
- No inline JavaScript execution
- All scripts loaded from relative paths
- No external CDN dependencies

## 🐛 Troubleshooting

### Common Issues

**Connection Failed**
- Verify API endpoint URL is correct
- Check API key if authentication required
- Ensure CORS headers are configured on API Gateway

**No Data Displayed**
- Check browser console for errors
- Verify API response format matches expected structure
- Test API endpoint directly with curl or Postman

**Filters Not Working**
- Ensure query parameters are supported by backend
- Check filter values match expected format
- Verify backend filtering logic is implemented

### Debug Mode
Open browser Developer Tools (F12) to view:
- Network requests to API
- JavaScript console logs
- API response data
- localStorage configuration

## 📝 Development

### Adding New Filters
1. Add filter to `filters.css` for styling
2. Update `buildQueryParams()` in `filters.js`
3. Add form element to HTML files
4. Update backend to handle new parameter

### Modifying Styles
- Edit appropriate CSS file in `/css/` directory
- Use existing CSS custom properties for consistency
- Test on mobile breakpoints

### Adding New Features
1. Add JavaScript to appropriate module in `/js/`
2. Update HTML structure if needed
3. Add corresponding CSS styles
4. Test across all step pages

## 🚀 Deployment

### Static Hosting
The frontend is completely static and can be deployed to:
- AWS S3 + CloudFront
- Netlify
- Vercel
- GitHub Pages
- Any static web hosting service

### Build Process
No build process required - files are ready to serve as-is.

### Production Checklist
- [ ] API endpoint configured correctly
- [ ] CORS headers enabled on API Gateway
- [ ] API key authentication working (if required)
- [ ] All step tutorial pages functional
- [ ] Main interface working with full filtering
- [ ] Mobile responsive design tested
- [ ] Browser compatibility verified

## 📖 API Documentation

For backend API implementation details, see:
- `../lambda/app/app.py` - Lambda function with filtering logic
- `../lambda/template.yaml` - SAM template with API Gateway configuration
- `../CLAUDE.md` - Complete project documentation