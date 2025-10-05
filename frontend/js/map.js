/**
 * Map functionality for Sky Forecaster application using Leaflet.js.
 */

class SkyForecasterMap {
    constructor() {
        this.map = null;
        this.markers = [];
        this.layers = {};
        this.currentLocation = null;
        this.isInitialized = false;
    }

    /**
     * Initialize the map.
     * @param {number} lat - Default latitude
     * @param {number} lon - Default longitude
     * @param {number} zoom - Default zoom level
     */
    init(lat = 40.7128, lon = -74.0060, zoom = 10) {
        try {
            // Initialize the map
            this.map = L.map('map').setView([lat, lon], zoom);

            // Add OpenStreetMap tiles
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(this.map);

            // Add additional tile layers
            this.addTileLayers();

            // Add map controls
            this.addMapControls();

            // Add event listeners
            this.addEventListeners();

            this.isInitialized = true;
            console.log('Map initialized successfully');

        } catch (error) {
            console.error('Failed to initialize map:', error);
            throw error;
        }
    }

    /**
     * Add additional tile layers for different map styles.
     */
    addTileLayers() {
        // Satellite layer
        this.layers.satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: '© Esri',
            maxZoom: 19
        });

        // Terrain layer
        this.layers.terrain = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenTopoMap contributors',
            maxZoom: 17
        });

        // Default layer (already added)
        if (this.map._layers && Object.keys(this.map._layers).length > 0) {
            this.layers.default = this.map._layers[Object.keys(this.map._layers)[0]];
        }
    }

    /**
     * Add map controls and UI elements.
     */
    addMapControls() {
        // Add scale control
        L.control.scale({
            position: 'bottomleft',
            metric: true,
            imperial: false
        }).addTo(this.map);

        // Add layer control
        const baseLayers = {};
        if (this.layers.default) baseLayers['OpenStreetMap'] = this.layers.default;
        if (this.layers.satellite) baseLayers['Satellite'] = this.layers.satellite;
        if (this.layers.terrain) baseLayers['Terrain'] = this.layers.terrain;
        
        const layerControl = L.control.layers(baseLayers, {}, {
            position: 'topright',
            collapsed: false
        }).addTo(this.map);

        // Add custom controls
        this.addCustomControls();
    }

    /**
     * Add custom map controls.
     */
    addCustomControls() {
        // Center map button
        const centerButton = L.control({ position: 'topleft' });
        centerButton.onAdd = function(map) {
            const div = L.DomUtil.create('div', 'leaflet-control-custom');
            div.innerHTML = '<button id="centerMapBtn" title="Center on Location">📍</button>';
            div.style.backgroundColor = 'white';
            div.style.padding = '5px';
            div.style.borderRadius = '5px';
            div.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
            return div;
        };
        centerButton.addTo(this.map);

        // Toggle layers button
        const toggleButton = L.control({ position: 'topleft' });
        toggleButton.onAdd = function(map) {
            const div = L.DomUtil.create('div', 'leaflet-control-custom');
            div.innerHTML = '<button id="toggleLayersBtn" title="Toggle Layers">🗺️</button>';
            div.style.backgroundColor = 'white';
            div.style.padding = '5px';
            div.style.borderRadius = '5px';
            div.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
            div.style.marginTop = '5px';
            return div;
        };
        toggleButton.addTo(this.map);
    }

    /**
     * Add event listeners for map interactions.
     */
    addEventListeners() {
        // Map click event
        this.map.on('click', (e) => {
            this.handleMapClick(e);
        });

        // Map move event
        this.map.on('moveend', () => {
            this.handleMapMove();
        });

        // Custom control events
        this.addControlEventListeners();
    }

    /**
     * Add event listeners for custom controls.
     */
    addControlEventListeners() {
        // Center map button
        const centerBtn = document.getElementById('centerMapBtn');
        if (centerBtn) {
            centerBtn.addEventListener('click', () => {
                this.centerOnCurrentLocation();
            });
        }

        // Toggle layers button
        const toggleBtn = document.getElementById('toggleLayersBtn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.toggleLayers();
            });
        }
    }

    /**
     * Handle map click events.
     * @param {Object} e - Leaflet click event
     */
    handleMapClick(e) {
        const lat = e.latlng.lat;
        const lon = e.latlng.lng;
        
        console.log(`Map clicked at: ${lat}, ${lon}`);
        
        // Update current location
        this.currentLocation = { lat, lon };
        
        // Trigger location update event
        this.triggerLocationUpdate(lat, lon);
    }

    /**
     * Handle map move events.
     */
    handleMapMove() {
        const center = this.map.getCenter();
        console.log(`Map moved to: ${center.lat}, ${center.lng}`);
    }

    /**
     * Center the map on current location.
     */
    centerOnCurrentLocation() {
        if (this.currentLocation) {
            this.map.setView([this.currentLocation.lat, this.currentLocation.lon], 12);
        } else {
            // Try to get user's current location
            getCurrentLocation()
                .then(coords => {
                    this.currentLocation = coords;
                    this.map.setView([coords.lat, coords.lon], 12);
                    this.addLocationMarker(coords.lat, coords.lon, 'Current Location');
                })
                .catch(error => {
                    console.error('Failed to get current location:', error);
                    showError('Unable to get your current location');
                });
        }
    }

    /**
     * Toggle between different map layers.
     */
    toggleLayers() {
        // Simple layer toggle - cycle through available layers
        const layerNames = Object.keys(this.layers);
        const currentLayer = this.getCurrentLayer();
        const currentIndex = layerNames.indexOf(currentLayer);
        const nextIndex = (currentIndex + 1) % layerNames.length;
        const nextLayer = layerNames[nextIndex];

        this.switchToLayer(nextLayer);
    }

    /**
     * Get the currently active layer.
     * @returns {string} Current layer name
     */
    getCurrentLayer() {
        // This is a simplified approach - in a real implementation,
        // you'd track the active layer more precisely
        return 'default';
    }

    /**
     * Switch to a specific layer.
     * @param {string} layerName - Name of the layer to switch to
     */
    switchToLayer(layerName) {
        if (this.layers[layerName]) {
            // Remove current layer
            this.map.eachLayer((layer) => {
                if (layer instanceof L.TileLayer) {
                    this.map.removeLayer(layer);
                }
            });

            // Add new layer
            this.layers[layerName].addTo(this.map);
            console.log(`Switched to ${layerName} layer`);
        }
    }

    /**
     * Add a marker to the map.
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @param {string} title - Marker title
     * @param {string} color - Marker color
     * @returns {Object} Leaflet marker
     */
    addMarker(lat, lon, title = '', color = 'red') {
        const marker = L.marker([lat, lon], {
            title: title
        }).addTo(this.map);

        if (title) {
            marker.bindPopup(title);
        }

        this.markers.push(marker);
        return marker;
    }

    /**
     * Add a location marker with custom icon.
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @param {string} title - Marker title
     * @returns {Object} Leaflet marker
     */
    addLocationMarker(lat, lon, title = 'Location') {
        const icon = L.divIcon({
            className: 'location-marker',
            html: '📍',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });

        const marker = L.marker([lat, lon], { icon: icon }).addTo(this.map);
        marker.bindPopup(title);
        
        this.markers.push(marker);
        return marker;
    }

    /**
     * Add an AQI marker with color coding.
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @param {number} aqi - AQI value
     * @param {string} title - Marker title
     * @returns {Object} Leaflet marker
     */
    addAQIMarker(lat, lon, aqi, title = '') {
        const aqiData = formatAQI(aqi);
        const color = aqiData.color;
        
        const icon = L.divIcon({
            className: 'aqi-marker',
            html: `<div style="background-color: ${color}; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">${aqi}</div>`,
            iconSize: [40, 40],
            iconAnchor: [20, 20]
        });

        const marker = L.marker([lat, lon], { icon: icon }).addTo(this.map);
        
        const popupContent = `
            <div style="text-align: center;">
                <h4>AQI: ${aqi}</h4>
                <p><strong>${aqiData.category}</strong></p>
                <p style="font-size: 12px; color: #666;">${aqiData.description}</p>
                ${title ? `<p style="font-size: 12px; color: #666;">${title}</p>` : ''}
            </div>
        `;
        
        marker.bindPopup(popupContent);
        this.markers.push(marker);
        return marker;
    }

    /**
     * Clear all markers from the map.
     */
    clearMarkers() {
        this.markers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.markers = [];
    }

    /**
     * Update map view to show a location.
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @param {number} zoom - Zoom level
     */
    updateView(lat, lon, zoom = 12) {
        if (this.map && this.isInitialized) {
            this.map.setView([lat, lon], zoom);
            this.currentLocation = { lat, lon };
        }
    }

    /**
     * Fit map bounds to show all markers.
     */
    fitBounds() {
        if (this.markers.length > 0) {
            const group = new L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    }

    /**
     * Trigger location update event.
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     */
    triggerLocationUpdate(lat, lon) {
        // Dispatch custom event for location updates
        const event = new CustomEvent('locationUpdate', {
            detail: { lat, lon }
        });
        document.dispatchEvent(event);
    }

    /**
     * Get current map center coordinates.
     * @returns {Object} Current center coordinates
     */
    getCurrentCenter() {
        if (this.map) {
            const center = this.map.getCenter();
            return {
                lat: center.lat,
                lon: center.lng
            };
        }
        return null;
    }

    /**
     * Check if map is initialized.
     * @returns {boolean} True if map is initialized
     */
    isMapInitialized() {
        return this.isInitialized && this.map !== null;
    }

    /**
     * Destroy the map instance.
     */
    destroy() {
        if (this.map) {
            this.map.remove();
            this.map = null;
            this.markers = [];
            this.isInitialized = false;
        }
    }
}

// Create global map instance
const skyMap = new SkyForecasterMap();
