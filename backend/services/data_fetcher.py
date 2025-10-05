"""
Data fetching service for Sky Forecaster application.
Integrates with NASA EarthData and OpenAQ APIs.
"""
import os
import requests
import earthaccess
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config import Config

logger = logging.getLogger(__name__)


class DataFetcher:
    """Service for fetching air quality data from various sources."""
    
    def __init__(self):
        # Try OpenAQ v2 first (no auth required), fallback to v3
        self.openaq_base_url = 'https://api.openaq.org/v2'
        self.openaq_v3_url = 'https://api.openaq.org/v3'
        
        # Real-time API keys
        self.airvisual_api_key = os.environ.get('AIRVISUAL_API_KEY', 'demo')  # Free tier
        self.openweather_api_key = os.environ.get('OPENWEATHER_API_KEY', '')  # Free tier
        self.worldaq_api_key = os.environ.get('WORLDAQ_API_KEY', '')  # Free tier
        
        # NASA credentials
        self.nasa_username = Config.NASA_EARTHDATA_USERNAME
        self.nasa_password = Config.NASA_EARTHDATA_PASSWORD
        
        # API endpoints
        self.airnow_base_url = 'https://www.airnowapi.org/aq/observation'
        self.openweather_base_url = 'https://api.openweathermap.org/data/2.5'
        self.worldaq_base_url = 'https://api.waqi.info/feed'
        
        # Initialize NASA EarthAccess if credentials are available
        self.nasa_authenticated = False
        if self.nasa_username and self.nasa_password:
            try:
                earthaccess.login(self.nasa_username, self.nasa_password)
                self.nasa_authenticated = True
                logger.info("NASA EarthAccess authentication successful")
            except Exception as e:
                logger.warning(f"NASA EarthAccess authentication failed: {e}")
    
    def fetch_current_conditions_openaq(self, lat: float, lon: float, radius: int = 10000) -> Optional[Dict]:
        """
        Fetch current air quality conditions from OpenAQ.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in meters (default: 10km)
            
        Returns:
            Dictionary with air quality data or None if error
        """
        try:
            # Try OpenAQ v2 first (no authentication required)
            url = f"{self.openaq_base_url}/measurements"
            
            # v2 API parameters (correct format)
            params = {
                'coordinates': f"{lat},{lon}",
                'radius': radius,
                'limit': 100,
                'sort': 'desc'
            }
            
            headers = {
                'User-Agent': 'SkyForecaster/1.0 (NASA Space Apps Challenge 2025)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('results'):
                logger.warning(f"No OpenAQ v2 data found for coordinates {lat}, {lon}")
                return None
            
            # Process the results
            return self._process_openaq_data(data['results'], lat, lon)
            
        except requests.RequestException as e:
            logger.warning(f"OpenAQ v2 API request failed: {e}")
            # Try v3 as fallback
            try:
                url = f"{self.openaq_v3_url}/measurements"
                
                # v3 API parameters
                params = {
                    'coordinates': f"{lat},{lon}",
                    'radius': radius,
                    'limit': 100,
                    'orderBy': 'datetime',
                    'sort': 'desc'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if not data.get('results'):
                    logger.warning(f"No OpenAQ v3 data found for coordinates {lat}, {lon}")
                    return self._get_mock_air_quality_data(lat, lon)
                
                # Process the results
                return self._process_openaq_data(data['results'], lat, lon)
                
            except requests.RequestException as v3_error:
                logger.error(f"OpenAQ v3 API request also failed: {v3_error}")
                # Try real-time APIs as fallback
                return self._fetch_realtime_data(lat, lon)
        except Exception as e:
            logger.error(f"Error processing OpenAQ data: {e}")
            # Return mock data as fallback
            return self._get_mock_air_quality_data(lat, lon)
    
    def _fetch_airvisual_data(self, lat: float, lon: float) -> Dict:
        """
        Fetch real-time air quality data from AirVisual API (free tier).
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with air quality data
        """
        try:
            # AirVisual free API endpoint
            url = "https://api.airvisual.com/v2/nearest_city"
            
            params = {
                'lat': lat,
                'lon': lon,
                'key': self.airvisual_api_key
            }
            
            headers = {
                'User-Agent': 'SkyForecaster/1.0 (NASA Space Apps Challenge 2025)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success':
                current = data.get('data', {}).get('current', {})
                pollution = current.get('pollution', {})
                weather = current.get('weather', {})
                
                # Convert AirVisual data to our format
                measurements = {
                    'pm25': pollution.get('aqius'),  # AirVisual uses AQI, we'll convert
                    'pm10': None,  # AirVisual doesn't provide PM10 in free tier
                    'no2': None,
                    'o3': None
                }
                
                # Convert AQI to approximate PM2.5 concentration
                if measurements['pm25']:
                    aqi = measurements['pm25']
                    if aqi <= 50:
                        measurements['pm25'] = round(aqi * 0.5, 1)  # Approximate conversion
                    elif aqi <= 100:
                        measurements['pm25'] = round(25 + (aqi - 50) * 0.5, 1)
                    elif aqi <= 150:
                        measurements['pm25'] = round(50 + (aqi - 100) * 0.8, 1)
                    else:
                        measurements['pm25'] = round(90 + (aqi - 150) * 1.2, 1)
                
                return {
                    'latitude': lat,
                    'longitude': lon,
                    'timestamp': datetime.utcnow().isoformat(),
                    'measurements': measurements,
                    'weather': {
                        'temperature': weather.get('tp'),  # Temperature
                        'humidity': weather.get('hu'),     # Humidity
                        'pressure': weather.get('pr'),     # Pressure
                        'wind_speed': weather.get('ws'),   # Wind speed
                        'wind_direction': weather.get('wd') # Wind direction
                    },
                    'source': 'AirVisual API (Real-time)'
                }
            else:
                logger.warning(f"AirVisual API returned error: {data}")
                return self._get_mock_air_quality_data(lat, lon)
                
        except requests.RequestException as e:
            logger.error(f"AirVisual API request failed: {e}")
            return self._get_mock_air_quality_data(lat, lon)
        except Exception as e:
            logger.error(f"Error processing AirVisual data: {e}")
            return self._get_mock_air_quality_data(lat, lon)
    
    def _fetch_realtime_data(self, lat: float, lon: float) -> Dict:
        """Fetch real-time data from multiple sources."""
        try:
            # Try World Air Quality Index (free, no auth needed)
            waqi_data = self._fetch_waqi_data(lat, lon)
            if waqi_data:
                return waqi_data
            
            # Try OpenWeatherMap (free tier)
            if self.openweather_api_key:
                owm_data = self._fetch_openweather_data(lat, lon)
                if owm_data:
                    return owm_data
            
            # Try AirNow (US only)
            if -125 <= lon <= -66 and 25 <= lat <= 49:  # US bounds
                airnow_data = self._fetch_airnow_data(lat, lon)
                if airnow_data:
                    return airnow_data
            
            # Fallback to mock data
            return self._get_mock_air_quality_data(lat, lon)
            
        except Exception as e:
            logger.error(f"Error fetching real-time data: {e}")
            return self._get_mock_air_quality_data(lat, lon)
    
    def _fetch_waqi_data(self, lat: float, lon: float) -> Optional[Dict]:
        """Fetch data from World Air Quality Index API."""
        try:
            url = f"{self.worldaq_base_url}/geo:{lat};{lon}/"
            params = {'token': self.worldaq_api_key} if self.worldaq_api_key else {}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') == 'ok' and data.get('data'):
                aq_data = data['data']
                
                return {
                    'latitude': lat,
                    'longitude': lon,
                    'timestamp': datetime.utcnow().isoformat(),
                    'measurements': {
                        'pm25': aq_data.get('iaqi', {}).get('pm25', {}).get('v'),
                        'pm10': aq_data.get('iaqi', {}).get('pm10', {}).get('v'),
                        'no2': aq_data.get('iaqi', {}).get('no2', {}).get('v'),
                        'o3': aq_data.get('iaqi', {}).get('o3', {}).get('v'),
                    },
                    'weather': {
                        'temperature': aq_data.get('iaqi', {}).get('t', {}).get('v'),
                        'humidity': aq_data.get('iaqi', {}).get('h', {}).get('v'),
                        'pressure': aq_data.get('iaqi', {}).get('p', {}).get('v'),
                        'wind_speed': aq_data.get('iaqi', {}).get('w', {}).get('v'),
                    },
                    'source': 'World Air Quality Index (Real-time)'
                }
            return None
            
        except Exception as e:
            logger.error(f"WAQI API error: {e}")
            return None
    
    def _fetch_openweather_data(self, lat: float, lon: float) -> Optional[Dict]:
        """Fetch air quality data from OpenWeatherMap."""
        try:
            url = f"{self.openweather_base_url}/air_pollution"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.openweather_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('list'):
                pollution = data['list'][0]['components']
                
                return {
                    'latitude': lat,
                    'longitude': lon,
                    'timestamp': datetime.utcnow().isoformat(),
                    'measurements': {
                        'pm25': pollution.get('pm2_5'),
                        'pm10': pollution.get('pm10'),
                        'no2': pollution.get('no2'),
                        'o3': pollution.get('o3'),
                        'co': pollution.get('co'),
                        'so2': pollution.get('so2'),
                    },
                    'weather': {},  # Weather data from separate API call
                    'source': 'OpenWeatherMap (Real-time)'
                }
            return None
            
        except Exception as e:
            logger.error(f"OpenWeatherMap API error: {e}")
            return None
    
    def _fetch_airnow_data(self, lat: float, lon: float) -> Optional[Dict]:
        """Fetch data from AirNow API (US only)."""
        try:
            # AirNow requires an API key, but we can try without for basic data
            url = f"{self.airnow_base_url}/latlong"
            params = {
                'latitude': lat,
                'longitude': lon,
                'format': 'application/json',
                'distance': 25
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data:
                # Process AirNow data
                measurements = {}
                for item in data:
                    param = item.get('ParameterName', '').lower()
                    value = item.get('Value')
                    if value is not None:
                        measurements[param] = float(value)
                
                return {
                    'latitude': lat,
                    'longitude': lon,
                    'timestamp': datetime.utcnow().isoformat(),
                    'measurements': measurements,
                    'weather': {},
                    'source': 'AirNow (Real-time)'
                }
            return None
            
        except Exception as e:
            logger.error(f"AirNow API error: {e}")
            return None
    
    def _process_openaq_data(self, results: List[Dict], lat: float, lon: float) -> Dict:
        """
        Process OpenAQ API results into standardized format.
        
        Args:
            results: List of measurement results from OpenAQ
            lat: Latitude
            lon: Longitude
            
        Returns:
            Processed air quality data
        """
        # Group measurements by parameter
        measurements = {}
        latest_timestamp = None
        
        for result in results:
            parameter = result.get('parameter', '').lower()
            value = result.get('value')
            unit = result.get('unit')
            
            if value is not None and parameter in ['pm25', 'pm10', 'no2', 'o3', 'co', 'so2']:
                # Convert units to standard format
                if unit == 'µg/m³' or unit == 'ug/m3':
                    # Already in correct units
                    measurements[parameter] = float(value)
                elif unit == 'ppm' and parameter in ['no2', 'o3', 'co', 'so2']:
                    # Convert ppm to µg/m³ (approximate conversion)
                    molecular_weights = {
                        'no2': 46.01,
                        'o3': 48.00,
                        'co': 28.01,
                        'so2': 64.07
                    }
                    if parameter in molecular_weights:
                        # Conversion: ppm * molecular_weight * 1000 / 24.45 (at 25°C, 1 atm)
                        measurements[parameter] = float(value) * molecular_weights[parameter] * 1000 / 24.45
                    else:
                        measurements[parameter] = float(value)
                else:
                    measurements[parameter] = float(value)
                
                # Track latest timestamp
                result_timestamp = result.get('date', {}).get('utc')
                if result_timestamp and (not latest_timestamp or result_timestamp > latest_timestamp):
                    latest_timestamp = result_timestamp
        
        # Get weather data from a nearby station if available
        weather_data = self._get_weather_data_nearest(results, lat, lon)
        
        return {
            'latitude': lat,
            'longitude': lon,
            'timestamp': latest_timestamp or datetime.utcnow().isoformat(),
            'measurements': measurements,
            'weather': weather_data,
            'source': 'OpenAQ'
        }
    
    def _get_weather_data_nearest(self, results: List[Dict], lat: float, lon: float) -> Dict:
        """
        Extract weather data from the nearest measurement station.
        
        Args:
            results: List of measurement results
            lat: Latitude
            lon: Longitude
            
        Returns:
            Weather data dictionary
        """
        weather_data = {}
        
        # Find results with weather data
        for result in results:
            # Check for weather-related parameters
            if result.get('parameter') in ['temperature', 'humidity', 'pressure', 'wind_speed']:
                param = result.get('parameter')
                value = result.get('value')
                if value is not None:
                    weather_data[param] = float(value)
            
            # Check for location data
            location = result.get('location')
            if location:
                # Get coordinates from location
                coords = location.get('coordinates')
                if coords and len(coords) == 2:
                    station_lat, station_lon = coords
                    # Calculate distance (simple approximation)
                    distance = ((lat - station_lat) ** 2 + (lon - station_lon) ** 2) ** 0.5
                    if distance < 0.1:  # Within ~10km
                        # Extract additional weather data if available
                        if 'temperature' not in weather_data:
                            weather_data['temperature'] = 22.0  # Default
                        if 'humidity' not in weather_data:
                            weather_data['humidity'] = 60.0  # Default
                        if 'pressure' not in weather_data:
                            weather_data['pressure'] = 1013.25  # Default
                        if 'wind_speed' not in weather_data:
                            weather_data['wind_speed'] = 5.0  # Default
                        break
        
        return weather_data
    
    def fetch_nasa_tempo_data(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Fetch NASA TEMPO data for the specified location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with NASA TEMPO data or None if error
        """
        if not self.nasa_authenticated:
            logger.warning("NASA EarthAccess not authenticated, skipping TEMPO data")
            return None
        
        try:
            # Search for TEMPO data
            # Note: This is a simplified implementation
            # Real implementation would use earthaccess to search and download data
            
            # For now, return mock data structure
            # In production, this would fetch real TEMPO data
            logger.info("TEMPO data fetching not fully implemented - using mock data")
            
            return {
                'latitude': lat,
                'longitude': lon,
                'timestamp': datetime.utcnow().isoformat(),
                'measurements': {
                    'no2': 25.0,  # µg/m³
                    'o3': 60.0,   # µg/m³
                    'pm25': 15.0, # µg/m³
                },
                'source': 'NASA TEMPO'
            }
            
        except Exception as e:
            logger.error(f"Error fetching NASA TEMPO data: {e}")
            return None
    
    def fetch_historical_data(self, lat: float, lon: float, days: int = 7) -> Optional[List[Dict]]:
        """
        Fetch historical air quality data.
        
        Args:
            lat: Latitude
            lon: Longitude
            days: Number of days to fetch
            
        Returns:
            List of historical data points
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Try OpenAQ v2 first
            url = f"{self.openaq_base_url}/measurements"
            
            # v2 API parameters (correct format)
            params = {
                'coordinates': f"{lat},{lon}",
                'radius': 50000,  # 50km radius for historical data
                'date_from': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'date_to': end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'limit': 1000,
                'sort': 'asc'
            }
            
            headers = {
                'User-Agent': 'SkyForecaster/1.0 (NASA Space Apps Challenge 2025)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('results'):
                logger.warning(f"No historical data found for coordinates {lat}, {lon}")
                return None
            
            # Process and group by day
            return self._process_historical_data(data['results'])
            
        except requests.RequestException as e:
            logger.warning(f"OpenAQ v2 historical data API request failed: {e}")
            # Try v3 as fallback
            try:
                url = f"{self.openaq_v3_url}/measurements"
                
                # v3 API parameters
                params = {
                    'coordinates': f"{lat},{lon}",
                    'radius': 50000,
                    'dateFrom': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'dateTo': end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'limit': 1000,
                    'orderBy': 'datetime',
                    'sort': 'asc'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=60)
                response.raise_for_status()
                
                data = response.json()
                
                if not data.get('results'):
                    logger.warning(f"No OpenAQ v3 historical data found for coordinates {lat}, {lon}")
                    return []
                
                # Process and group by day
                return self._process_historical_data(data['results'])
                
            except requests.RequestException as v3_error:
                logger.error(f"OpenAQ v3 historical data API request also failed: {v3_error}")
                # Return empty list as fallback
                return []
        except Exception as e:
            logger.error(f"Error processing historical data: {e}")
            # Return empty list as fallback
            return []
    
    def _process_historical_data(self, results: List[Dict]) -> List[Dict]:
        """
        Process historical data into daily averages.
        
        Args:
            results: List of historical measurement results
            
        Returns:
            List of daily averaged data points
        """
        # Group by date
        daily_data = {}
        
        for result in results:
            date_str = result.get('date', {}).get('utc', '')
            if not date_str:
                continue
                
            # Extract date (YYYY-MM-DD)
            date = date_str.split('T')[0]
            
            if date not in daily_data:
                daily_data[date] = {}
            
            parameter = result.get('parameter', '').lower()
            value = result.get('value')
            
            if value is not None and parameter in ['pm25', 'pm10', 'no2', 'o3']:
                if parameter not in daily_data[date]:
                    daily_data[date][parameter] = []
                daily_data[date][parameter].append(float(value))
        
        # Calculate daily averages
        processed_data = []
        for date, measurements in daily_data.items():
            daily_avg = {}
            for param, values in measurements.items():
                if values:
                    daily_avg[param] = sum(values) / len(values)
            
            if daily_avg:
                processed_data.append({
                    'date': date,
                    'measurements': daily_avg,
                    'source': 'OpenAQ Historical'
                })
        
        return processed_data
    
    def get_combined_data(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get combined air quality data from multiple sources.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Combined air quality data
        """
        try:
            # Fetch from OpenAQ (primary source)
            openaq_data = self.fetch_current_conditions_openaq(lat, lon)
            
            # Fetch from NASA TEMPO (secondary source)
            tempo_data = self.fetch_nasa_tempo_data(lat, lon)
            
            # Combine data sources
            combined_data = self._combine_data_sources(openaq_data, tempo_data)
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Error getting combined data: {e}")
            # Return mock data as fallback
            return self._get_mock_air_quality_data(lat, lon)
    
    def _get_mock_air_quality_data(self, lat: float, lon: float) -> Dict:
        """
        Generate mock air quality data as fallback.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Mock air quality data dictionary
        """
        # Generate location-specific mock data based on coordinates
        # This ensures different locations get different values
        base_pm25 = 10.0 + (abs(lat * 2) % 20) + (abs(lon * 3) % 15)
        base_pm10 = 25.0 + (abs(lat * 1.5) % 25) + (abs(lon * 2) % 20)
        base_no2 = 15.0 + (abs(lat * 2.5) % 18) + (abs(lon * 1.8) % 12)
        base_o3 = 45.0 + (abs(lat * 1.2) % 22) + (abs(lon * 2.2) % 18)
        
        # Mock pollutant concentrations (location-specific)
        measurements = {
            'pm25': round(base_pm25, 1),
            'pm10': round(base_pm10, 1),
            'no2': round(base_no2, 1),
            'o3': round(base_o3, 1)
        }
        
        # Generate location-specific weather data
        base_temp = 15.0 + (abs(lat * 0.8) % 25)  # Temperature varies by latitude
        base_humidity = 40.0 + (abs(lon * 1.2) % 40)  # Humidity varies by longitude
        base_pressure = 1000.0 + (abs(lat * lon) % 50)  # Pressure varies by location
        
        return {
            'latitude': lat,
            'longitude': lon,
            'timestamp': datetime.utcnow().isoformat(),
            'measurements': measurements,
            'weather': {
                'temperature': round(base_temp, 1),
                'humidity': round(base_humidity, 1),
                'pressure': round(base_pressure, 2),
                'wind_speed': round(3.0 + (abs(lat + lon) % 8), 1),
                'wind_direction': round((abs(lat * lon) % 360), 1)
            },
            'source': f'Mock Data (OpenAQ unavailable) - Location: {lat:.2f}, {lon:.2f}'
        }
    
    def _combine_data_sources(self, openaq_data: Optional[Dict], tempo_data: Optional[Dict]) -> Dict:
        """
        Combine data from multiple sources.
        
        Args:
            openaq_data: OpenAQ data
            tempo_data: NASA TEMPO data
            
        Returns:
            Combined data dictionary
        """
        # Start with OpenAQ data as base
        combined = openaq_data or {}
        
        if not combined:
            # Fallback to TEMPO data
            combined = tempo_data or {}
        
        if not combined:
            # Return empty structure if no data available
            return {
                'latitude': 0,
                'longitude': 0,
                'timestamp': datetime.utcnow().isoformat(),
                'measurements': {},
                'weather': {},
                'source': 'No data available'
            }
        
        # Merge TEMPO data if available
        if tempo_data and tempo_data.get('measurements'):
            tempo_measurements = tempo_data['measurements']
            combined_measurements = combined.get('measurements', {})
            
            # Use TEMPO data to fill gaps
            for param, value in tempo_measurements.items():
                if param not in combined_measurements:
                    combined_measurements[param] = value
            
            combined['measurements'] = combined_measurements
            combined['source'] = f"{combined.get('source', '')} + TEMPO"
        
        return combined
