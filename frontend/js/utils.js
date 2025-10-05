/**
 * Utility functions for Sky Forecaster application.
 */

/**
 * Validate location input string.
 * @param {string} locationInput - Location input string
 * @returns {Object} Validation result with isValid, error, lat, lon
 */
function validateLocationInput(locationInput) {
    if (!locationInput || typeof locationInput !== 'string') {
        return {
            isValid: false,
            error: 'Location input is required',
            lat: null,
            lon: null
        };
    }

    const trimmedInput = locationInput.trim();
    
    // Check if input is coordinates (lat, lon format)
    if (trimmedInput.includes(',')) {
        try {
            const coords = trimmedInput.split(',');
            if (coords.length === 2) {
                const lat = parseFloat(coords[0].trim());
                const lon = parseFloat(coords[1].trim());
                
                if (isValidCoordinates(lat, lon)) {
                    return {
                        isValid: true,
                        error: null,
                        lat: lat,
                        lon: lon
                    };
                } else {
                    return {
                        isValid: false,
                        error: 'Invalid coordinate values. Latitude must be between -90 and 90, longitude between -180 and 180',
                        lat: null,
                        lon: null
                    };
                }
            }
        } catch (error) {
            return {
                isValid: false,
                error: 'Invalid coordinate format. Use "latitude, longitude"',
                lat: null,
                lon: null
            };
        }
    }
    
    // For address input, we'll let the geocoding service handle validation
    return {
        isValid: true,
        error: null,
        lat: null,
        lon: null
    };
}

/**
 * Validate latitude and longitude coordinates.
 * @param {number} latitude - Latitude value
 * @param {number} longitude - Longitude value
 * @returns {boolean} True if coordinates are valid
 */
function isValidCoordinates(latitude, longitude) {
    if (typeof latitude !== 'number' || typeof longitude !== 'number') {
        return false;
    }
    
    if (isNaN(latitude) || isNaN(longitude)) {
        return false;
    }
    
    return latitude >= -90 && latitude <= 90 && longitude >= -180 && longitude <= 180;
}

/**
 * Get current geolocation from browser.
 * @returns {Promise<Object>} Promise that resolves with coordinates
 */
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation is not supported by this browser'));
            return;
        }

        const options = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 300000 // 5 minutes
        };

        navigator.geolocation.getCurrentPosition(
            (position) => {
                resolve({
                    lat: position.coords.latitude,
                    lon: position.coords.longitude
                });
            },
            (error) => {
                let errorMessage;
                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage = 'Location access denied by user';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage = 'Location information is unavailable';
                        break;
                    case error.TIMEOUT:
                        errorMessage = 'Location request timed out';
                        break;
                    default:
                        errorMessage = 'An unknown error occurred while retrieving location';
                        break;
                }
                reject(new Error(errorMessage));
            },
            options
        );
    });
}

/**
 * Format AQI value with appropriate styling.
 * @param {number} aqi - AQI value
 * @returns {Object} Formatted AQI data
 */
function formatAQI(aqi) {
    let category, color, description;
    
    if (aqi <= 50) {
        category = 'Good';
        color = '#00e400';
        description = 'Air quality is satisfactory';
    } else if (aqi <= 100) {
        category = 'Moderate';
        color = '#ffff00';
        description = 'Air quality is acceptable';
    } else if (aqi <= 150) {
        category = 'Unhealthy for Sensitive Groups';
        color = '#ff7e00';
        description = 'Members of sensitive groups may experience health effects';
    } else if (aqi <= 200) {
        category = 'Unhealthy';
        color = '#ff0000';
        description = 'Everyone may experience health effects';
    } else if (aqi <= 300) {
        category = 'Very Unhealthy';
        color = '#8f3f97';
        description = 'Health warnings of emergency conditions';
    } else {
        category = 'Hazardous';
        color = '#7e0023';
        description = 'Health alert: everyone may experience serious health effects';
    }
    
    return {
        value: aqi,
        category: category,
        color: color,
        description: description
    };
}

/**
 * Format timestamp for display.
 * @param {string} timestamp - ISO timestamp string
 * @returns {string} Formatted timestamp
 */
function formatTimestamp(timestamp) {
    try {
        const date = new Date(timestamp);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            timeZoneName: 'short'
        });
    } catch (error) {
        return 'Invalid timestamp';
    }
}

