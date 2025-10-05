# Sky Forecaster 🌤️

## NASA Space Apps Challenge 2025 Submission

**Project Name:** Sky Forecaster  
**Challenge:** From EarthData to Action: Cloud Computing with Earth Observation Data for Predicting Cleaner, Safer Skies  
**Team:** Mambacita  
**Event:** Nirma University
---

## High-Level Project Summary

Sky Forecaster is a data-driven web application that addresses the critical challenge of air quality prediction and monitoring using NASA Earth observation data. Our project harnesses cloud computing to process satellite data and ground-based measurements, providing real-time air quality forecasts to help communities make informed decisions about outdoor activities and health safety.

**What we developed:** A comprehensive air quality monitoring and forecasting platform that integrates NASA TEMPO satellite data, OpenAQ ground measurements, and meteorological data to predict air quality conditions up to 7 days in advance.

**How it addresses the challenge:** By combining NASA Earth observation data with cloud computing capabilities, we provide actionable air quality information that helps communities predict and prepare for poor air quality conditions, contributing to cleaner, safer skies.

**Why it's important:** Air pollution affects billions of people worldwide, causing millions of premature deaths annually. Our solution democratizes access to NASA's satellite data, making advanced air quality predictions available to communities that may not have access to sophisticated monitoring infrastructure.

## Project Structure

```
sky-forecaster/
├── backend/
│   ├── app.py              # Flask application
│   ├── config.py           # Configuration settings
│   ├── models/             # Data models
│   ├── services/           # API services and data processing
│   ├── utils/              # Utility functions
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── css/
│   │   └── style.css       # Stylesheet
│   ├── js/
│   │   ├── app.js          # Main JavaScript application
│   │   ├── map.js          # Leaflet.js mapping functionality
│   │   └── utils.js        # Utility functions
│   └── assets/             # Static assets
├── .env                    # Environment variables
└── README.md
```

## Features

- Real-time air quality monitoring using NASA Earthdata and OpenAQ
- Interactive mapping with Leaflet.js
- AQI calculation and forecasting
- Responsive design for mobile and desktop
- Clean separation of concerns between backend and frontend

---

## Detailed Project Description

### What exactly does it do?

Sky Forecaster provides:
- **Real-time Air Quality Monitoring**: Current conditions for any location worldwide
- **Air Quality Forecasting**: Predictions up to 7 days in advance
- **Interactive Mapping**: Visual representation of air quality data with clickable locations
- **AQI Calculation**: Standardized Air Quality Index using EPA methodology
- **Location Search**: Find air quality data for any city or address
- **Health Recommendations**: Guidance based on current air quality conditions

### How does it work?

1. **Data Collection**: Integrates multiple data sources including NASA TEMPO satellite data, OpenAQ ground measurements, and meteorological data
2. **Data Processing**: Cloud-based processing using Flask backend to aggregate and analyze data
3. **Prediction Algorithm**: Machine learning-based forecasting using historical trends and current conditions
4. **User Interface**: Interactive web application with real-time updates and responsive design

### What benefits does it have?

- **Public Health**: Helps individuals make informed decisions about outdoor activities
- **Accessibility**: Democratizes access to advanced air quality data
- **Real-time**: Provides up-to-date information for immediate decision making
- **Predictive**: Forecasts help communities prepare for poor air quality events
- **Global Coverage**: Works for any location worldwide

### What do you hope to achieve?

- Improve public health outcomes through better air quality awareness
- Increase accessibility to NASA Earth observation data
- Demonstrate the power of cloud computing for environmental monitoring
- Contribute to cleaner, safer skies through informed decision making

### Tools, coding languages, hardware, and software used:

**Backend:**
- Python 3.12
- Flask (Web framework)
- earthaccess (NASA data access)
- requests (HTTP client)
- python-dotenv (Environment configuration)
- Flask-Cors (Cross-origin resource sharing)

**Frontend:**
- HTML5, CSS3
- Vanilla JavaScript (ES6+)
- Leaflet.js (Interactive mapping)
- Fetch API (HTTP requests)

**Data Sources:**
- NASA TEMPO satellite data
- OpenAQ ground-based measurements
- OpenStreetMap Nominatim (Geocoding)

