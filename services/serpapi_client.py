"""
SerpAPI OpenTable Reviews Integration Service

This module provides the SerpAPIClient class for integrating with the SerpAPI 
OpenTable Reviews endpoint to fetch restaurant review data.
"""

import requests
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SerpAPIError(Exception):
    """Custom exception for SerpAPI related errors"""
    pass


class SerpAPIClient:
    """
    Client class for SerpAPI OpenTable Reviews endpoint integration.
    
    Handles authentication, request management, error handling, and data validation
    for OpenTable review data retrieval.
    """
    
    BASE_URL = "https://serpapi.com/search.json"
    ENGINE = "open_table_reviews"
    
    def __init__(self, api_key: Optional[str] = None, place_id: Optional[str] = None):
        """
        Initialize SerpAPI client with authentication and configuration.
        
        Args:
            api_key: SerpAPI authentication key (defaults to SERPAPI_KEY env var)
            place_id: OpenTable place identifier (defaults to PLACE_ID env var)
        """
        self.api_key = api_key if api_key is not None else os.getenv('SERPAPI_KEY')
        self.place_id = place_id if place_id is not None else os.getenv('PLACE_ID')
        
        if not self.api_key or self.api_key.strip() == '':
            raise SerpAPIError("SerpAPI key is required. Set SERPAPI_KEY environment variable or pass api_key parameter.")
        
        if not self.place_id or self.place_id.strip() == '':
            raise SerpAPIError("Place ID is required. Set PLACE_ID environment variable or pass place_id parameter.")
        
        # Request session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Restaurant-Review-Dashboard/1.0'
        })
        
        logger.info(f"SerpAPI client initialized for place_id: {self.place_id}")
    
    def fetch_reviews(self, start: int = 0, num_reviews: int = 100) -> Dict[str, Any]:
        """
        Fetch restaurant reviews from SerpAPI OpenTable Reviews endpoint.
        
        Args:
            start: Starting position for pagination (default: 0)
            num_reviews: Number of reviews to fetch (default: 100)
            
        Returns:
            Dict containing validated review data and metadata
            
        Raises:
            SerpAPIError: For API-related errors (authentication, rate limits, etc.)
            requests.RequestException: For network-related errors
        """
        params = {
            'engine': self.ENGINE,
            'api_key': self.api_key,
            'place_id': self.place_id,
            'start': start,
            'num': num_reviews
        }
        
        try:
            logger.info(f"Fetching reviews from SerpAPI (start={start}, num={num_reviews})")
            
            response = self._make_request(params)
            validated_data = self._validate_response(response)
            
            logger.info(f"Successfully fetched {len(validated_data.get('reviews', []))} reviews")
            return validated_data
            
        except requests.exceptions.Timeout:
            raise SerpAPIError("Request timeout while fetching reviews from SerpAPI")
        except requests.exceptions.ConnectionError:
            raise SerpAPIError("Connection error while accessing SerpAPI")
        except requests.exceptions.RequestException as e:
            raise SerpAPIError(f"Network error during SerpAPI request: {str(e)}")
    
    def _make_request(self, params: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """
        Make HTTP request to SerpAPI with retry logic and error handling.
        
        Args:
            params: Request parameters
            max_retries: Maximum number of retry attempts
            
        Returns:
            JSON response data
            
        Raises:
            SerpAPIError: For API errors or exceeded retry attempts
        """
        for attempt in range(max_retries + 1):
            try:
                response = self.session.get(
                    self.BASE_URL,
                    params=params,
                    timeout=30
                )
                
                # Handle HTTP status codes
                if response.status_code == 401:
                    raise SerpAPIError("Invalid SerpAPI key. Please check your authentication credentials.")
                elif response.status_code == 429:
                    if attempt < max_retries:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"Rate limit hit. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise SerpAPIError("Rate limit exceeded. Please try again later.")
                elif response.status_code >= 400:
                    raise SerpAPIError(f"SerpAPI request failed with status {response.status_code}: {response.text}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request failed (attempt {attempt + 1}). Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise
        
        raise SerpAPIError(f"Failed to complete request after {max_retries + 1} attempts")
    
    def _validate_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize SerpAPI response data.
        
        Args:
            response_data: Raw JSON response from SerpAPI
            
        Returns:
            Validated and normalized data structure
            
        Raises:
            SerpAPIError: For invalid or malformed response data
        """
        if not isinstance(response_data, dict):
            raise SerpAPIError("Invalid response format: expected JSON object")
        
        # Check for API errors in response
        if 'error' in response_data:
            error_msg = response_data.get('error', 'Unknown API error')
            raise SerpAPIError(f"SerpAPI returned error: {error_msg}")
        
        # Validate required fields
        reviews = response_data.get('reviews', [])
        if not isinstance(reviews, list):
            raise SerpAPIError("Invalid response format: 'reviews' field must be a list")
        
        # Validate and normalize individual reviews
        validated_reviews = []
        for i, review in enumerate(reviews):
            try:
                validated_review = self._validate_review(review)
                validated_reviews.append(validated_review)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid review at index {i}: {str(e)}")
                continue
        
        # Extract metadata
        metadata = {
            'total_results': response_data.get('search_metadata', {}).get('total_results', len(validated_reviews)),
            'place_id': self.place_id,
            'fetched_at': datetime.utcnow().isoformat(),
            'search_parameters': response_data.get('search_parameters', {})
        }
        
        return {
            'reviews': validated_reviews,
            'metadata': metadata,
            'place_info': response_data.get('place_info', {}),
            'pagination': response_data.get('serpapi_pagination', {})
        }
    
    def _validate_review(self, review: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize individual review data.
        
        Args:
            review: Raw review data from API response
            
        Returns:
            Validated and normalized review structure
            
        Raises:
            ValueError: For invalid review data
        """
        if not isinstance(review, dict):
            raise ValueError("Review must be a dictionary")
        
        # Extract and validate required fields
        rating = review.get('rating')
        if rating is not None:
            try:
                rating = float(rating)
                if not (1 <= rating <= 5):
                    raise ValueError(f"Rating must be between 1 and 5, got {rating}")
            except (ValueError, TypeError):
                raise ValueError(f"Invalid rating format: {rating}")
        
        # Extract review text (may be empty)
        review_text = review.get('review', '') or review.get('text', '') or ''
        if not isinstance(review_text, str):
            review_text = str(review_text) if review_text is not None else ''
        
        # Extract date and normalize format
        date_str = review.get('date') or review.get('review_date')
        normalized_date = None
        if date_str:
            try:
                # Try to parse and normalize date format
                # SerpAPI may return various date formats
                if isinstance(date_str, str):
                    normalized_date = date_str
                else:
                    normalized_date = str(date_str)
            except Exception:
                logger.warning(f"Could not parse date: {date_str}")
        
        # Build normalized review structure
        normalized_review = {
            'review_id': review.get('review_id') or review.get('id') or f"review_{hash(str(review))}",
            'rating': rating,
            'review_text': review_text.strip(),
            'date': normalized_date,
            'reviewer_name': review.get('reviewer_name') or review.get('author') or 'Anonymous',
            'helpful_votes': self._safe_int(review.get('helpful_votes') or review.get('helpful', 0)),
            'raw_data': review  # Keep original data for debugging
        }
        
        return normalized_review
    
    def _safe_int(self, value: Any, default: int = 0) -> int:
        """
        Safely convert value to integer with fallback.
        
        Args:
            value: Value to convert
            default: Default value if conversion fails
            
        Returns:
            Integer value or default
        """
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    def get_place_info(self) -> Dict[str, Any]:
        """
        Get basic place information without reviews.
        
        Returns:
            Place information and metadata
        """
        try:
            response = self.fetch_reviews(start=0, num_reviews=1)
            return {
                'place_info': response.get('place_info', {}),
                'place_id': self.place_id,
                'metadata': response.get('metadata', {})
            }
        except SerpAPIError:
            # Return minimal info if API call fails
            return {
                'place_info': {},
                'place_id': self.place_id,
                'metadata': {'error': 'Could not fetch place information'}
            }
    
    def close(self):
        """Close the HTTP session."""
        if hasattr(self, 'session'):
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()