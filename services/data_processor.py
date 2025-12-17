"""
Data Processing and Aggregation Services

This module provides data transformation, aggregation, and analysis functions
for restaurant review data from the SerpAPI OpenTable Reviews endpoint.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re
from statistics import mean, median

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Service class for processing and aggregating restaurant review data.
    
    Handles data transformation, rating aggregation, volume calculations,
    and theme extraction from review content.
    """
    
    def __init__(self):
        """Initialize the data processor."""
        self.common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'was', 'are', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i',
            'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
    
    def transform_review_data(self, raw_reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform raw API review data to standardized internal format.
        
        Args:
            raw_reviews: List of raw review dictionaries from SerpAPI
            
        Returns:
            List of transformed review dictionaries with standardized fields
        """
        transformed_reviews = []
        
        for review in raw_reviews:
            try:
                transformed = self._transform_single_review(review)
                if transformed:
                    transformed_reviews.append(transformed)
            except Exception as e:
                logger.warning(f"Failed to transform review: {e}")
                continue
        
        logger.info(f"Transformed {len(transformed_reviews)} reviews from {len(raw_reviews)} raw reviews")
        return transformed_reviews
    
    def _transform_single_review(self, review: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Transform a single review to internal format.
        
        Args:
            review: Raw review dictionary
            
        Returns:
            Transformed review dictionary or None if invalid
        """
        # Extract and validate rating
        rating = review.get('rating')
        if rating is not None:
            try:
                rating = float(rating)
                if not (1 <= rating <= 5):
                    logger.warning(f"Invalid rating {rating}, skipping review")
                    return None
            except (ValueError, TypeError):
                logger.warning(f"Could not parse rating {rating}, skipping review")
                return None
        
        # Extract and clean review text
        review_text = review.get('review_text', '') or review.get('review', '') or ''
        if isinstance(review_text, str):
            review_text = review_text.strip()
        else:
            review_text = str(review_text).strip() if review_text else ''
        
        # Parse and normalize date
        date_str = review.get('date')
        parsed_date = self._parse_date(date_str)
        
        # Build transformed review
        transformed = {
            'review_id': review.get('review_id', f"review_{hash(str(review))}"),
            'rating': rating,
            'review_text': review_text,
            'date': parsed_date,
            'date_string': date_str,
            'reviewer_name': review.get('reviewer_name', 'Anonymous'),
            'helpful_votes': self._safe_int(review.get('helpful_votes', 0)),
            'word_count': len(review_text.split()) if review_text else 0,
            'character_count': len(review_text) if review_text else 0
        }
        
        return transformed
    
    def _parse_date(self, date_str: Any) -> Optional[datetime]:
        """
        Parse date string to datetime object.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Parsed datetime object or None if parsing fails
        """
        if not date_str:
            return None
        
        # Common date formats to try
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%B %d, %Y',
            '%b %d, %Y'
        ]
        
        date_str = str(date_str).strip()
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def _safe_int(self, value: Any, default: int = 0) -> int:
        """
        Safely convert value to integer.
        
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
    
    def aggregate_ratings_by_time(self, reviews: List[Dict[str, Any]], 
                                 interval: str = 'monthly') -> List[Dict[str, Any]]:
        """
        Aggregate ratings by time intervals.
        
        Args:
            reviews: List of transformed review dictionaries
            interval: Time interval ('daily', 'weekly', 'monthly')
            
        Returns:
            List of time-aggregated rating data
        """
        if not reviews:
            return []
        
        # Group reviews by time interval
        time_groups = defaultdict(list)
        
        for review in reviews:
            if not review.get('date') or review.get('rating') is None:
                continue
            
            time_key = self._get_time_key(review['date'], interval)
            if time_key:
                time_groups[time_key].append(review)
        
        # Calculate aggregated metrics for each time period
        aggregated_data = []
        for time_key in sorted(time_groups.keys()):
            group_reviews = time_groups[time_key]
            ratings = [r['rating'] for r in group_reviews if r['rating'] is not None]
            
            if ratings:
                aggregated_data.append({
                    'date': time_key,
                    'average_rating': round(mean(ratings), 2),
                    'median_rating': round(median(ratings), 2),
                    'review_count': len(group_reviews),
                    'rating_distribution': self._calculate_rating_distribution(ratings),
                    'total_helpful_votes': sum(r.get('helpful_votes', 0) for r in group_reviews)
                })
        
        logger.info(f"Aggregated {len(reviews)} reviews into {len(aggregated_data)} time periods ({interval})")
        return aggregated_data
    
    def _get_time_key(self, date: datetime, interval: str) -> Optional[str]:
        """
        Get time key for grouping based on interval.
        
        Args:
            date: Datetime object
            interval: Time interval type
            
        Returns:
            Time key string or None
        """
        if not date:
            return None
        
        if interval == 'daily':
            return date.strftime('%Y-%m-%d')
        elif interval == 'weekly':
            # Get Monday of the week
            monday = date - timedelta(days=date.weekday())
            return monday.strftime('%Y-%m-%d')
        elif interval == 'monthly':
            return date.strftime('%Y-%m')
        else:
            logger.warning(f"Unknown interval: {interval}")
            return None
    
    def _calculate_rating_distribution(self, ratings: List[float]) -> Dict[str, int]:
        """
        Calculate distribution of ratings.
        
        Args:
            ratings: List of rating values
            
        Returns:
            Dictionary with rating distribution counts
        """
        distribution = {'1_star': 0, '2_star': 0, '3_star': 0, '4_star': 0, '5_star': 0}
        
        for rating in ratings:
            if 1 <= rating < 2:
                distribution['1_star'] += 1
            elif 2 <= rating < 3:
                distribution['2_star'] += 1
            elif 3 <= rating < 4:
                distribution['3_star'] += 1
            elif 4 <= rating < 5:
                distribution['4_star'] += 1
            elif rating == 5:
                distribution['5_star'] += 1
        
        return distribution
    
    def calculate_review_volume(self, reviews: List[Dict[str, Any]], 
                               interval: str = 'monthly') -> List[Dict[str, Any]]:
        """
        Calculate review volume over time periods.
        
        Args:
            reviews: List of transformed review dictionaries
            interval: Time interval ('daily', 'weekly', 'monthly')
            
        Returns:
            List of volume data by time period
        """
        if not reviews:
            return []
        
        # Group reviews by time interval
        time_groups = defaultdict(int)
        
        for review in reviews:
            if not review.get('date'):
                continue
            
            time_key = self._get_time_key(review['date'], interval)
            if time_key:
                time_groups[time_key] += 1
        
        # Build volume data
        volume_data = []
        for time_key in sorted(time_groups.keys()):
            volume_data.append({
                'date': time_key,
                'review_count': time_groups[time_key],
                'interval': interval
            })
        
        logger.info(f"Calculated review volume for {len(volume_data)} time periods ({interval})")
        return volume_data
    
    def extract_themes(self, reviews: List[Dict[str, Any]], 
                      max_themes: int = 10) -> List[Dict[str, Any]]:
        """
        Extract common themes from review text content.
        
        Args:
            reviews: List of transformed review dictionaries
            max_themes: Maximum number of themes to return
            
        Returns:
            List of theme dictionaries with frequency counts
        """
        if not reviews:
            return []
        
        # Collect all review text
        all_text = []
        for review in reviews:
            text = review.get('review_text', '')
            if text and len(text.strip()) > 0:
                all_text.append(text.lower())
        
        if not all_text:
            return []
        
        # Extract keywords and phrases
        word_counts = Counter()
        phrase_counts = Counter()
        
        for text in all_text:
            # Clean and tokenize text
            words = self._extract_words(text)
            phrases = self._extract_phrases(text)
            
            # Count significant words (not common words)
            for word in words:
                if len(word) > 2 and word not in self.common_words:
                    word_counts[word] += 1
            
            # Count phrases
            for phrase in phrases:
                phrase_counts[phrase] += 1
        
        # Combine and rank themes
        themes = []
        
        # Add top words as themes
        for word, count in word_counts.most_common(max_themes // 2):
            if count >= 2:  # Only include words that appear multiple times
                themes.append({
                    'theme': word,
                    'type': 'keyword',
                    'frequency': count,
                    'percentage': round((count / len(all_text)) * 100, 1)
                })
        
        # Add top phrases as themes
        for phrase, count in phrase_counts.most_common(max_themes // 2):
            if count >= 2:  # Only include phrases that appear multiple times
                themes.append({
                    'theme': phrase,
                    'type': 'phrase',
                    'frequency': count,
                    'percentage': round((count / len(all_text)) * 100, 1)
                })
        
        # Sort by frequency and limit results
        themes.sort(key=lambda x: x['frequency'], reverse=True)
        themes = themes[:max_themes]
        
        logger.info(f"Extracted {len(themes)} themes from {len(all_text)} reviews")
        return themes
    
    def _extract_words(self, text: str) -> List[str]:
        """
        Extract individual words from text.
        
        Args:
            text: Review text
            
        Returns:
            List of cleaned words
        """
        # Remove punctuation and split into words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return [word for word in words if len(word) > 2]
    
    def _extract_phrases(self, text: str) -> List[str]:
        """
        Extract meaningful phrases from text.
        
        Args:
            text: Review text
            
        Returns:
            List of phrases
        """
        phrases = []
        
        # Look for common restaurant-related phrases
        phrase_patterns = [
            r'\b(great|good|excellent|amazing|wonderful|fantastic|delicious|tasty)\s+\w+\b',
            r'\b(bad|terrible|awful|horrible|disgusting|poor)\s+\w+\b',
            r'\b(friendly|rude|helpful|slow|fast|quick)\s+(service|staff|server|waiter|waitress)\b',
            r'\b(fresh|stale|hot|cold|warm|spicy|bland)\s+(food|meal|dish)\b'
        ]
        
        for pattern in phrase_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                if isinstance(match, tuple):
                    phrase = ' '.join(match)
                else:
                    phrase = match
                if len(phrase) > 3:
                    phrases.append(phrase)
        
        return phrases
    
    def calculate_overall_metrics(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall metrics for all reviews.
        
        Args:
            reviews: List of transformed review dictionaries
            
        Returns:
            Dictionary with overall metrics
        """
        if not reviews:
            return {
                'total_reviews': 0,
                'average_rating': 0,
                'median_rating': 0,
                'rating_distribution': {'1_star': 0, '2_star': 0, '3_star': 0, '4_star': 0, '5_star': 0},
                'total_helpful_votes': 0,
                'average_word_count': 0,
                'date_range': None
            }
        
        # Extract valid ratings
        ratings = [r['rating'] for r in reviews if r.get('rating') is not None]
        
        # Extract dates for range calculation
        dates = [r['date'] for r in reviews if r.get('date') is not None]
        
        # Calculate metrics
        metrics = {
            'total_reviews': len(reviews),
            'average_rating': round(mean(ratings), 2) if ratings else 0,
            'median_rating': round(median(ratings), 2) if ratings else 0,
            'rating_distribution': self._calculate_rating_distribution(ratings),
            'total_helpful_votes': sum(r.get('helpful_votes', 0) for r in reviews),
            'average_word_count': round(mean([r.get('word_count', 0) for r in reviews]), 1),
            'date_range': {
                'earliest': min(dates).isoformat() if dates else None,
                'latest': max(dates).isoformat() if dates else None
            } if dates else None
        }
        
        logger.info(f"Calculated overall metrics for {len(reviews)} reviews")
        return metrics