---

## NASA Data Usage

### Specific NASA Data Used:
- **NASA TEMPO (Tropospheric Emissions: Monitoring of Pollution)**: 
  - Nitrogen dioxide (NO₂) measurements
  - Formaldehyde (CH₂O) measurements
  - Aerosol Index (AI)
  - Ozone (O₃) concentrations
- **NASA EarthData Cloud**: Cloud-based access to satellite data
- **NASA Giovanni**: Data visualization and analysis tools

### How NASA Data is Used:
1. **Primary Data Source**: TEMPO satellite data provides high-resolution air quality measurements
2. **Validation**: NASA data validates and enhances ground-based measurements
3. **Gap Filling**: Satellite data fills geographical gaps where ground stations are unavailable
4. **Temporal Coverage**: Provides continuous monitoring capabilities

### NASA Data Integration:
- Real-time access to TEMPO data through earthaccess Python library
- Cloud-computing approach for processing large satellite datasets
- Integration with ground-based measurements for comprehensive coverage

---

## Space Agency Partner & Other Data

### Data Sources:
- **NASA**: TEMPO satellite data, EarthData Cloud
- **OpenAQ**: Ground-based air quality measurements
- **OpenStreetMap**: Geocoding and mapping services
- **Meteorological Data**: Weather conditions for enhanced predictions

### Resources and Tools:
- **Open Source Libraries**: Leaflet.js, Flask, earthaccess
- **Cloud Services**: NASA EarthData Cloud
- **Development Tools**: Python, JavaScript, HTML5, CSS3
- **Data Formats**: JSON, GeoJSON for data exchange

---

## Use of Artificial Intelligence

**AI Tools Utilized:**
- **Claude AI (Anthropic)**: Used for code development assistance, documentation generation, and project planning
- **Purpose**: Accelerated development process and ensured best practices in coding and documentation

**AI Usage Disclosure:**
- Code development: AI-assisted with code review and optimization
- Documentation: AI-assisted with README and technical documentation
- Project planning: AI-assisted with task organization and requirement analysis

**Note**: All AI-generated content has been reviewed, modified, and validated by the development team. The core algorithms, data processing logic, and application functionality are original work.

---

## Getting Started

### Prerequisites
- Python 3.12+
- Modern web browser
- Internet connection (for data sources)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/[your-username]/sky-forecaster.git
   cd sky-forecaster
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your NASA EarthData credentials (optional)
   ```

5. **Start the application:**
   ```bash
   # Start backend
   python start_backend.py
   
   # Open frontend in browser
   open frontend/index.html
   ```

### Usage
1. Open the application in your web browser
2. Search for a location or click on the map
3. View current air quality conditions
4. Check the forecast for upcoming days
5. Use health recommendations for outdoor activities

---

## Demo Links

**Project Demo**: https://drive.google.com/file/d/1CVGEYekDH6Xb-Fy51M9mf42EJ-xqkj0N/view?usp=sharing

---

## Judging Criteria Alignment

### Impact
- Addresses global air quality challenges affecting billions of people
- Provides actionable information for public health decisions
- Democratizes access to NASA satellite data

### Creativity
- Innovative integration of satellite and ground-based data
- Interactive mapping interface for intuitive data exploration
- Cloud-computing approach for scalable data processing

### Validity
- Uses scientifically validated AQI calculation methods
- Integrates multiple authoritative data sources
- Implements proper error handling and data validation

### Relevance
- Directly addresses the NASA challenge theme
- Uses NASA Earth observation data as primary source
- Focuses on cleaner, safer skies objective

### Presentation
- Clean, intuitive user interface
- Comprehensive documentation
- Clear demonstration of functionality

---

## Future Enhancements

- Machine learning models for improved forecasting accuracy
- Mobile application development
- Integration with additional NASA datasets
- Community reporting features
- Historical data analysis tools

---

## License

This project is open source and available under the MIT License.

---

## Team Information

**Team Members:** [Add your team member names and roles]  
**Contact:** [Add contact information]  
**Repository:** https://github.com/diya1008/Sky-Forecaster
