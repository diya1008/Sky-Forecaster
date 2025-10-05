"""
Air quality data models.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class AirQualityData:
    """Represents air quality data for a specific location and time."""
    
    latitude: float
    longitude: float
    aqi: int
    primary_pollutant: str
    timestamp: datetime
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    no2: Optional[float] = None
    o3: Optional[float] = None
    co: Optional[float] = None
    so2: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'aqi': self.aqi,
            'primary_pollutant': self.primary_pollutant,
            'timestamp': self.timestamp.isoformat(),
            'pm25': self.pm25,
            'pm10': self.pm10,
            'no2': self.no2,
            'o3': self.o3,
            'co': self.co,
            'so2': self.so2,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AirQualityData':
        """Create instance from dictionary."""
        return cls(
            latitude=data['latitude'],
            longitude=data['longitude'],
            aqi=data['aqi'],
            primary_pollutant=data['primary_pollutant'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            pm25=data.get('pm25'),
            pm10=data.get('pm10'),
            no2=data.get('no2'),
            o3=data.get('o3'),
            co=data.get('co'),
            so2=data.get('so2'),
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            pressure=data.get('pressure'),
            wind_speed=data.get('wind_speed'),
            wind_direction=data.get('wind_direction')
        )


@dataclass
class ForecastData:
    """Represents forecasted air quality data."""
    
    latitude: float
    longitude: float
    forecast_hours: int
    timestamp: datetime
    predictions: list[AirQualityData]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'forecast_hours': self.forecast_hours,
            'timestamp': self.timestamp.isoformat(),
            'predictions': [pred.to_dict() for pred in self.predictions]
        }