/**
 * Format date for forecast display.
 * @param {string} timestamp - ISO timestamp string
 * @returns {string} Formatted date
 */
function formatForecastDate(timestamp) {
    try {
        const date = new Date(timestamp);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return 'Invalid date';
    }
}

/**
 * Format pollutant concentration value.
 * @param {number} value - Concentration value
 * @param {string} pollutant - Pollutant type
 * @returns {string} Formatted value with units
 */
function formatPollutantValue(value, pollutant) {
    if (value === null || value === undefined || isNaN(value)) {
        return 'N/A';
    }
    
    const units = {
        'pm25': 'μg/m³',
        'pm10': 'μg/m³',
        'no2': 'μg/m³',
        'o3': 'μg/m³',
        'co': 'mg/m³',
        'so2': 'μg/m³'
    };
    
    return `${value.toFixed(1)} ${units[pollutant] || ''}`;
}

/**
 * Format weather value with units.
 * @param {number} value - Weather value
 * @param {string} type - Weather type
 * @returns {string} Formatted value with units
 */
function formatWeatherValue(value, type) {
    if (value === null || value === undefined || isNaN(value)) {
        return 'N/A';
    }
    
    const units = {
        'temperature': '°C',
        'humidity': '%',
        'pressure': 'hPa',
        'wind_speed': 'm/s',
        'wind_direction': '°'
    };
    
    return `${value.toFixed(1)}${units[type] || ''}`;
}

/**
 * Debounce function to limit API calls.
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Show loading indicator.
 * @param {boolean} show - Whether to show loading
 */
function showLoading(show = true) {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        if (show) {
            loadingIndicator.classList.add('show');
        } else {
            loadingIndicator.classList.remove('show');
        }
    }
}

/**
 * Show error message.
 * @param {string} message - Error message to display
 */
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    const errorText = errorMessage.querySelector('.error-text');
    
    if (errorMessage && errorText) {
        errorText.textContent = message;
        errorMessage.classList.add('show');
    }
}

/**
 * Hide error message.
 */
function hideError() {
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.classList.remove('show');
    }
}

/**
 * Show location error.
 * @param {string} message - Error message to display
 */
function showLocationError(message) {
    const locationError = document.getElementById('locationError');
    if (locationError) {
        locationError.textContent = message;
        locationError.classList.add('show');
    }
}

/**
 * Hide location error.
 */
function hideLocationError() {
    const locationError = document.getElementById('locationError');
    if (locationError) {
        locationError.classList.remove('show');
    }
}

/**
 * Make API request with error handling.
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} Promise that resolves with response data
 */
async function apiRequest(url, options = {}) {
    try {
        console.log('Making API request to:', url);
        
        const fetchOptions = {
            method: options.method || 'GET',
            headers: {
                'Accept': 'application/json',
                ...options.headers
            },
            mode: 'cors',
            credentials: 'omit'
        };
        
        // Only add Content-Type for non-GET requests with body
        if (options.body && options.method !== 'GET') {
            fetchOptions.headers['Content-Type'] = 'application/json';
        }
        
        // Only add body for non-GET requests
        if (options.body && options.method !== 'GET') {
            fetchOptions.body = options.body;
        }
        
        console.log('Fetch options:', fetchOptions);
        
        const response = await fetch(url, fetchOptions);
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`HTTP error! status: ${response.status}, response: ${errorText}`);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

/**
 * Get API base URL.
 * @returns {string} API base URL
 */
function getApiBaseUrl() {
    // In development, use localhost
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:5000/api';
    }
    
    // For file:// protocol (opening HTML directly), use localhost
    if (window.location.protocol === 'file:') {
        return 'http://localhost:5000/api';
    }
    
    // In production, use relative URL
    return '/api';
}

/**
 * Utility function to check if element exists.
 * @param {string} selector - CSS selector
 * @returns {boolean} True if element exists
 */
function elementExists(selector) {
    return document.querySelector(selector) !== null;
}

/**
 * Utility function to safely get element.
 * @param {string} selector - CSS selector
 * @returns {Element|null} Element or null if not found
 */
function getElement(selector) {
    return document.querySelector(selector);
}

/**
 * Utility function to safely get elements.
 * @param {string} selector - CSS selector
 * @returns {NodeList} Elements
 */
function getElements(selector) {
    return document.querySelectorAll(selector);
}
