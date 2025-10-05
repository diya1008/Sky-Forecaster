# Sky Forecaster Backend

Flask-based backend for the Sky Forecaster air quality monitoring application.

## Features

- RESTful API endpoints for air quality data
- AQI calculation using EPA standards
- NASA EarthData integration
- OpenAQ API integration
- Mock data support for development
- Comprehensive error handling
- CORS support for frontend integration

## API Endpoints

### Health Check
- `GET /api/health` - Application health status

### Current Conditions
- `GET /api/current-conditions?lat={lat}&lon={lon}` - Get current air quality data
- `GET /api/current-conditions?location={location}` - Get current air quality data by location

### Forecast
- `GET /api/forecast?lat={lat}&lon={lon}&hours={hours}` - Get air quality forecast
- `GET /api/forecast?location={location}&hours={hours}` - Get forecast by location

### AQI Calculation
- `POST /api/aqi/calculate` - Calculate AQI from pollutant concentrations

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   ```bash
   cp env.example .env
   # Edit .env with your credentials
   ```

3. Run the application:
   ```bash
   python app.py
   # Or use the start script from project root:
   python start_backend.py
   ```

## Environment Variables

- `SECRET_KEY` - Flask secret key
- `FLASK_DEBUG` - Debug mode (True/False)
- `FLASK_CONFIG` - Configuration environment (development/production)
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)
- `NASA_EARTHDATA_USERNAME` - NASA EarthData username
- `NASA_EARTHDATA_PASSWORD` - NASA EarthData password
- `OPENAQ_API_KEY` - OpenAQ API key (optional)

## Development

The backend uses a mock-first approach. All endpoints return mock data by default for development and testing. Real data integration will be implemented in future phases.

## Project Structure

```
backend/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── models/             # Data models
│   └── air_quality.py  # Air quality data models
├── services/           # Business logic services
│   └── aqi_calculator.py # AQI calculation logic
├── utils/              # Utility functions
│   └── validators.py   # Input validation
└── requirements.txt    # Python dependencies
```
