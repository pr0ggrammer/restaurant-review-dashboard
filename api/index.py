"""
Vercel API endpoint - Serverless deployment entry point
Fixed: Removed vercel_app.py to prevent import conflicts
"""

import os
import sys
from datetime import datetime, timedelta
import json
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, render_template, jsonify, request

# Create Flask app for Vercel
app = Flask(__name__, 
           template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
           static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))

# Mock data for demo (since SerpAPI might have issues in serverless)
def generate_mock_data():
    """Generate mock review data for demo purposes"""
    reviews = []
    base_date = datetime.now() - timedelta(days=90)
    
    sample_reviews = [
        {"text": "Excellent food and service! Highly recommend this place.", "rating": 5.0},
        {"text": "Good food but service was a bit slow.", "rating": 4.0},
        {"text": "Disappointing experience. Food was cold and staff was rude.", "rating": 2.0},
        {"text": "Great atmosphere and delicious food. Will come back!", "rating": 4.5},
        {"text": "Average food, nothing special but not bad either.", "rating": 3.0},
        {"text": "Outstanding dining experience! Perfect for special occasions.", "rating": 5.0},
        {"text": "Nice ambiance but overpriced for the quality.", "rating": 3.5},
        {"text": "Fresh ingredients and creative dishes. Loved it!", "rating": 4.5},
    ]
    
    for i in range(20):
        review_data = random.choice(sample_reviews)
        review_date = base_date + timedelta(days=random.randint(0, 90))
        
        reviews.append({
            'review_id': f'demo_review_{i}',
            'rating': review_data['rating'],
            'review_text': review_data['text'],
            'date': review_date.strftime('%Y-%m-%d'),
            'reviewer_name': f'Customer {i+1}',
            'helpful_votes': random.randint(0, 10)
        })
    
    return reviews

# Generate mock data
mock_reviews = generate_mock_data()

@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template('dashboard.html', config={'demo_mode': True})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0-vercel",
        "mode": "serverless"
    })

@app.route('/api/reviews')
def get_reviews():
    """Mock reviews endpoint"""
    start = request.args.get('start', 0, type=int)
    num_reviews = request.args.get('num', 100, type=int)
    
    end = start + num_reviews
    paginated_reviews = mock_reviews[start:end]
    
    return jsonify({
        "success": True,
        "data": {
            "reviews": paginated_reviews,
            "metadata": {
                "total_results": len(mock_reviews),
                "place_id": "demo-restaurant-vercel",
                "fetched_at": datetime.utcnow().isoformat()
            }
        },
        "pagination": {
            "start": start,
            "requested": num_reviews,
            "returned": len(paginated_reviews)
        }
    })

@app.route('/api/metrics')
def get_metrics():
    """Mock metrics endpoint"""
    interval = request.args.get('interval', 'monthly')
    
    # Calculate metrics from mock data
    total_reviews = len(mock_reviews)
    average_rating = sum(r['rating'] for r in mock_reviews) / total_reviews if total_reviews > 0 else 0
    
    # Rating distribution
    rating_distribution = {
        '5_star': len([r for r in mock_reviews if r['rating'] >= 4.5]),
        '4_star': len([r for r in mock_reviews if 3.5 <= r['rating'] < 4.5]),
        '3_star': len([r for r in mock_reviews if 2.5 <= r['rating'] < 3.5]),
        '2_star': len([r for r in mock_reviews if 1.5 <= r['rating'] < 2.5]),
        '1_star': len([r for r in mock_reviews if r['rating'] < 1.5])
    }
    
    # Mock trends and themes
    rating_trends = [
        {'date': '2024-01', 'average_rating': 4.2},
        {'date': '2024-02', 'average_rating': 4.1},
        {'date': '2024-03', 'average_rating': 4.3},
    ]
    
    volume_data = [
        {'date': '2024-01', 'review_count': 8},
        {'date': '2024-02', 'review_count': 6},
        {'date': '2024-03', 'review_count': 6},
    ]
    
    themes = [
        {'theme': 'Great Service', 'frequency': 15},
        {'theme': 'Delicious Food', 'frequency': 12},
        {'theme': 'Nice Atmosphere', 'frequency': 8},
    ]
    
    return jsonify({
        "success": True,
        "data": {
            "overall_metrics": {
                "total_reviews": total_reviews,
                "average_rating": round(average_rating, 2),
                "total_helpful_votes": sum(r['helpful_votes'] for r in mock_reviews),
                "rating_distribution": rating_distribution
            },
            "rating_trends": rating_trends,
            "volume_data": volume_data,
            "themes": themes
        }
    })

@app.route('/api/sentiment')
def get_sentiment():
    """Mock sentiment endpoint"""
    positive_count = len([r for r in mock_reviews if r['rating'] >= 4.0])
    negative_count = len([r for r in mock_reviews if r['rating'] < 3.0])
    neutral_count = len(mock_reviews) - positive_count - negative_count
    
    total = len(mock_reviews)
    
    return jsonify({
        "success": True,
        "data": {
            "sentiment_distribution": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count
            },
            "sentiment_percentages": {
                "positive": round((positive_count / total) * 100, 1) if total > 0 else 0,
                "negative": round((negative_count / total) * 100, 1) if total > 0 else 0,
                "neutral": round((neutral_count / total) * 100, 1) if total > 0 else 0
            },
            "total_reviews": total,
            "analyzed_reviews": total,
            "average_confidence": 0.85
        }
    })

# Vercel handler function
def handler(event, context):
    """Vercel serverless handler"""
    return app

# For Vercel compatibility
app = app