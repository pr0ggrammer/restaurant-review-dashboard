"""
Vercel-compatible entry point for the Restaurant Review Dashboard
"""

from app import app

# Vercel expects the Flask app to be available as 'app'
# This file serves as the entry point for Vercel deployment

if __name__ == "__main__":
    app.run(debug=False)