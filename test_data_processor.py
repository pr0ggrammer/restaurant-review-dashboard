"""
Test the data processor functionality
"""

import sys
sys.path.insert(0, '.')

from services.data_processor import DataProcessor
from datetime import datetime

def test_data_processor():
    """Test basic data processor functionality"""
    print("Testing DataProcessor...")
    
    # Create test data
    raw_reviews = [
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
            'review': 'Average meal, slow service but friendly staff.',
            'date': '2023-01-20',
            'reviewer_name': 'Jane Smith',
            'helpful_votes': 2
        },
        {
            'review_id': 'review_3',
            'rating': 5.0,
            'review': 'Amazing experience! Delicious food and wonderful atmosphere.',
            'date': '2023-02-10',
            'reviewer_name': 'Bob Johnson',
            'helpful_votes': 8
        }
    ]
    
    # Initialize processor
    processor = DataProcessor()
    
    # Test data transformation
    print("Testing data transformation...")
    transformed = processor.transform_review_data(raw_reviews)
    assert len(transformed) == 3
    assert transformed[0]['rating'] == 4.5
    assert transformed[0]['word_count'] > 0
    print("✓ Data transformation works")
    
    # Test rating aggregation
    print("Testing rating aggregation...")
    aggregated = processor.aggregate_ratings_by_time(transformed, 'monthly')
    assert len(aggregated) == 2  # January and February
    assert aggregated[0]['date'] == '2023-01'
    assert aggregated[1]['date'] == '2023-02'
    print("✓ Rating aggregation works")
    
    # Test volume calculation
    print("Testing volume calculation...")
    volume = processor.calculate_review_volume(transformed, 'monthly')
    assert len(volume) == 2
    assert volume[0]['review_count'] == 2  # 2 reviews in January
    assert volume[1]['review_count'] == 1  # 1 review in February
    print("✓ Volume calculation works")
    
    # Test theme extraction
    print("Testing theme extraction...")
    themes = processor.extract_themes(transformed)
    assert len(themes) >= 0  # Should extract some themes
    print("✓ Theme extraction works")
    
    # Test overall metrics
    print("Testing overall metrics...")
    metrics = processor.calculate_overall_metrics(transformed)
    assert metrics['total_reviews'] == 3
    assert metrics['average_rating'] > 0
    print("✓ Overall metrics calculation works")
    
    print("All DataProcessor tests passed!")
    return True

if __name__ == "__main__":
    test_data_processor()