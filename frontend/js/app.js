/**
 * Sky Forecaster - Main Application Logic
 * Built for NASA Space Apps Challenge 2025 "From EarthData to Action"
 */

class SkyForecasterApp {
    constructor() {
        this.currentLocation = null;
        this.currentData = null;
        this.forecastData = null;
        this.isLoading = false;
        this.apiBaseUrl = getApiBaseUrl();
        
        this.init();
    }

    /**
     * Initialize the application.
     */
    init() {
        console.log('Initializing Sky Forecaster App...');
        
        // Initialize event listeners
        this.initEventListeners();
        
        // Initialize map
        this.initMap();
        
        // Initialize navigation
        this.initNavigation();
        
        console.log('Sky Forecaster App initialized successfully');
    }

    /**
     * Initialize event listeners.
     */
    initEventListeners() {
        // Location input events
        const locationInput = document.getElementById('locationInput');
        const searchBtn = document.getElementById('searchLocationBtn');
        const currentLocationBtn = document.getElementById('getCurrentLocationBtn');

        if (locationInput) {
            // Debounced search for better UX
            const debouncedSearch = debounce(() => {
                this.handleLocationInput();
            }, 500);

            locationInput.addEventListener('input', debouncedSearch);
            locationInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handleLocationInput();
                }
            });
        }

        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.handleLocationInput();
            });
        }

        if (currentLocationBtn) {
            currentLocationBtn.addEventListener('click', () => {
                this.useCurrentLocation();
            });
        }

        // Error message close
        const errorClose = document.getElementById('errorClose');
        if (errorClose) {
            errorClose.addEventListener('click', hideError);
        }

        // Test API button
        const testApiBtn = document.getElementById('testApiBtn');
        if (testApiBtn) {
            testApiBtn.addEventListener('click', () => {
                this.testApiConnection();
            });
        }

        // Clear errors button
        const clearErrorBtn = document.getElementById('clearErrorBtn');
        if (clearErrorBtn) {
            clearErrorBtn.addEventListener('click', () => {
                hideError();
                hideLocationError();
            });
        }

        // Forecast hours change
        const forecastHours = document.getElementById('forecastHours');
        if (forecastHours) {
            forecastHours.addEventListener('change', () => {
                if (this.currentLocation) {
                    this.loadForecastData();
                }
            });
        }

        // Map location update events
        document.addEventListener('locationUpdate', (e) => {
            this.handleLocationUpdate(e.detail);
        });
    }

    /**
     * Initialize the map.
     */
    initMap() {
        try {
            // Wait for DOM to be fully loaded
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    this.initMap();
                });
                return;
            }
            
            // Check if Leaflet is available
            if (typeof L === 'undefined') {
                console.error('Leaflet.js not loaded');
                showError('Map library not loaded. Please refresh the page.');
                return;
            }
            
            // Initialize map with default location (New York)
            skyMap.init(40.7128, -74.0060, 10);
            console.log('Map initialized');
        } catch (error) {
            console.error('Failed to initialize map:', error);
            showError('Failed to initialize map. Please refresh the page.');
        }
    }

    /**
     * Initialize navigation functionality.
     */
    initNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const sections = document.querySelectorAll('.section');

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                
                // Update active nav link
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                
                // Show target section
                sections.forEach(section => {
                    if (section.id === targetId) {
                        section.style.display = 'block';
                        section.scrollIntoView({ behavior: 'smooth' });
                    } else if (targetId !== 'current' && section.id !== 'about') {
                        section.style.display = 'none';
                    }
                });
            });
        });

        // Mobile nav toggle
        const navToggle = document.querySelector('.nav-toggle');
        const navMenu = document.querySelector('.nav-menu');
        
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
            });
        }
    }

    /**
     * Handle location input from user.
     */
    async handleLocationInput() {
        const locationInput = document.getElementById('locationInput');
        if (!locationInput) return;

        const inputValue = locationInput.value.trim();
        if (!inputValue) {
            showLocationError('Please enter a location');
            return;
        }

        hideLocationError();

        // Validate input
        const validation = validateLocationInput(inputValue);
        if (!validation.isValid) {
            showLocationError(validation.error);
            return;
        }

        // If coordinates provided directly
        if (validation.lat !== null && validation.lon !== null) {
            this.currentLocation = {
                lat: validation.lat,
                lon: validation.lon
            };
            await this.loadAllData();
            return;
        }

        // Try to geocode the address
        try {
            const geocodingResult = await this.geocodeAddress(inputValue);
            if (geocodingResult) {
                this.currentLocation = {
                    lat: geocodingResult.latitude,
                    lon: geocodingResult.longitude
                };
                await this.loadAllData();
            } else {
                showLocationError('Location not found. Please try a different address or use coordinates.');
            }
        } catch (error) {
            console.error('Geocoding failed:', error);
            showLocationError('Failed to find location. Please try coordinates instead.');
        }
    }

    /**
     * Use current geolocation.
     */
    async useCurrentLocation() {
        try {
            showLoading(true);
            const coords = await getCurrentLocation();
            this.currentLocation = coords;
            
            // Update location input
            const locationInput = document.getElementById('locationInput');
            if (locationInput) {
                locationInput.value = `${coords.lat.toFixed(4)}, ${coords.lon.toFixed(4)}`;
            }
            
            await this.loadAllData();
        } catch (error) {
            console.error('Failed to get current location:', error);
            showError(error.message);
        } finally {
            showLoading(false);
        }
    }

    /**
     * Handle location update from map.
     */
    async handleLocationUpdate(location) {
        this.currentLocation = location;
        
        // Update location input
        const locationInput = document.getElementById('locationInput');
        if (locationInput) {
            locationInput.value = `${location.lat.toFixed(4)}, ${location.lon.toFixed(4)}`;
        }
        
        await this.loadAllData();
    }

    /**
     * Load all data for current location.
     */
    async loadAllData() {
        if (!this.currentLocation) {
            console.error('No location set');
            return;
        }

        try {
            showLoading(true);
            
            // Load current conditions and forecast in parallel
            await Promise.all([
                this.loadCurrentConditions(),
                this.loadForecastData()
            ]);
            
            // Update map
            this.updateMap();
            
        } catch (error) {
            console.error('Failed to load data:', error);
            showError('Failed to load air quality data. Please try again.');
        } finally {
            showLoading(false);
        }
    }

    /**
     * Load current air quality conditions.
     */
    async loadCurrentConditions() {
        try {
            const url = `${this.apiBaseUrl}/current-conditions?lat=${this.currentLocation.lat}&lon=${this.currentLocation.lon}`;
            console.log('Loading current conditions from:', url);
            
            const data = await apiRequest(url);
            console.log('Current conditions data received:', data);
            
            this.currentData = data;
            this.displayCurrentConditions(data);
            
        } catch (error) {
            console.error('Failed to load current conditions:', error);
            
            // Check for specific error types
            let errorMessage = 'Failed to load current air quality data. Using mock data.';
            if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Network error: Cannot connect to backend server. Using mock data.';
            } else if (error.message.includes('CORS')) {
                errorMessage = 'CORS error: Cross-origin request blocked. Using mock data.';
            } else if (error.message.includes('500')) {
                errorMessage = 'Server error: Backend is experiencing issues. Using mock data.';
            }
            
            showError(errorMessage);
            
            // Display mock data as fallback
            this.displayCurrentConditions({
                aqi: 67,
                primary_pollutant: 'o3',
                pm25: 15.5,
                pm10: 45.0,
                no2: 25.0,
                o3: 60.0,
                temperature: 22.5,
                humidity: 65.0,
                wind_speed: 5.2,
                timestamp: new Date().toISOString(),
                source: 'Mock Data (API Error)'
            });
        }
    }

    /**
     * Load forecast data.
     */
    async loadForecastData() {
        try {
            const forecastHours = document.getElementById('forecastHours')?.value || 24;
            const url = `${this.apiBaseUrl}/forecast?lat=${this.currentLocation.lat}&lon=${this.currentLocation.lon}&hours=${forecastHours}`;
            console.log('Loading forecast from:', url);
            
            const data = await apiRequest(url);
            console.log('Forecast data received:', data);
            
            this.forecastData = data;
            this.displayForecast(data);
            
        } catch (error) {
            console.error('Failed to load forecast:', error);
            // Show user-friendly error message
            showError('Failed to load forecast data. Using mock forecast.');
            // Display mock forecast as fallback
            this.displayMockForecast(forecastHours);
        }
    }

    /**
     * Display current air quality conditions.
     */
    displayCurrentConditions(data) {
        const currentContent = document.getElementById('currentContent');
        if (!currentContent) return;

        const aqiData = formatAQI(data.aqi);
        
        currentContent.innerHTML = `
            <div class="current-grid">
                <div class="aqi-card" style="background-color: ${aqiData.color}">
                    <div class="aqi-value">${data.aqi}</div>
                    <div class="aqi-category">${aqiData.category}</div>
                    <div class="aqi-pollutant">Primary: ${data.primary_pollutant.toUpperCase()}</div>
                </div>
                
                <div class="conditions-grid">
                    <div class="condition-item">
                        <div class="condition-value">${formatPollutantValue(data.pm25, 'pm25')}</div>
                        <div class="condition-label">PM2.5</div>
                    </div>
                    <div class="condition-item">
                        <div class="condition-value">${formatPollutantValue(data.pm10, 'pm10')}</div>
                        <div class="condition-label">PM10</div>
                    </div>
                    <div class="condition-item">
                        <div class="condition-value">${formatPollutantValue(data.no2, 'no2')}</div>
                        <div class="condition-label">NO₂</div>
                    </div>
                    <div class="condition-item">
                        <div class="condition-value">${formatPollutantValue(data.o3, 'o3')}</div>
                        <div class="condition-label">O₃</div>
                    </div>
                    <div class="condition-item">
                        <div class="condition-value">${formatWeatherValue(data.temperature, 'temperature')}</div>
                        <div class="condition-label">Temperature</div>
                    </div>
                    <div class="condition-item">
                        <div class="condition-value">${formatWeatherValue(data.humidity, 'humidity')}</div>
                        <div class="condition-label">Humidity</div>
                    </div>
                    <div class="condition-item">
                        <div class="condition-value">${formatWeatherValue(data.wind_speed, 'wind_speed')}</div>
                        <div class="condition-label">Wind Speed</div>
                    </div>
                    <div class="condition-item">
                        <div class="condition-value">${formatTimestamp(data.timestamp)}</div>
                        <div class="condition-label">Last Updated</div>
                    </div>
                    <div class="condition-item">
                        <div class="condition-value" style="font-size: 12px;">${data.source || 'Unknown'}</div>
                        <div class="condition-label">Data Source</div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Display forecast data.
     */
    displayForecast(data) {
        const forecastContent = document.getElementById('forecastContent');
        if (!forecastContent) return;

        if (!data.predictions || data.predictions.length === 0) {
            forecastContent.innerHTML = '<p>No forecast data available.</p>';
            return;
        }

        const forecastCards = data.predictions.map(prediction => {
            const aqiData = formatAQI(prediction.aqi);
            return `
                <div class="forecast-card" style="border-left: 4px solid ${aqiData.color}">
                    <div class="forecast-time">${formatForecastDate(prediction.timestamp)}</div>
                    <div class="forecast-aqi" style="color: ${aqiData.color}">AQI ${prediction.aqi}</div>
                    <div class="forecast-category">${aqiData.category}</div>
                    <div class="forecast-pollutant">Primary: ${prediction.primary_pollutant.toUpperCase()}</div>
                    <div class="forecast-details">
                        <small>
                            PM2.5: ${formatPollutantValue(prediction.pm25, 'pm25')}<br>
                            PM10: ${formatPollutantValue(prediction.pm10, 'pm10')}<br>
                            NO₂: ${formatPollutantValue(prediction.no2, 'no2')}<br>
                            O₃: ${formatPollutantValue(prediction.o3, 'o3')}
                        </small>
                    </div>
                </div>
            `;
        }).join('');

        forecastContent.innerHTML = forecastCards;
    }

    /**
     * Display mock forecast data as fallback.
     */
    displayMockForecast(hours) {
        const forecastContent = document.getElementById('forecastContent');
        if (!forecastContent) return;

        const predictions = [];
        const now = new Date();
        
        for (let i = 0; i < hours; i += 6) {
            const futureTime = new Date(now.getTime() + i * 60 * 60 * 1000);
            const aqi = 67 + Math.floor(Math.random() * 20) - 10; // Random AQI around 67
            const aqiData = formatAQI(aqi);
            
            predictions.push({
                timestamp: futureTime.toISOString(),
                aqi: aqi,
                primary_pollutant: 'o3',
                pm25: 15.5 + (i * 0.1),
                pm10: 45.0 + (i * 0.2),
                no2: 25.0 + (i * 0.1),
                o3: 60.0 + (i * 0.3),
                category: aqiData.category,
                color: aqiData.color
            });
        }

        const forecastCards = predictions.map(prediction => {
            return `
                <div class="forecast-card" style="border-left: 4px solid ${prediction.color}">
                    <div class="forecast-time">${formatForecastDate(prediction.timestamp)}</div>
                    <div class="forecast-aqi" style="color: ${prediction.color}">AQI ${prediction.aqi}</div>
                    <div class="forecast-category">${prediction.category}</div>
                    <div class="forecast-pollutant">Primary: ${prediction.primary_pollutant.toUpperCase()}</div>
                    <div class="forecast-details">
                        <small>
                            PM2.5: ${formatPollutantValue(prediction.pm25, 'pm25')}<br>
                            PM10: ${formatPollutantValue(prediction.pm10, 'pm10')}<br>
                            NO₂: ${formatPollutantValue(prediction.no2, 'no2')}<br>
                            O₃: ${formatPollutantValue(prediction.o3, 'o3')}
                        </small>
                    </div>
                </div>
            `;
        }).join('');

        forecastContent.innerHTML = forecastCards;
    }

    /**
     * Update map with current data.
     */
    updateMap() {
        if (!skyMap.isMapInitialized() || !this.currentLocation) return;

        try {
            // Update map view
            skyMap.updateView(this.currentLocation.lat, this.currentLocation.lon, 12);
            
            // Clear existing markers
            skyMap.clearMarkers();
            
            // Add current location marker
            skyMap.addLocationMarker(
                this.currentLocation.lat, 
                this.currentLocation.lon, 
                'Current Location'
            );
            
            // Add AQI marker if data available
            if (this.currentData) {
                skyMap.addAQIMarker(
                    this.currentLocation.lat,
                    this.currentLocation.lon,
                    this.currentData.aqi,
                    `${this.currentData.primary_pollutant.toUpperCase()} - ${formatAQI(this.currentData.aqi).category}`
                );
            }
            
        } catch (error) {
            console.error('Failed to update map:', error);
        }
    }

    /**
     * Geocode an address using the backend service.
     */
    async geocodeAddress(address) {
        try {
            const url = `${this.apiBaseUrl}/location/search?q=${encodeURIComponent(address)}`;
            console.log('Geocoding address:', url);
            
            const data = await apiRequest(url);
            console.log('Geocoding response:', data);
            
            if (data.results && data.results.length > 0) {
                return data.results[0];
            }
            return null;
        } catch (error) {
            console.error('Failed to geocode address:', error);
            // Return null instead of throwing to allow graceful fallback
            return null;
        }
    }

    /**
     * Calculate AQI from pollutants.
     */
    async calculateAQI(pollutants) {
        try {
            const url = `${this.apiBaseUrl}/aqi/calculate`;
            const data = await apiRequest(url, {
                method: 'POST',
                body: JSON.stringify({ pollutants })
            });
            
            return data;
        } catch (error) {
            console.error('Failed to calculate AQI:', error);
            throw error;
        }
    }

    /**
     * Test API connection.
     */
    async testApiConnection() {
        try {
            console.log('Testing API connection...');
            const url = `${this.apiBaseUrl}/health`;
            
            // Test with simple fetch first
            const response = await fetch(url, {
                method: 'GET',
                mode: 'cors',
                credentials: 'omit'
            });
            
            console.log('Raw response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('API test successful:', data);
            showError('✅ API connection successful! Backend is running properly.');
            setTimeout(hideError, 3000);
            
        } catch (error) {
            console.error('API test failed:', error);
            let errorMsg = '❌ API connection failed. ';
            if (error.message.includes('Failed to fetch')) {
                errorMsg += 'Cannot connect to backend server. Please ensure it\'s running on port 5000.';
            } else if (error.message.includes('CORS')) {
                errorMsg += 'CORS error. Check browser console for details.';
            } else {
                errorMsg += error.message;
            }
            showError(errorMsg);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.skyForecasterApp = new SkyForecasterApp();
        console.log('Sky Forecaster application started successfully');
    } catch (error) {
        console.error('Failed to start Sky Forecaster application:', error);
        showError('Failed to initialize application. Please refresh the page.');
    }
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SkyForecasterApp;
}
