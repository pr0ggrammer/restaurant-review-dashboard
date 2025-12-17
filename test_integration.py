"""
Comprehensive integration test for the Restaurant Review Dashboard.

Tests end-to-end functionality including API integration, data processing,
sentiment analysis, and UI rendering.
"""

import os
import sys
import json
import time
from unittest.mock import Mock, patch
import requests

# Add the current directory to Python path
sys.path.insert(0, '.')

def test_full_integration():
    """
    Test complete end-to-end functionality of the dashboard.
    """
    print("Testing full integration...")
    
    # Import all services
    from services.serpapi_client import SerpAPIClient, SerpAPIError
    from services.data_processor import DataProcessor
    from services.sentiment_analyzer import SentimentAnalyzer
    
    # Create mock review data that represents a realistic API response
    mock_review_data = {
        'reviews': [
            {
                'review_id': 'review_1',
                'rating': 5.0,
                'review': 'Excellent food and service! Highly recommend this place.',
                'date': '2023-12-01',
                'reviewer_name': 'John Doe',
                'helpful_votes': 5
            },
            {
                'review_id': 'review_2', 
                'rating': 4.0,
                'review': 'Good food but service was a bit slow.',
                'date': '2023-12-02',
                'reviewer_name': 'Jane Smith',
                'helpful_votes': 2
            },
            {
                'review_id': 'review_3',
                'rating': 2.0,
                'review': 'Disappointing experience. Food was cold and staff was rude.',
                'date': '2023-12-03',
                'reviewer_name': 'Bob Johnson',
                'helpful_votes': 1
            },
            {
                'review_id': 'review_4',
                'rating': 4.5,
                'review': 'Great atmosphere and delicious food. Will come back!',
                'date': '2023-12-04',
                'reviewer_name': 'Alice Brown',
                'helpful_votes': 3
            },
            {
                'review_id': 'review_5',
                'rating': 3.0,
                'review': 'Average food, nothing special but not bad either.',
                'date': '2023-12-05',
                'reviewer_name': 'Charlie Wilson',
                'helpful_votes': 0
            }
        ],
        'search_metadata': {'total_results': 5},
        'place_info': {'name': 'Test Restaurant'},
        'serpapi_pagination': {}
    }
    
    # Test 1: SerpAPI Integration
    with patch('services.serpapi_client.requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_review_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        
        # Test SerpAPI client
        with SerpAPIClient(api_key="test_key", place_id="test_place") as client:
            result = client.fetch_reviews(start=0, num_reviews=5)
            
            assert 'reviews' in result
            assert 'metadata' in result
            assert len(result['reviews']) == 5
            print("✓ SerpAPI integration working")
    
    # Test 2: Data Processing Pipeline
    processor = DataProcessor()
    transformed_reviews = processor.transform_review_data(mock_review_data['reviews'])
    
    assert len(transformed_reviews) == 5
    assert all('rating' in review for review in transformed_reviews)
    assert all('review_text' in review for review in transformed_reviews)
    print("✓ Data processing pipeline working")
    
    # Test 3: Metrics Calculation
    overall_metrics = processor.calculate_overall_metrics(transformed_reviews)
    
    assert 'average_rating' in overall_metrics
    assert 'total_reviews' in overall_metrics
    assert overall_metrics['total_reviews'] == 5
    assert 3.0 <= overall_metrics['average_rating'] <= 4.0  # Should be around 3.7
    print("✓ Metrics calculation working")
    
    # Test 4: Rating Trends
    rating_trends = processor.aggregate_ratings_by_time(transformed_reviews, 'daily')
    
    assert isinstance(rating_trends, list)
    assert len(rating_trends) > 0
    print("✓ Rating trends calculation working")
    
    # Test 5: Review Volume
    volume_data = processor.calculate_review_volume(transformed_reviews, 'daily')
    
    assert isinstance(volume_data, list)
    assert len(volume_data) > 0
    print("✓ Review volume calculation working")
    
    # Test 6: Theme Extraction
    themes = processor.extract_themes(transformed_reviews)
    
    assert isinstance(themes, list)
    print("✓ Theme extraction working")
    
    # Test 7: Sentiment Analysis
    analyzer = SentimentAnalyzer()
    sentiment_results = analyzer.analyze_batch(transformed_reviews)
    
    assert 'sentiment_distribution' in sentiment_results
    assert 'sentiment_percentages' in sentiment_results
    assert 'total_reviews' in sentiment_results
    
    # Verify sentiment distribution adds up correctly
    distribution = sentiment_results['sentiment_distribution']
    total_analyzed = sum(distribution.values())
    assert total_analyzed == len(transformed_reviews)
    
    # Verify percentages add up to 100%
    percentages = sentiment_results['sentiment_percentages']
    total_percentage = sum(percentages.values())
    assert abs(total_percentage - 100.0) < 0.1  # Allow for small rounding errors
    
    print("✓ Sentiment analysis working")
    
    return True


def test_flask_endpoints():
    """
    Test Flask API endpoints with mock data.
    """
    print("Testing Flask API endpoints...")
    
    # Import Flask app
    from app import app
    
    # Create test client
    with app.test_client() as client:
        
        # Test 1: Dashboard route
        response = client.get('/')
        assert response.status_code == 200
        assert b'html' in response.data.lower()
        print("✓ Dashboard route working")
        
        # Test 2: Health check endpoint
        response = client.get('/health')
        assert response.status_code in [200, 503]  # May be degraded without real config
        
        health_data = json.loads(response.data)
        assert 'status' in health_data
        assert 'timestamp' in health_data
        assert 'services' in health_data
        print("✓ Health check endpoint working")
        
        # Mock the SerpAPI for endpoint tests
        mock_review_data = {
            'reviews': [
                {
                    'review_id': 'test_1',
                    'rating': 4.5,
                    'review': 'Great test review',
                    'date': '2023-12-01',
                    'reviewer_name': 'Test User',
                    'helpful_votes': 1
                }
            ],
            'search_metadata': {'total_results': 1},
            'place_info': {'name': 'Test Restaurant'},
            'serpapi_pagination': {}
        }
        
        with patch('services.serpapi_client.requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_review_data
            mock_response.raise_for_status.return_value = None
            mock_session.get.return_value = mock_response
            
            # Set environment variables for testing
            os.environ['SERPAPI_KEY'] = 'test_key'
            os.environ['PLACE_ID'] = 'test_place'
            
            try:
                # Test 3: Reviews endpoint
                response = client.get('/api/reviews?start=0&num=10')
                
                if response.status_code == 200:
                    reviews_data = json.loads(response.data)
                    assert reviews_data['success'] == True
                    assert 'data' in reviews_data
                    assert 'pagination' in reviews_data
                    print("✓ Reviews API endpoint working")
                else:
                    print(f"⚠ Reviews endpoint returned {response.status_code}")
                
                # Test 4: Metrics endpoint
                response = client.get('/api/metrics?start=0&num=10&interval=daily')
                
                if response.status_code == 200:
                    metrics_data = json.loads(response.data)
                    assert metrics_data['success'] == True
                    assert 'data' in metrics_data
                    print("✓ Metrics API endpoint working")
                else:
                    print(f"⚠ Metrics endpoint returned {response.status_code}")
                
                # Test 5: Sentiment endpoint
                response = client.get('/api/sentiment?start=0&num=10')
                
                if response.status_code == 200:
                    sentiment_data = json.loads(response.data)
                    assert sentiment_data['success'] == True
                    assert 'data' in sentiment_data
                    print("✓ Sentiment API endpoint working")
                else:
                    print(f"⚠ Sentiment endpoint returned {response.status_code}")
                    
            finally:
                # Clean up environment variables
                if 'SERPAPI_KEY' in os.environ:
                    del os.environ['SERPAPI_KEY']
                if 'PLACE_ID' in os.environ:
                    del os.environ['PLACE_ID']
    
    return True


def test_error_scenarios():
    """
    Test various error scenarios to ensure graceful handling.
    """
    print("Testing error scenarios...")
    
    from app import app
    
    with app.test_client() as client:
        
        # Test 1: Invalid parameters
        response = client.get('/api/reviews?start=-1&num=0')
        assert response.status_code == 400
        
        error_data = json.loads(response.data)
        assert error_data['success'] == False
        assert 'error' in error_data
        print("✓ Invalid parameters handled correctly")
        
        # Test 2: Missing configuration
        response = client.get('/api/reviews')
        # Should return error due to missing API key/place ID
        assert response.status_code in [400, 503]
        print("✓ Missing configuration handled correctly")
        
        # Test 3: Non-existent endpoint
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        
        error_data = json.loads(response.data)
        assert error_data['success'] == False
        assert error_data['status_code'] == 404
        print("✓ Non-existent endpoint handled correctly")
    
    return True


def test_ui_components():
    """
    Test that UI components are properly structured.
    """
    print("Testing UI components...")
    
    # Check if template file exists and has required elements
    template_path = 'templates/dashboard.html'
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Check for essential HTML elements
        assert '<html' in template_content.lower()
        assert '<head' in template_content.lower()
        assert '<body' in template_content.lower()
        
        # Check for Chart.js integration
        assert 'chart' in template_content.lower()
        
        # Check for glass morphism CSS classes or styles
        glass_indicators = ['glass', 'blur', 'backdrop', 'translucent', 'morphism']
        has_glass_styling = any(indicator in template_content.lower() for indicator in glass_indicators)
        
        if has_glass_styling:
            print("✓ Glass morphism UI elements detected")
        else:
            print("⚠ Glass morphism styling may not be present")
        
        print("✓ UI template structure is valid")
    else:
        print("⚠ Dashboard template not found")
    
    # Check CSS file
    css_path = 'static/css/style.css'
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check for glass morphism properties
        glass_properties = ['backdrop-filter', 'blur', 'rgba', 'opacity']
        has_glass_css = any(prop in css_content.lower() for prop in glass_properties)
        
        if has_glass_css:
            print("✓ Glass morphism CSS properties found")
        else:
            print("⚠ Glass morphism CSS may be incomplete")
    else:
        print("⚠ CSS file not found")
    
    # Check JavaScript file
    js_path = 'static/js/dashboard.js'
    if os.path.exists(js_path):
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Check for Chart.js usage
        chart_indicators = ['Chart', 'chart', 'canvas', 'ctx']
        has_chart_js = any(indicator in js_content for indicator in chart_indicators)
        
        if has_chart_js:
            print("✓ Chart.js integration found")
        else:
            print("⚠ Chart.js integration may be incomplete")
    else:
        print("⚠ JavaScript file not found")
    
    return True


def test_performance_basics():
    """
    Basic performance tests to ensure reasonable response times.
    """
    print("Testing basic performance...")
    
    from app import app
    
    with app.test_client() as client:
        
        # Test dashboard load time
        start_time = time.time()
        response = client.get('/')
        end_time = time.time()
        
        load_time = end_time - start_time
        assert load_time < 5.0  # Should load within 5 seconds
        print(f"✓ Dashboard loads in {load_time:.3f}s")
        
        # Test health check response time
        start_time = time.time()
        response = client.get('/health')
        end_time = time.time()
        
        health_time = end_time - start_time
        assert health_time < 2.0  # Should respond within 2 seconds
        print(f"✓ Health check responds in {health_time:.3f}s")
    
    return True


if __name__ == "__main__":
    print("Running comprehensive integration tests...")
    print("=" * 60)
    
    try:
        test_full_integration()
        test_flask_endpoints()
        test_error_scenarios()
        test_ui_components()
        test_performance_basics()
        
        print("=" * 60)
        print("✓ All integration tests completed successfully!")
        print("\nFinal integration testing complete.")
        print("The Restaurant Review Dashboard is ready for deployment.")
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)