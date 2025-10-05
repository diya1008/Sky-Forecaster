"""
Validation utilities for Sky Forecaster application.
"""
from typing import Tuple, Optional


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate latitude and longitude coordinates.
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        
    Returns:
        True if coordinates are valid, False otherwise
    """
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        return False
    
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def validate_location_input(location_input: str) -> Tuple[bool, Optional[str], Optional[float], Optional[float]]:
    """
    Validate location input string.
    
    Args:
        location_input: Location input string (could be coordinates or address)
        
    Returns:
        Tuple of (is_valid, error_message, latitude, longitude)
    """
    if not location_input or not isinstance(location_input, str):
        return False, "Location input is required", None, None
    
    location_input = location_input.strip()
    
    # Check if input is coordinates (lat, lon format)
    if ',' in location_input:
        try:
            coords = location_input.split(',')
            if len(coords) == 2:
                lat = float(coords[0].strip())
                lon = float(coords[1].strip())
                
                if validate_coordinates(lat, lon):
                    return True, None, lat, lon
                else:
                    return False, "Invalid coordinate values", None, None
        except ValueError:
            return False, "Invalid coordinate format", None, None
    
    # For address input, we'll let the geocoding service handle validation
    return True, None, None, None


def validate_aqi_value(aqi: int) -> bool:
    """
    Validate AQI value.
    
    Args:
        aqi: AQI value
        
    Returns:
        True if AQI is valid, False otherwise
    """
    return isinstance(aqi, int) and 0 <= aqi <= 500


def validate_pollutant_concentration(concentration: float, pollutant: str) -> bool:
    """
    Validate pollutant concentration value.
    
    Args:
        concentration: Pollutant concentration
        pollutant: Pollutant type
        
    Returns:
        True if concentration is valid, False otherwise
    """
    if not isinstance(concentration, (int, float)):
        return False
    
    if concentration < 0:
        return False
    
    # Set reasonable upper limits for different pollutants
    limits = {
        'pm25': 1000,  # μg/m³
        'pm10': 2000,  # μg/m³
        'no2': 5000,   # μg/m³
        'o3': 1000,    # μg/m³
        'co': 100,     # mg/m³
        'so2': 2000    # μg/m³
    }
    
    return concentration <= limits.get(pollutant, 10000)
