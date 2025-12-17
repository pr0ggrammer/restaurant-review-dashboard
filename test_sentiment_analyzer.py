"""
Test the sentiment analyzer functionality
"""

import sys
sys.path.insert(0, '.')

from services.sentiment_analyzer import SentimentAnalyzer

def test_sentiment_analyzer():
    """Test basic sentiment analyzer functionality"""
    print("Testing SentimentAnalyzer...")
    
    # Initialize analyzer
    analyzer = SentimentAnalyzer()
    
    # Test positive sentiment
    print("Testing positive sentiment...")
    positive_text = "This restaurant is amazing! The food was delicious and the service was excellent."
    result = analyzer.analyze_sentiment(positive_text)
    assert result['sentiment'] == 'positive'
    assert result['confidence'] > 0.5
    print(f"✓ Positive sentiment detected: {result['sentiment']} (confidence: {result['confidence']})")
    
    # Test negative sentiment
    print("Testing negative sentiment...")
    negative_text = "Terrible food and awful service. Would not recommend this place to anyone."
    result = analyzer.analyze_sentiment(negative_text)
    assert result['sentiment'] == 'negative'
    assert result['confidence'] > 0.5
    print(f"✓ Negative sentiment detected: {result['sentiment']} (confidence: {result['confidence']})")
    
    # Test neutral sentiment
    print("Testing neutral sentiment...")
    neutral_text = "The restaurant is located on Main Street. They serve food."
    result = analyzer.analyze_sentiment(neutral_text)
    assert result['sentiment'] == 'neutral'
    print(f"✓ Neutral sentiment detected: {result['sentiment']} (confidence: {result['confidence']})")
    
    # Test batch analysis
    print("Testing batch analysis...")
    reviews = [
        {'review_text': 'Great food and excellent service!'},
        {'review_text': 'Terrible experience, would not return.'},
        {'review_text': 'Average meal, nothing special.'},
        {'review_text': 'Amazing restaurant, highly recommend!'},
        {'review_text': 'Poor quality food and slow service.'}
    ]
    
    batch_result = analyzer.analyze_batch(reviews)
    assert batch_result['total_reviews'] == 5
    assert batch_result['analyzed_reviews'] == 5
    assert 'sentiment_distribution' in batch_result
    assert 'sentiment_percentages' in batch_result
    
    print(f"✓ Batch analysis completed:")
    print(f"  - Positive: {batch_result['sentiment_distribution'].get('positive', 0)} reviews")
    print(f"  - Negative: {batch_result['sentiment_distribution'].get('negative', 0)} reviews") 
    print(f"  - Neutral: {batch_result['sentiment_distribution'].get('neutral', 0)} reviews")
    print(f"  - Average confidence: {batch_result['average_confidence']}")
    
    # Test edge cases
    print("Testing edge cases...")
    
    # Empty text
    empty_result = analyzer.analyze_sentiment("")
    assert empty_result['sentiment'] == 'neutral'
    print("✓ Empty text handled correctly")
    
    # Very short text
    short_result = analyzer.analyze_sentiment("OK")
    assert short_result['sentiment'] == 'neutral'
    print("✓ Short text handled correctly")
    
    # Negation handling
    negation_text = "The food was not bad, but not great either."
    negation_result = analyzer.analyze_sentiment(negation_text)
    print(f"✓ Negation handling: {negation_result['sentiment']} (confidence: {negation_result['confidence']})")
    
    print("All SentimentAnalyzer tests passed!")
    return True

if __name__ == "__main__":
    test_sentiment_analyzer()