# ReviewRabbit Example Usage

This directory contains example scripts demonstrating how to use ReviewRabbit programmatically.

## Examples

### Basic Analysis
```python
from reviewrabbit import CodeAnalyzer

analyzer = CodeAnalyzer()
issues, metrics = analyzer.analyze_file('example.py')
print(f"Found {len(issues)} issues")
```

### AI Review
```python
from reviewrabbit import AIReviewer

reviewer = AIReviewer(api_key="your-api-key")
review = reviewer.review_code('example.py', code_content, issues, metrics)
print(f"Code Quality Score: {review.overall_score}/10")
```

### Batch Analysis
```python
from reviewrabbit import CodeAnalyzer

analyzer = CodeAnalyzer()
results = analyzer.analyze_directory('./src/')
print(f"Analyzed {results['total_files']} files")
```
