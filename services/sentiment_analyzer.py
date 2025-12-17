"""
Sentiment Analysis Service

This module provides sentiment analysis functionality for restaurant review text,
classifying reviews as positive, negative, or neutral with confidence scores.
"""

import logging
import re
from typing import Dict, List, Any, Tuple
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Service class for analyzing sentiment in restaurant review text.
    
    Uses lexicon-based approach with restaurant-specific keywords and patterns
    to classify sentiment as positive, negative, or neutral.
    """
    
    def __init__(self):
        """Initialize the sentiment analyzer with keyword lexicons."""
        
        # Positive sentiment keywords
        self.positive_words = {
            'excellent', 'amazing', 'fantastic', 'wonderful', 'great', 'good', 'delicious',
            'tasty', 'fresh', 'hot', 'perfect', 'outstanding', 'superb', 'brilliant',
            'lovely', 'beautiful', 'friendly', 'helpful', 'quick', 'fast', 'efficient',
            'clean', 'cozy', 'comfortable', 'relaxing', 'enjoyable', 'pleasant',
            'recommend', 'love', 'loved', 'favorite', 'best', 'top', 'quality',
            'value', 'worth', 'satisfied', 'happy', 'pleased', 'impressed'
        }
        
        # Negative sentiment keywords
        self.negative_words = {
            'terrible', 'awful', 'horrible', 'disgusting', 'bad', 'poor', 'worst',
            'hate', 'hated', 'disappointing', 'disappointed', 'bland', 'tasteless',
            'cold', 'stale', 'overpriced', 'expensive', 'slow', 'rude', 'unfriendly',
            'dirty', 'messy', 'noisy', 'crowded', 'uncomfortable', 'unpleasant',
            'avoid', 'never', 'waste', 'money', 'time', 'regret', 'sorry',
            'complain', 'complaint', 'problem', 'issue', 'wrong', 'mistake'
        }
        
        # Intensifiers that modify sentiment strength
        self.intensifiers = {
            'very': 1.5, 'extremely': 2.0, 'incredibly': 2.0, 'absolutely': 1.8,
            'really': 1.3, 'quite': 1.2, 'pretty': 1.1, 'somewhat': 0.8,
            'rather': 0.9, 'fairly': 0.9, 'totally': 1.7, 'completely': 1.8
        }
        
        # Negation words that flip sentiment
        self.negations = {
            'not', 'no', 'never', 'nothing', 'nobody', 'nowhere', 'neither',
            'nor', 'none', 'hardly', 'scarcely', 'barely', 'seldom', 'rarely'
        }
        
        # Restaurant-specific positive phrases
        self.positive_phrases = [
            r'\b(highly recommend|would recommend|will return|come back|worth it)\b',
            r'\b(great (food|service|experience|place|restaurant))\b',
            r'\b(excellent (food|service|experience|meal|dish))\b',
            r'\b(amazing (food|service|experience|meal|taste))\b',
            r'\b(love this place|favorite restaurant|best (food|service|meal))\b'
        ]
        
        # Restaurant-specific negative phrases
        self.negative_phrases = [
            r'\b(would not recommend|will not return|never again|avoid this place)\b',
            r'\b(terrible (food|service|experience|meal))\b',
            r'\b(awful (food|service|experience|meal))\b',
            r'\b(worst (food|service|experience|meal|restaurant))\b',
            r'\b(waste of (money|time)|not worth it|overpriced)\b'
        ]
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of review text.
        
        Args:
            text: Review text to analyze
            
        Returns:
            Dictionary containing sentiment classification and confidence
        """
        if not text or not isinstance(text, str):
            return self._create_neutral_result("Empty or invalid text")
        
        text = text.strip().lower()
        if len(text) < 3:
            return self._create_neutral_result("Text too short for analysis")
        
        # Calculate sentiment scores
        positive_score = self._calculate_positive_score(text)
        negative_score = self._calculate_negative_score(text)
        
        # Determine overall sentiment
        sentiment, confidence = self._classify_sentiment(positive_score, negative_score)
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_score': round(positive_score, 3),
            'negative_score': round(negative_score, 3),
            'text_length': len(text),
            'analysis_method': 'lexicon_based'
        }
    
    def _calculate_positive_score(self, text: str) -> float:
        """
        Calculate positive sentiment score for text.
        
        Args:
            text: Preprocessed review text
            
        Returns:
            Positive sentiment score
        """
        score = 0.0
        words = self._tokenize_text(text)
        
        # Check for positive phrases first (higher weight)
        for pattern in self.positive_phrases:
            matches = len(re.findall(pattern, text))
            score += matches * 2.0
        
        # Analyze individual words with context
        for i, word in enumerate(words):
            if word in self.positive_words:
                word_score = 1.0
                
                # Check for intensifiers before the word
                if i > 0 and words[i-1] in self.intensifiers:
                    word_score *= self.intensifiers[words[i-1]]
                
                # Check for negations (within 3 words before)
                negated = False
                for j in range(max(0, i-3), i):
                    if words[j] in self.negations:
                        negated = True
                        break
                
                if negated:
                    word_score *= -0.5  # Negated positive becomes slightly negative
                
                score += word_score
        
        return score
    
    def _calculate_negative_score(self, text: str) -> float:
        """
        Calculate negative sentiment score for text.
        
        Args:
            text: Preprocessed review text
            
        Returns:
            Negative sentiment score
        """
        score = 0.0
        words = self._tokenize_text(text)
        
        # Check for negative phrases first (higher weight)
        for pattern in self.negative_phrases:
            matches = len(re.findall(pattern, text))
            score += matches * 2.0
        
        # Analyze individual words with context
        for i, word in enumerate(words):
            if word in self.negative_words:
                word_score = 1.0
                
                # Check for intensifiers before the word
                if i > 0 and words[i-1] in self.intensifiers:
                    word_score *= self.intensifiers[words[i-1]]
                
                # Check for negations (within 3 words before)
                negated = False
                for j in range(max(0, i-3), i):
                    if words[j] in self.negations:
                        negated = True
                        break
                
                if negated:
                    word_score *= -0.5  # Negated negative becomes slightly positive
                
                score += word_score
        
        return score
    
    def _tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of words
        """
        # Remove punctuation and split into words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return words
    
    def _classify_sentiment(self, positive_score: float, negative_score: float) -> Tuple[str, float]:
        """
        Classify sentiment based on positive and negative scores.
        
        Args:
            positive_score: Calculated positive sentiment score
            negative_score: Calculated negative sentiment score
            
        Returns:
            Tuple of (sentiment_label, confidence_score)
        """
        # Calculate net sentiment
        net_sentiment = positive_score - negative_score
        total_sentiment = positive_score + negative_score
        
        # Determine thresholds
        strong_threshold = 2.0
        weak_threshold = 0.5
        
        # Classify sentiment
        if abs(net_sentiment) < weak_threshold:
            sentiment = 'neutral'
            confidence = 1.0 - (abs(net_sentiment) / weak_threshold) * 0.3
        elif net_sentiment > 0:
            sentiment = 'positive'
            if net_sentiment >= strong_threshold:
                confidence = min(0.9, 0.6 + (net_sentiment / strong_threshold) * 0.3)
            else:
                confidence = 0.5 + (net_sentiment / strong_threshold) * 0.4
        else:
            sentiment = 'negative'
            if abs(net_sentiment) >= strong_threshold:
                confidence = min(0.9, 0.6 + (abs(net_sentiment) / strong_threshold) * 0.3)
            else:
                confidence = 0.5 + (abs(net_sentiment) / strong_threshold) * 0.4
        
        # Adjust confidence based on total sentiment strength
        if total_sentiment > 0:
            confidence = min(confidence * (1 + total_sentiment / 10), 0.95)
        else:
            confidence = max(confidence * 0.7, 0.3)  # Lower confidence for no sentiment words
        
        return sentiment, round(confidence, 3)
    
    def _create_neutral_result(self, reason: str) -> Dict[str, Any]:
        """
        Create neutral sentiment result with low confidence.
        
        Args:
            reason: Reason for neutral classification
            
        Returns:
            Neutral sentiment result dictionary
        """
        return {
            'sentiment': 'neutral',
            'confidence': 0.3,
            'positive_score': 0.0,
            'negative_score': 0.0,
            'text_length': 0,
            'analysis_method': 'default',
            'reason': reason
        }
    
    def analyze_batch(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze sentiment for a batch of reviews and calculate distribution.
        
        Args:
            reviews: List of review dictionaries with 'review_text' field
            
        Returns:
            Dictionary with sentiment distribution and statistics
        """
        if not reviews:
            return {
                'total_reviews': 0,
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                'sentiment_percentages': {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0},
                'average_confidence': 0.0,
                'analysis_summary': 'No reviews to analyze'
            }
        
        sentiment_counts = Counter()
        confidence_scores = []
        analyzed_reviews = []
        
        for review in reviews:
            text = review.get('review_text', '') or review.get('review', '')
            if text:
                result = self.analyze_sentiment(text)
                sentiment_counts[result['sentiment']] += 1
                confidence_scores.append(result['confidence'])
                
                # Add sentiment info to review copy
                review_with_sentiment = review.copy()
                review_with_sentiment['sentiment_analysis'] = result
                analyzed_reviews.append(review_with_sentiment)
        
        total_analyzed = len(analyzed_reviews)
        if total_analyzed == 0:
            return self._create_empty_batch_result(len(reviews))
        
        # Calculate percentages
        percentages = {}
        for sentiment in ['positive', 'negative', 'neutral']:
            count = sentiment_counts.get(sentiment, 0)
            percentages[sentiment] = round((count / total_analyzed) * 100, 1)
        
        # Calculate statistics
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        result = {
            'total_reviews': len(reviews),
            'analyzed_reviews': total_analyzed,
            'sentiment_distribution': dict(sentiment_counts),
            'sentiment_percentages': percentages,
            'average_confidence': round(avg_confidence, 3),
            'confidence_range': {
                'min': min(confidence_scores) if confidence_scores else 0,
                'max': max(confidence_scores) if confidence_scores else 0
            },
            'reviews_with_sentiment': analyzed_reviews,
            'analysis_summary': self._create_analysis_summary(sentiment_counts, total_analyzed)
        }
        
        logger.info(f"Analyzed sentiment for {total_analyzed} reviews: "
                   f"{sentiment_counts.get('positive', 0)} positive, "
                   f"{sentiment_counts.get('negative', 0)} negative, "
                   f"{sentiment_counts.get('neutral', 0)} neutral")
        
        return result
    
    def _create_empty_batch_result(self, total_reviews: int) -> Dict[str, Any]:
        """
        Create result for batch with no analyzable reviews.
        
        Args:
            total_reviews: Total number of reviews in batch
            
        Returns:
            Empty batch result dictionary
        """
        return {
            'total_reviews': total_reviews,
            'analyzed_reviews': 0,
            'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
            'sentiment_percentages': {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0},
            'average_confidence': 0.0,
            'confidence_range': {'min': 0, 'max': 0},
            'reviews_with_sentiment': [],
            'analysis_summary': f'No analyzable text found in {total_reviews} reviews'
        }
    
    def _create_analysis_summary(self, sentiment_counts: Counter, total: int) -> str:
        """
        Create human-readable analysis summary.
        
        Args:
            sentiment_counts: Counter of sentiment classifications
            total: Total number of analyzed reviews
            
        Returns:
            Summary string
        """
        positive = sentiment_counts.get('positive', 0)
        negative = sentiment_counts.get('negative', 0)
        neutral = sentiment_counts.get('neutral', 0)
        
        if positive > negative and positive > neutral:
            dominant = 'positive'
            percentage = round((positive / total) * 100, 1)
        elif negative > positive and negative > neutral:
            dominant = 'negative'
            percentage = round((negative / total) * 100, 1)
        else:
            dominant = 'neutral'
            percentage = round((neutral / total) * 100, 1)
        
        return f"Overall sentiment is {dominant} ({percentage}% of reviews)"