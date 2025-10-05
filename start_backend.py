#!/usr/bin/env python3
"""
Start script for Sky Forecaster backend.
"""

import os
import sys

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Set environment variables if .env file exists
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    from dotenv import load_dotenv
    load_dotenv(env_file)

if __name__ == '__main__':
    from backend.app import create_app
    
    app = create_app()
    
    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Sky Forecaster backend on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {os.environ.get('FLASK_CONFIG', 'development')}")
    
    app.run(host=host, port=port, debug=debug)
