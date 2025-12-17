"""
Demo version of the Restaurant Review Dashboard with mock data.
This version works without requiring real SerpAPI credentials.
"""

from flask import Flask, render_template, jsonify, request
import sys
import json
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Mock data for demonstration
def generate_mock_reviews():
    """Generate realistic mock review data"""
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
        {"text": "Service was excellent, food was okay.", "rating": 3.5},
        {"text": "Best restaurant in the area! Amazing flavors.", "rating": 5.0},
        {"text": "Decent food but long wait times.", "rating": 3.0},
        {"text": "Wonderful experience from start to finish.", "rating": 4.5},
        {"text": "Food quality has declined recently.", "rating": 2.5},
        {"text": "Great value for money and friendly staff.", "rating": 4.0},
        {"text": "Unique menu items and excellent presentation.", "rating": 4.5}
    ]
    
    for i in range(50):
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

def calculate_mock_metrics(reviews, interval='monthly'):
    """Calculate metrics from mock reviews"""
    # Overall metrics
    total_reviews = len(reviews)
    average_rating = sum(r['rating'] for r in reviews) / total_reviews if total_reviews > 0 else 0
    total_helpful_votes = sum(r['helpful_votes'] for r in reviews)
    
    # Rating distribution
    rating_distribution = {
        '5_star': len([r for r in reviews if r['rating'] >= 4.5]),
        '4_star': len([r for r in reviews if 3.5 <= r['rating'] < 4.5]),
        '3_star': len([r for r in reviews if 2.5 <= r['rating'] < 3.5]),
        '2_star': len([r for r in reviews if 1.5 <= r['rating'] < 2.5]),
        '1_star': len([r for r in reviews if r['rating'] < 1.5])
    }
    
    # Time-based trends (simplified)
    rating_trends = []
    volume_data = []
    
    # Group by time periods
    from collections import defaultdict
    date_groups = defaultdict(list)
    
    for review in reviews:
        date_key = review['date'][:7]  # YYYY-MM format
        date_groups[date_key].append(review)
    
    for date_key in sorted(date_groups.keys()):
        group_reviews = date_groups[date_key]
        avg_rating = sum(r['rating'] for r in group_reviews) / len(group_reviews)
        
        rating_trends.append({
            'date': date_key,
            'average_rating': round(avg_rating, 2)
        })
        
        volume_data.append({
            'date': date_key,
            'review_count': len(group_reviews)
        })
    
    # Mock themes
    themes = [
        {'theme': 'Great Service', 'frequency': 15},
        {'theme': 'Delicious Food', 'frequency': 12},
        {'theme': 'Nice Atmosphere', 'frequency': 8},
        {'theme': 'Good Value', 'frequency': 6},
        {'theme': 'Fresh Ingredients', 'frequency': 5}
    ]
    
    return {
        'overall_metrics': {
            'total_reviews': total_reviews,
            'average_rating': round(average_rating, 2),
            'total_helpful_votes': total_helpful_votes,
            'rating_distribution': rating_distribution
        },
        'rating_trends': rating_trends,
        'volume_data': volume_data,
        'themes': themes
    }

def calculate_mock_sentiment(reviews):
    """Calculate sentiment analysis from mock reviews"""
    positive_count = len([r for r in reviews if r['rating'] >= 4.0])
    negative_count = len([r for r in reviews if r['rating'] < 3.0])
    neutral_count = len(reviews) - positive_count - negative_count
    
    total = len(reviews)
    
    return {
        'sentiment_distribution': {
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count
        },
        'sentiment_percentages': {
            'positive': round((positive_count / total) * 100, 1) if total > 0 else 0,
            'negative': round((negative_count / total) * 100, 1) if total > 0 else 0,
            'neutral': round((neutral_count / total) * 100, 1) if total > 0 else 0
        },
        'total_reviews': total,
        'analyzed_reviews': total,
        'average_confidence': 0.85
    }

# Generate mock data once
mock_reviews = generate_mock_reviews()

@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template('dashboard.html', config={'demo_mode': True})

@app.route('/api/reviews')
def get_reviews():
    """Mock reviews endpoint"""
    start = request.args.get('start', 0, type=int)
    num_reviews = request.args.get('num', 100, type=int)
    
    # Paginate mock reviews
    end = start + num_reviews
    paginated_reviews = mock_reviews[start:end]
    
    return jsonify({
        "success": True,
        "data": {
            "reviews": paginated_reviews,
            "metadata": {
                "total_results": len(mock_reviews),
                "place_id": "demo-restaurant",
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
    metrics_data = calculate_mock_metrics(mock_reviews, interval)
    
    return jsonify({
        "success": True,
        "data": metrics_data,
        "metadata": {
            "place_id": "demo-restaurant",
            "fetched_at": datetime.utcnow().isoformat()
        }
    })

@app.route('/api/sentiment')
def get_sentiment():
    """Mock sentiment endpoint"""
    sentiment_data = calculate_mock_sentiment(mock_reviews)
    
    return jsonify({
        "success": True,
        "data": sentiment_data,
        "metadata": {
            "place_id": "demo-restaurant",
            "fetched_at": datetime.utcnow().isoformat()
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0-demo",
        "mode": "demo"
    })

if __name__ == '__main__':
    print("Starting Restaurant Review Dashboard (Demo Mode)...")
    print("This version uses mock data and doesn't require SerpAPI credentials.")
    
    try:
        # Use PORT environment variable for cloud deployment, fallback to 8001 for local
        port = int(os.environ.get('PORT', 8001))
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"Failed to start demo server: {str(e)}")
        sys.exit(1)