"""
Simple Flask test
"""

import sys
sys.path.insert(0, '.')

def test_flask_import():
    """Test that Flask app can be imported"""
    print("Testing Flask app import...")
    
    try:
        from app import app
        print("✓ Flask app imported successfully")
        
        # Test that app is configured
        assert app is not None
        print("✓ Flask app is configured")
        
        # Test routes are registered
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        expected_routes = ['/', '/api/reviews', '/api/metrics', '/api/sentiment']
        
        for route in expected_routes:
            assert route in routes, f"Route {route} not found"
            print(f"✓ Route {route} is registered")
        
        print("All Flask import tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Flask import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_flask_import()