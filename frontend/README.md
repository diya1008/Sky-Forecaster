# Sky Forecaster Frontend

Vanilla JavaScript frontend for the Sky Forecaster air quality monitoring application.

## Features

- Responsive design for mobile and desktop
- Interactive mapping with Leaflet.js
- Real-time air quality data visualization
- AQI color-coded displays
- Location search and geolocation
- Forecast visualization
- Clean, modern UI

## Technology Stack

- **HTML5** - Semantic markup
- **CSS3** - Modern styling with CSS custom properties
- **Vanilla JavaScript (ES6+)** - No frameworks, pure JavaScript
- **Leaflet.js** - Interactive mapping
- **Fetch API** - HTTP requests

## Project Structure

```
frontend/
├── index.html          # Main HTML file
├── css/
│   └── style.css       # Stylesheet with CSS custom properties
├── js/
│   ├── app.js          # Main application logic
│   ├── map.js          # Leaflet.js mapping functionality
│   └── utils.js        # Utility functions
└── assets/             # Static assets (favicon, images)
```

## Setup

1. Open `index.html` in a web browser
2. Ensure the backend is running on `http://localhost:5000`
3. The application will automatically connect to the backend API

## Usage

### Location Input
- Enter coordinates in "latitude, longitude" format
- Enter city name or address (geocoding not implemented yet)
- Use the location button to get your current position

### Navigation
- **Current** - View current air quality conditions
- **Forecast** - View air quality forecast
- **About** - Learn about the application

### Interactive Map
- Click on the map to select a location
- AQI values are color-coded on the map
- Use map controls to change layers and center view

## API Integration

The frontend communicates with the backend through RESTful API endpoints:

- `GET /api/current-conditions` - Current air quality data
- `GET /api/forecast` - Forecast data
- `POST /api/aqi/calculate` - AQI calculation

## Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

## Browser Support

- Modern browsers with ES6+ support
- Fetch API support required
- Geolocation API support (optional)

## Development

The frontend uses a modular approach with separate files for:
- **app.js** - Main application logic and event handling
- **map.js** - Map functionality and geospatial features
- **utils.js** - Utility functions and helpers

All code follows modern JavaScript practices with proper error handling and user feedback.
