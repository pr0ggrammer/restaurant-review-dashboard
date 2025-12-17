"""
Vercel-compatible entry point for the Restaurant Review Dashboard
"""

import os
import sys

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app
from app import app

# Vercel expects the Flask app to be available as 'app'
# This is the WSGI application that Vercel will use
application = app

# For local testing
if __name__ == "__main__":
    app.run(debug=False)