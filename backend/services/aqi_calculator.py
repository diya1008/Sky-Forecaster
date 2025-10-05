"""
AQI calculation service.
"""
from typing import Tuple, Optional


class AQICalculator:
    """Calculates Air Quality Index (AQI) based on pollutant concentrations."""
    
    # AQI breakpoints for different pollutants (concentration, AQI)
    BREAKPOINTS = {
        'pm25': [
            (0, 12.0, 0, 50),
            (12.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150),
            (55.5, 150.4, 151, 200),
            (150.5, 250.4, 201, 300),
            (250.5, 500.4, 301, 500)
        ],
        'pm10': [
            (0, 54, 0, 50),
            (55, 154, 51, 100),
            (155, 254, 101, 150),
            (255, 354, 151, 200),
            (355, 424, 201, 300),
            (425, 604, 301, 500)
        ],
        'no2': [
            (0, 53, 0, 50),
            (54, 100, 51, 100),
            (101, 360, 101, 150),
            (361, 649, 151, 200),
            (650, 1249, 201, 300),
            (1250, 2049, 301, 500)
        ],
        'o3': [
            (0, 54, 0, 50),
            (55, 70, 51, 100),
            (71, 85, 101, 150),
            (86, 105, 151, 200),
            (106, 200, 201, 300),
            (201, 400, 301, 500)
        ]
    }
    
    @classmethod
    def calculate_aqi(cls, pollutant: str, concentration: float) -> Tuple[int, str]:
        """
        Calculate AQI for a specific pollutant.
        
        Args:
            pollutant: Pollutant type (pm25, pm10, no2, o3)
            concentration: Pollutant concentration
            
        Returns:
            Tuple of (AQI value, pollutant name)
        """
        if pollutant not in cls.BREAKPOINTS:
            raise ValueError(f"Unknown pollutant: {pollutant}")
        
        # Find the appropriate breakpoint range
        for c_low, c_high, aqi_low, aqi_high in cls.BREAKPOINTS[pollutant]:
            if c_low <= concentration <= c_high:
                # Linear interpolation formula
                aqi = ((aqi_high - aqi_low) / (c_high - c_low)) * (concentration - c_low) + aqi_low
                return round(aqi), pollutant
        
        # If concentration is above the highest breakpoint
        if concentration > cls.BREAKPOINTS[pollutant][-1][1]:
            return 500, pollutant
        
        return 0, pollutant
    
    @classmethod
    def calculate_overall_aqi(cls, pollutants: dict) -> Tuple[int, str]:
        """
        Calculate overall AQI from multiple pollutants.
        
        Args:
            pollutants: Dictionary of pollutant concentrations
                e.g., {'pm25': 15.5, 'pm10': 45.0, 'no2': 25.0}
        
        Returns:
            Tuple of (overall AQI, primary pollutant)
        """
        if not pollutants:
            return 0, "unknown"
        
        max_aqi = 0
        primary_pollutant = "unknown"
        
        for pollutant, concentration in pollutants.items():
            if concentration is not None and concentration > 0:
                try:
                    aqi, _ = cls.calculate_aqi(pollutant, concentration)
                    if aqi > max_aqi:
                        max_aqi = aqi
                        primary_pollutant = pollutant
                except ValueError:
                    continue
        
        return max_aqi, primary_pollutant
    
    @classmethod
    def get_aqi_category(cls, aqi: int) -> str:
        """
        Get AQI category based on AQI value.
        
        Args:
            aqi: AQI value
            
        Returns:
            AQI category string
        """
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"
    
    @classmethod
    def get_aqi_color(cls, aqi: int) -> str:
        """
        Get color code for AQI value.
        
        Args:
            aqi: AQI value
            
        Returns:
            Hex color code
        """
        if aqi <= 50:
            return "#00e400"  # Green
        elif aqi <= 100:
            return "#ffff00"  # Yellow
        elif aqi <= 150:
            return "#ff7e00"  # Orange
        elif aqi <= 200:
            return "#ff0000"  # Red
        elif aqi <= 300:
            return "#8f3f97"  # Purple
        else:
            return "#7e0023"  # Maroon
