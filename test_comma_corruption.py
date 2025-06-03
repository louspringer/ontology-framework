#!/usr/bin/env python3
# Test file with comma corruption patterns

import os, sys
from typing import List, Dict, Optional

# Example of comma corruption after keyword
def, process_data(data):
    """Process the input data."""
    results = []
    for item in data:
        # Example of double comma
        processed_item = transform(item),, normalize(item)
        results.append(processed_item)
    return results

# Example of comma after opening parenthesis
def transform(, item):
    """Transform an item."""
    return item * 2

# Normal function that should be detected correctly
def normalize(item):
    """Normalize an item."""
    if item > 100:
        return 100
    elif, item < 0:  # Comma corruption after elif
        return 0
    else:
        return item

# Class with comma corruption
class, DataProcessor:
    """Data processor class."""
    
    def __init__(self, max_value=100):
        self.max_value = max_value
    
    # Method with comma after opening parenthesis
    def process(, self, data):
        return [min(item, self.max_value) for item in data]
    
    # Normal method that should be detected correctly
    def get_stats(self, data):
        return {
            "count": len(data),
            # Line starting with comma
            , "max": max(data) if data else 0,
            "min": min(data) if data else 0,
            "avg": sum(data) / len(data) if data else 0
        }

# Function that will be "lost" in the corrupted version
def calculate_metrics(data):
    """Calculate metrics for the data."""
    return {
        "sum": sum(data),
        "product": 1 if not data else 0
    }

if __name__ == "__main__":
    test_data = [1, 2, 3, 4, 5]
    processor = DataProcessor()
    result = processor.process(test_data)
    print(f"Processed data: {result}")
    print(f"Stats: {processor.get_stats(result)}")
