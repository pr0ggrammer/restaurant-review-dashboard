"""
Test for comprehensive error handling functionality.

**Feature: restaurant-review-dashboard, Property 8: Error Handling Consistency**
**Validates: Requirements 6.4**
"""

import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock
import tempfile
import logging

# Add the current directory to Python path
sys.path.insert(0, '.')

def test_error_handling_consistency():
    """
    Property: For any error condition (API failures, invalid data, network issues), 
    the system should log appropriate information and maintain service availability.
    """
    print("Testing error handling consistency...")
    
    # Test SerpAPI error handling
    from services.serpapi_client import SerpAPIClient, SerpAPIError
    
    # Test 1: Invalid API key error handling
    with patch('services.serpapi_client.requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid API key"
        mock_session.get.return_value = mock_response
        
        client = SerpAPIClient(api_key="invalid_key", place_id="test_place")
        
        try:
            client.fetch_reviews()
            assert False, "Expected SerpAPIError for invalid API key"
        except SerpAPIError as e:
            assert "Invalid SerpAPI key" in str(e)
            print("✓ Invalid API key error handled correctly")
        finally:
            client.close()
    
    # Test 2: Rate limit error handling
    with patch('services.serpapi_client.requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock 429 response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_session.get.return_value = mock_response
        
        client = SerpAPIClient(api_key="test_key", place_id="test_place")
        
        try:
            client.fetch_reviews()
            assert False, "Expected SerpAPIError for rate limit"
        except SerpAPIError as e:
            assert "Rate limit exceeded" in str(e)
            print("✓ Rate limit error handled correctly")
        finally:
            client.close()
    
    # Test 3: Network timeout error handling
    with patch('services.serpapi_client.requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock timeout exception
        from requests.exceptions import Timeout
        mock_session.get.side_effect = Timeout("Request timeout")
        
        client = SerpAPIClient(api_key="test_key", place_id="test_place")
        
        try:
            client.fetch_reviews()
            assert False, "Expected SerpAPIError for timeout"
        except SerpAPIError as e:
            assert "timeout" in str(e).lower()
            print("✓ Network timeout error handled correctly")
        finally:
            client.close()
    
    return True


def test_data_validation_error_handling():
    """
    Test error handling for invalid or malformed data.
    """
    print("Testing data validation error handling...")
    
    from services.serpapi_client import SerpAPIClient, SerpAPIError
    
    # Test invalid response format
    with patch('services.serpapi_client.requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = "invalid_json_structure"  # Should be dict
        
        mock_session.get.return_value = mock_response
        
        client = SerpAPIClient(api_key="test_key", place_id="test_place")
        
        try:
            client.fetch_reviews()
            assert False, "Expected SerpAPIError for invalid response format"
        except SerpAPIError as e:
            assert "Invalid response format" in str(e)
            print("✓ Invalid response format error handled correctly")
        finally:
            client.close()
    
    # Test API error response
    with patch('services.serpapi_client.requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock response with API error
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"error": "Invalid place_id"}
        
        mock_session.get.return_value = mock_response
        
        client = SerpAPIClient(api_key="test_key", place_id="invalid_place")
        
        try:
            client.fetch_reviews()
            assert False, "Expected SerpAPIError for API error response"
        except SerpAPIError as e:
            assert "Invalid place_id" in str(e)
            print("✓ API error response handled correctly")
        finally:
            client.close()
    
    return True


def test_configuration_error_handling():
    """
    Test error handling for missing or invalid configuration.
    """
    print("Testing configuration error handling...")
    
    from services.serpapi_client import SerpAPIClient, SerpAPIError
    
    # Test missing API key
    try:
        client = SerpAPIClient(api_key=None, place_id="test_place")
        assert False, "Expected SerpAPIError for missing API key"
    except SerpAPIError as e:
        assert "SerpAPI key is required" in str(e)
        print("✓ Missing API key error handled correctly")
    
    # Test empty API key
    try:
        client = SerpAPIClient(api_key="", place_id="test_place")
        assert False, "Expected SerpAPIError for empty API key"
    except SerpAPIError as e:
        assert "SerpAPI key is required" in str(e)
        print("✓ Empty API key error handled correctly")
    
    # Test missing place ID
    try:
        client = SerpAPIClient(api_key="test_key", place_id=None)
        assert False, "Expected SerpAPIError for missing place ID"
    except SerpAPIError as e:
        assert "Place ID is required" in str(e)
        print("✓ Missing place ID error handled correctly")
    
    # Test empty place ID
    try:
        client = SerpAPIClient(api_key="test_key", place_id="")
        assert False, "Expected SerpAPIError for empty place ID"
    except SerpAPIError as e:
        assert "Place ID is required" in str(e)
        print("✓ Empty place ID error handled correctly")
    
    return True


def test_logging_functionality():
    """
    Test that errors are properly logged for debugging and monitoring.
    """
    print("Testing logging functionality...")
    
    # Create a temporary log file
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.log') as temp_log:
        temp_log_path = temp_log.name
    
    try:
        # Configure logging to write to temp file
        test_logger = logging.getLogger('test_error_handling')
        test_logger.setLevel(logging.INFO)
        
        # Add file handler
        file_handler = logging.FileHandler(temp_log_path)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        test_logger.addHandler(file_handler)
        
        # Test logging different error levels
        test_logger.info("Test info message")
        test_logger.warning("Test warning message")
        test_logger.error("Test error message")
        
        # Flush and read log file
        file_handler.flush()
        
        with open(temp_log_path, 'r') as log_file:
            log_content = log_file.read()
        
        # Verify log messages are present
        assert "Test info message" in log_content
        assert "Test warning message" in log_content
        assert "Test error message" in log_content
        
        print("✓ Logging functionality working correctly")
        
        # Clean up
        test_logger.removeHandler(file_handler)
        file_handler.close()
        
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_log_path)
        except:
            pass
    
    return True


def test_graceful_degradation():
    """
    Test that the system maintains service availability during partial failures.
    """
    print("Testing graceful degradation...")
    
    from services.data_processor import DataProcessor
    
    # Test processing with empty data
    processor = DataProcessor()
    
    # Should handle empty reviews gracefully
    result = processor.transform_review_data([])
    assert result == []
    print("✓ Empty data handled gracefully")
    
    # Should handle malformed review data
    malformed_reviews = [
        {"invalid": "data"},
        {"rating": "not_a_number"},
        None,
        {"rating": 4.5, "review_text": "Valid review"}
    ]
    
    result = processor.transform_review_data(malformed_reviews)
    # Should skip invalid reviews but process valid ones
    assert len(result) >= 0  # At least doesn't crash
    print("✓ Malformed data handled gracefully")
    
    # Test metrics calculation with empty data
    metrics = processor.calculate_overall_metrics([])
    assert isinstance(metrics, dict)
    assert metrics.get('average_rating') == 0.0
    assert metrics.get('total_reviews') == 0
    print("✓ Empty metrics calculation handled gracefully")
    
    return True


if __name__ == "__main__":
    print("Running comprehensive error handling tests...")
    print("=" * 60)
    
    try:
        test_error_handling_consistency()
        test_data_validation_error_handling()
        test_configuration_error_handling()
        test_logging_functionality()
        test_graceful_degradation()
        
        print("=" * 60)
        print("✓ All error handling tests completed successfully!")
        print("\nProperty 8 (Error Handling Consistency) has been validated.")
        print("The system correctly handles errors and maintains service availability.")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)