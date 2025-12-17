"""
Test Flask API endpoints
"""

import sys
sys.path.insert(0, '.')

import os
from unittest.mock import patch, Mock
from app import app

def test_flask_endpoints():
    """Test Flask API endpoints"""
    print("Testing Flask API endpoints...")
    
    # Create test client
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Test main dashboard route
    print("Testing dashboard route...")
    response = client.get('/')
    assert response.status_code == 200
    print("✓ Dashboard route works")
    
    # Mock environment variables for API tests
    with patch.dict(os.environ, {'SERPAPI_KEY': 'test_key', 'PLACE_ID': 'test_place'}):
        
        # Mock SerpAPI response
        mock_response_data = {
            'reviews': [
                {
                    'review_id': 'review_1',
                    'rating': 4.5,
                    'review': 'Great food and excellent service!',
                    'date': '2023-01-15',
                    'reviewer_name': 'John Doe',
                    'helpful_votes': 5
                },
                {
                    'review_id': 'review_2',
                    'rating': 3.0,
                    'review': 'Average meal, slow service.',
                    'date': '2023-01-20',
                    'reviewer_name': 'Jane Smith',
                    'helpful_votes': 2
                }
            ],
            'search_metadata': {'total_results': 2},
            'place_info': {'name': 'Test Restaurant'},
            'serpapi_pagination': {}
        }
        
        with patch('services.serpapi_client.requests.Session') as mock_session_class:
            # Setup mock session
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            # Setup mock response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_session.get.return_value = mock_response
            
            # Test reviews endpoint
            print("Testing /api/reviews endpoint...")
            response = client.get('/api/reviews?num=2')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] == True
            assert 'data' in data
            print("✓ Reviews endpoint works")
            
            # Test metrics endpoint
            print("Testing /api/metrics endpoint...")
            response = client.get('/api/metrics?num=2&interval=monthly')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] == True
            assert 'data' in data
            assert 'overall_metrics' in data['data']
            assert 'rating_trends' in data['data']
            assert 'volume_data' in data['data']
            assert 'themes' in data['data']
            print("✓ Metrics endpoint works")
            
            # Test sentiment endpoint
            print("Testing /api/sentiment endpoint...")
            response = client.get('/api/sentiment?num=2')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] == True
            assert 'data' in data
            assert 'sentiment_distribution' in data['data']
            assert 'sentiment_percentages' in data['data']
            print("✓ Sentiment endpoint works")
    
    # Test error handling
    print("Testing error handling...")
    
    # Test invalid parameters
    response = client.get('/api/reviews?start=-1')
    assert response.status_code == 400
    print("✓ Invalid parameter handling works")
    
    response = client.get('/api/metrics?interval=invalid')
    assert response.status_code == 400
    print("✓ Invalid interval handling works")
    
    print("All Flask endpoint tests passed!")
    return True

if __name__ == "__main__":
    test_flask_endpoints()