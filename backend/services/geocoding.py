"""
Geocoding service for Sky Forecaster application.
Provides location search and coordinate lookup functionality.
"""
import requests
import logging
from typing import Optional, Tuple, Dict

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service for geocoding addresses and locations."""
    
    def __init__(self):
        self.nominatim_base_url = "https://nominatim.openstreetmap.org"
    
    def geocode_address(self, address: str) -> Optional[Dict]:
        """
        Geocode an address to coordinates using OpenStreetMap Nominatim.
        
        Args:
            address: Address string to geocode
            
        Returns:
            Dictionary with coordinates and address info, or None if not found
        """
        try:
            url = f"{self.nominatim_base_url}/search"
            
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1,
                'extratags': 1
            }
            
            headers = {
                'User-Agent': 'SkyForecaster/1.0 (NASA Space Apps Challenge 2025)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                logger.warning(f"No geocoding results found for address: {address}")
                return None
            
            result = data[0]
            
            return {
                'latitude': float(result['lat']),
                'longitude': float(result['lon']),
                'display_name': result.get('display_name', address),
                'address': result.get('address', {}),
                'place_id': result.get('place_id'),
                'type': result.get('type'),
                'source': 'OpenStreetMap Nominatim'
            }
            
        except requests.RequestException as e:
            logger.error(f"Geocoding request failed: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing geocoding response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in geocoding: {e}")
            return None
    
    def reverse_geocode(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Reverse geocode coordinates to an address.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with address info, or None if not found
        """
        try:
            url = f"{self.nominatim_base_url}/reverse"
            
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1,
                'extratags': 1
            }
            
            headers = {
                'User-Agent': 'SkyForecaster/1.0 (NASA Space Apps Challenge 2025)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or 'error' in data:
                logger.warning(f"No reverse geocoding results found for {lat}, {lon}")
                return None
            
            return {
                'latitude': lat,
                'longitude': lon,
                'display_name': data.get('display_name', f"{lat}, {lon}"),
                'address': data.get('address', {}),
                'place_id': data.get('place_id'),
                'type': data.get('type'),
                'source': 'OpenStreetMap Nominatim'
            }
            
        except requests.RequestException as e:
            logger.error(f"Reverse geocoding request failed: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing reverse geocoding response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in reverse geocoding: {e}")
            return None
    
    def search_nearby_places(self, lat: float, lon: float, query: str, radius: int = 1000) -> list:
        """
        Search for nearby places using coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            query: Search query
            radius: Search radius in meters
            
        Returns:
            List of nearby place results
        """
        try:
            url = f"{self.nominatim_base_url}/search"
            
            params = {
                'q': query,
                'format': 'json',
                'limit': 10,
                'addressdetails': 1,
                'extratags': 1,
                'bounded': 1,
                'viewbox': f"{lon-0.01},{lat-0.01},{lon+0.01},{lat+0.01}"
            }
            
            headers = {
                'User-Agent': 'SkyForecaster/1.0 (NASA Space Apps Challenge 2025)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data:
                try:
                    result = {
                        'latitude': float(item['lat']),
                        'longitude': float(item['lon']),
                        'display_name': item.get('display_name', query),
                        'address': item.get('address', {}),
                        'place_id': item.get('place_id'),
                        'type': item.get('type'),
                        'importance': item.get('importance', 0),
                        'source': 'OpenStreetMap Nominatim'
                    }
                    results.append(result)
                except (KeyError, ValueError) as e:
                    logger.warning(f"Skipping invalid search result: {e}")
                    continue
            
            return results
            
        except requests.RequestException as e:
            logger.error(f"Nearby places search failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in nearby places search: {e}")
            return []
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """
        Validate that coordinates are within valid ranges.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            True if coordinates are valid
        """
        try:
            lat = float(lat)
            lon = float(lon)
            
            return -90 <= lat <= 90 and -180 <= lon <= 180
        except (ValueError, TypeError):
            return False
    
    def get_location_info(self, location_input: str) -> Optional[Dict]:
        """
        Get location information from various input formats.
        
        Args:
            location_input: Location string (address, coordinates, etc.)
            
        Returns:
            Location information dictionary
        """
        if not location_input or not isinstance(location_input, str):
            return None
        
        location_input = location_input.strip()
        
        # Check if input is coordinates
        if ',' in location_input:
            try:
                coords = location_input.split(',')
                if len(coords) == 2:
                    lat = float(coords[0].strip())
                    lon = float(coords[1].strip())
                    
                    if self.validate_coordinates(lat, lon):
                        # Try to get address info for coordinates
                        address_info = self.reverse_geocode(lat, lon)
                        if address_info:
                            return address_info
                        else:
                            return {
                                'latitude': lat,
                                'longitude': lon,
                                'display_name': f"{lat}, {lon}",
                                'source': 'Coordinates'
                            }
            except ValueError:
                pass
        
        # Try to geocode as address
        return self.geocode_address(location_input)
