"""
Sky Forecaster Flask Application

A data-driven web application for air quality forecasting and monitoring.
Built for NASA Space Apps Challenge 2025 "From EarthData to Action" challenge.
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import logging

from config import config
from models.air_quality import AirQualityData, ForecastData
from services.aqi_calculator import AQICalculator
from services.data_fetcher import DataFetcher
from services.geocoding import GeocodingService
from utils.validators import validate_coordinates, validate_location_input


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])
    
    # Initialize CORS with more permissive settings
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'Accept'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize services
    data_fetcher = DataFetcher()
    geocoding_service = GeocodingService()
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })
    
    @app.route('/api/current-conditions', methods=['GET'])
    def get_current_conditions():
        """
        Get current air quality conditions for a location.
        
        Query Parameters:
            lat (float): Latitude
            lon (float): Longitude
            location (str): Location string (alternative to lat/lon)
        """
        try:
            # Get location parameters
            lat = request.args.get('lat', type=float)
            lon = request.args.get('lon', type=float)
            location = request.args.get('location', type=str)
            
            # Validate location input
            if lat is not None and lon is not None:
                if not validate_coordinates(lat, lon):
                    return jsonify({'error': 'Invalid coordinates'}), 400
            elif location:
                # Try geocoding the location
                location_info = geocoding_service.get_location_info(location)
                if location_info:
                    lat = location_info['latitude']
                    lon = location_info['longitude']
                else:
                    # Fallback to validation
                    is_valid, error_msg, parsed_lat, parsed_lon = validate_location_input(location)
                    if not is_valid:
                        return jsonify({'error': error_msg}), 400
                    lat, lon = parsed_lat, parsed_lon
            else:
                return jsonify({'error': 'Location or coordinates required'}), 400
            
            # Try to fetch real data first
            try:
                real_data = data_fetcher.get_combined_data(lat, lon)
                
                if real_data and real_data.get('measurements'):
                    # Process real data
                    processed_data = process_real_air_quality_data(real_data)
                    return jsonify(processed_data.to_dict())
                else:
                    logger.warning("No real data available, using mock data")
                    # Fallback to mock data
                    mock_data = create_mock_air_quality_data(lat, lon)
                    return jsonify(mock_data.to_dict())
                    
            except Exception as e:
                logger.error(f"Error fetching real data: {e}")
                # Fallback to mock data
                mock_data = create_mock_air_quality_data(lat, lon)
                return jsonify(mock_data.to_dict())
            
        except Exception as e:
            logger.error(f"Error in get_current_conditions: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/forecast', methods=['GET'])
    def get_forecast():
        """
        Get air quality forecast for a location.
        
        Query Parameters:
            lat (float): Latitude
            lon (float): Longitude
            location (str): Location string (alternative to lat/lon)
            hours (int): Forecast hours (default: 24)
        """
        try:
            # Get location parameters
            lat = request.args.get('lat', type=float)
            lon = request.args.get('lon', type=float)
            location = request.args.get('location', type=str)
            hours = request.args.get('hours', 24, type=int)
            
            # Validate location input
            if lat is not None and lon is not None:
                if not validate_coordinates(lat, lon):
                    return jsonify({'error': 'Invalid coordinates'}), 400
            elif location:
                # Try geocoding the location
                location_info = geocoding_service.get_location_info(location)
                if location_info:
                    lat = location_info['latitude']
                    lon = location_info['longitude']
                else:
                    # Fallback to validation
                    is_valid, error_msg, parsed_lat, parsed_lon = validate_location_input(location)
                    if not is_valid:
                        return jsonify({'error': error_msg}), 400
                    lat, lon = parsed_lat, parsed_lon
            else:
                return jsonify({'error': 'Location or coordinates required'}), 400
            
            # Validate hours parameter
            if not isinstance(hours, int) or hours < 1 or hours > 168:  # Max 7 days
                return jsonify({'error': 'Invalid hours parameter (1-168)'}), 400
            
            # Try to fetch real forecast data first
            try:
                # For now, use historical data to simulate forecast
                # In a real implementation, this would use weather models
                historical_data = data_fetcher.fetch_historical_data(lat, lon, days=7)
                
                if historical_data and len(historical_data) > 0:
                    # Process historical data into forecast
                    processed_forecast = process_historical_to_forecast(historical_data, lat, lon, hours)
                    return jsonify(processed_forecast.to_dict())
                else:
                    logger.warning("No historical data available, using mock forecast")
                    # Fallback to mock forecast
                    mock_forecast = create_mock_forecast_data(lat, lon, hours)
                    return jsonify(mock_forecast.to_dict())
                    
            except Exception as e:
                logger.error(f"Error fetching forecast data: {e}")
                # Fallback to mock forecast
                mock_forecast = create_mock_forecast_data(lat, lon, hours)
                return jsonify(mock_forecast.to_dict())
            
        except Exception as e:
            logger.error(f"Error in get_forecast: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/location/search', methods=['GET'])
    def search_location():
        """
        Search for locations using a query string.
        
        Query Parameters:
            q (str): Search query
            lat (float): Latitude for nearby search
            lon (float): Longitude for nearby search
        """
        try:
            query = request.args.get('q', type=str)
            lat = request.args.get('lat', type=float)
            lon = request.args.get('lon', type=float)
            
            if not query:
                return jsonify({'error': 'Query parameter required'}), 400
            
            if lat is not None and lon is not None:
                # Search nearby places
                results = geocoding_service.search_nearby_places(lat, lon, query)
            else:
                # General geocoding search
                location_info = geocoding_service.geocode_address(query)
                results = [location_info] if location_info else []
            
            return jsonify({
                'query': query,
                'results': results,
                'count': len(results)
            })
            
        except Exception as e:
            logger.error(f"Error in search_location: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/aqi/calculate', methods=['POST'])
    def calculate_aqi():
        """
        Calculate AQI from pollutant concentrations.
        
        Request Body:
            {
                "pollutants": {
                    "pm25": 15.5,
                    "pm10": 45.0,
                    "no2": 25.0
                }
            }
        """
        try:
            data = request.get_json()
            
            if not data or 'pollutants' not in data:
                return jsonify({'error': 'Pollutants data required'}), 400
            
            pollutants = data['pollutants']
            
            if not isinstance(pollutants, dict):
                return jsonify({'error': 'Pollutants must be a dictionary'}), 400
            
            # Calculate overall AQI
            aqi, primary_pollutant = AQICalculator.calculate_overall_aqi(pollutants)
            category = AQICalculator.get_aqi_category(aqi)
            color = AQICalculator.get_aqi_color(aqi)
            
            return jsonify({
                'aqi': aqi,
                'primary_pollutant': primary_pollutant,
                'category': category,
                'color': color,
                'pollutants': pollutants
            })
            
        except Exception as e:
            logger.error(f"Error in calculate_aqi: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


def create_mock_air_quality_data(lat: float, lon: float) -> AirQualityData:
    """Create mock air quality data for testing."""
    # Mock pollutant concentrations
    pollutants = {
        'pm25': 15.5,
        'pm10': 45.0,
        'no2': 25.0,
        'o3': 60.0
    }
    
    # Calculate AQI
    aqi, primary_pollutant = AQICalculator.calculate_overall_aqi(pollutants)
    
    return AirQualityData(
        latitude=lat,
        longitude=lon,
        aqi=aqi,
        primary_pollutant=primary_pollutant,
        timestamp=datetime.utcnow(),
        pm25=pollutants['pm25'],
        pm10=pollutants['pm10'],
        no2=pollutants['no2'],
        o3=pollutants['o3'],
        temperature=22.5,
        humidity=65.0,
        pressure=1013.25,
        wind_speed=5.2,
        wind_direction=180.0
    )


def process_real_air_quality_data(data: dict) -> AirQualityData:
    """Process real air quality data into AirQualityData model."""
    measurements = data.get('measurements', {})
    weather = data.get('weather', {})
    
    # Calculate AQI from measurements
    aqi, primary_pollutant = AQICalculator.calculate_overall_aqi(measurements)
    
    # Parse timestamp
    timestamp_str = data.get('timestamp', datetime.utcnow().isoformat())
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        timestamp = datetime.utcnow()
    
    return AirQualityData(
        latitude=data.get('latitude', 0),
        longitude=data.get('longitude', 0),
        aqi=aqi,
        primary_pollutant=primary_pollutant,
        timestamp=timestamp,
        pm25=measurements.get('pm25'),
        pm10=measurements.get('pm10'),
        no2=measurements.get('no2'),
        o3=measurements.get('o3'),
        co=measurements.get('co'),
        so2=measurements.get('so2'),
        temperature=weather.get('temperature'),
        humidity=weather.get('humidity'),
        pressure=weather.get('pressure'),
        wind_speed=weather.get('wind_speed'),
        wind_direction=weather.get('wind_direction')
    )


def process_historical_to_forecast(historical_data: list, lat: float, lon: float, hours: int) -> ForecastData:
    """Process historical data into forecast predictions."""
    predictions = []
    
    # Use historical data to create forecast predictions
    for i in range(0, hours, 6):  # Every 6 hours
        # Get base measurements from most recent historical data
        if historical_data:
            base_measurements = historical_data[-1].get('measurements', {})
        else:
            base_measurements = {'pm25': 15.0, 'pm10': 45.0, 'no2': 25.0, 'o3': 60.0}
        
        # Add some variation for forecast
        forecast_measurements = {}
        for param, value in base_measurements.items():
            if value is not None:
                # Add random variation (±20%)
                import random
                variation = random.uniform(0.8, 1.2)
                forecast_measurements[param] = value * variation
        
        aqi, primary_pollutant = AQICalculator.calculate_overall_aqi(forecast_measurements)
        
        # Create future timestamp
        future_timestamp = datetime.utcnow() + timedelta(hours=i)
        
        prediction = AirQualityData(
            latitude=lat,
            longitude=lon,
            aqi=aqi,
            primary_pollutant=primary_pollutant,
            timestamp=future_timestamp,
            pm25=forecast_measurements.get('pm25'),
            pm10=forecast_measurements.get('pm10'),
            no2=forecast_measurements.get('no2'),
            o3=forecast_measurements.get('o3'),
            co=forecast_measurements.get('co'),
            so2=forecast_measurements.get('so2'),
            temperature=22.5 + (i * 0.1),
            humidity=65.0 - (i * 0.2),
            pressure=1013.25 + (i * 0.1),
            wind_speed=5.2 + (i * 0.05),
            wind_direction=180.0 + (i * 2.0)
        )
        
        predictions.append(prediction)
    
    return ForecastData(
        latitude=lat,
        longitude=lon,
        forecast_hours=hours,
        timestamp=datetime.utcnow(),
        predictions=predictions
    )


def create_mock_forecast_data(lat: float, lon: float, hours: int) -> ForecastData:
    """Create mock forecast data for testing."""
    predictions = []
    
    for i in range(0, hours, 6):  # Every 6 hours
        # Mock pollutant concentrations with some variation
        pollutants = {
            'pm25': 15.5 + (i * 0.5),
            'pm10': 45.0 + (i * 1.0),
            'no2': 25.0 + (i * 0.3),
            'o3': 60.0 + (i * 0.8)
        }
        
        aqi, primary_pollutant = AQICalculator.calculate_overall_aqi(pollutants)
        
        prediction = AirQualityData(
            latitude=lat,
            longitude=lon,
            aqi=aqi,
            primary_pollutant=primary_pollutant,
            timestamp=datetime.utcnow(),
            pm25=pollutants['pm25'],
            pm10=pollutants['pm10'],
            no2=pollutants['no2'],
            o3=pollutants['o3'],
            temperature=22.5 + (i * 0.1),
            humidity=65.0 - (i * 0.2),
            pressure=1013.25 + (i * 0.1),
            wind_speed=5.2 + (i * 0.05),
            wind_direction=180.0 + (i * 2.0)
        )
        
        predictions.append(prediction)
    
    return ForecastData(
        latitude=lat,
        longitude=lon,
        forecast_hours=hours,
        timestamp=datetime.utcnow(),
        predictions=predictions
    )


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
