# Sky Forecaster - Setup Guide

## Quick Start

### 1. Backend Setup

1. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your credentials (optional for basic functionality)
   ```

3. **Start the backend server:**
   ```bash
   python app.py
   # Or from project root:
   python start_backend.py
   ```

The backend will start on `http://localhost:5000`

### 2. Frontend Setup

1. **Open the frontend:**
   ```bash
   # Simply open the index.html file in your browser
   open frontend/index.html
   # Or double-click on frontend/index.html
   ```

2. **The application will automatically connect to the backend**

## Features

### ✅ Completed Features

- **Real-time Air Quality Monitoring**
  - OpenAQ API integration
  - NASA EarthData integration (with credentials)
  - AQI calculation using EPA standards
  - Multiple pollutant support (PM2.5, PM10, NO₂, O₃, CO, SO₂)

- **Interactive Mapping**
  - Leaflet.js integration
  - Click to select locations
  - AQI color-coded markers
  - Multiple map layers (Street, Satellite, Terrain)

- **Location Services**
  - Address geocoding using OpenStreetMap Nominatim
  - Current location detection
  - Coordinate input support
  - Location search API

- **Forecasting**
  - Historical data analysis
  - Forecast generation based on trends
  - Configurable forecast periods (24h, 48h, 72h, 7 days)

- **Responsive Design**
  - Mobile-friendly interface
  - Desktop optimization
  - Clean, modern UI

- **Error Handling**
  - Comprehensive error messages
  - Graceful fallbacks to mock data
  - User-friendly feedback

## API Endpoints

### Core Endpoints
- `GET /api/health` - Health check
- `GET /api/current-conditions` - Current air quality data
- `GET /api/forecast` - Air quality forecast
- `GET /api/location/search` - Location search
- `POST /api/aqi/calculate` - AQI calculation

### Usage Examples

**Get current conditions:**
```bash
curl "http://localhost:5000/api/current-conditions?lat=40.7128&lon=-74.0060"
```

**Search for locations:**
```bash
curl "http://localhost:5000/api/location/search?q=New York"
```

**Calculate AQI:**
```bash
curl -X POST "http://localhost:5000/api/aqi/calculate" \
  -H "Content-Type: application/json" \
  -d '{"pollutants": {"pm25": 15.5, "pm10": 45.0, "no2": 25.0}}'
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
FLASK_CONFIG=development

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# NASA Earthdata Credentials (optional)
NASA_EARTHDATA_USERNAME=your-nasa-username
NASA_EARTHDATA_PASSWORD=your-nasa-password

# OpenAQ API Key (optional)
OPENAQ_API_KEY=your-openaq-api-key
```

### Data Sources

The application uses multiple data sources:

1. **OpenAQ** - Primary source for real-time air quality data
2. **NASA EarthData** - Satellite data (requires credentials)
3. **OpenStreetMap Nominatim** - Geocoding services
4. **Mock Data** - Fallback when real data is unavailable

## Troubleshooting

### Common Issues

1. **Backend won't start:**
   - Check Python version (3.7+ required)
   - Install dependencies: `pip install -r backend/requirements.txt`
   - Check port 5000 is available

2. **No air quality data:**
   - Check internet connection
   - Verify OpenAQ API is accessible
   - Application will fallback to mock data

3. **Location search not working:**
   - Check internet connection
   - Verify OpenStreetMap Nominatim is accessible
   - Try using coordinates instead

4. **Map not loading:**
   - Check internet connection
   - Verify Leaflet.js CDN is accessible
   - Check browser console for errors

### Development Mode

For development, the application runs with:
- Debug mode enabled
- CORS enabled for localhost
- Detailed error logging
- Mock data fallbacks

## Production Deployment

For production deployment:

1. Set `FLASK_DEBUG=False` in environment
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure proper CORS origins
4. Set up HTTPS
5. Configure logging
6. Set up monitoring

## NASA Space Apps Challenge

This application was built for the **2025 NASA Space Apps Challenge** "From EarthData to Action: Cloud Computing with Earth Observation Data for Predicting Cleaner, Safer Skies".

### Challenge Requirements Met:
- ✅ NASA EarthData integration
- ✅ Cloud computing approach
- ✅ Earth observation data utilization
- ✅ Air quality prediction
- ✅ Cleaner, safer skies focus
- ✅ Open-source implementation
- ✅ User-friendly interface

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check browser console for errors
4. Verify backend logs

## License

This project is open source and available under the MIT License.
