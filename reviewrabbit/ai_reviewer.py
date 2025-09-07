"""
AI-powered code review module using OpenAI API.
Provides intelligent code analysis and suggestions.
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import openai
from .analyzer import CodeIssue, CodeMetrics


@dataclass
class AIReview:
    """Represents an AI-generated code review."""
    file_path: str
    overall_score: float
    summary: str
    strengths: List[str]
    improvements: List[str]
    suggestions: List[Dict[str, str]]
    security_concerns: List[str]
    performance_notes: List[str]


class AIReviewer:
    """AI-powered code reviewer using OpenAI API."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4", max_tokens: int = 2000):
        """Initialize the AI reviewer."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model
        self.max_tokens = max_tokens
    
    def review_code(self, file_path: str, code_content: str, 
                   issues: List[CodeIssue] = None, metrics: CodeMetrics = None) -> AIReview:
        """Generate AI review for a code file."""
        
        # Prepare context for AI
        context = self._prepare_context(file_path, code_content, issues, metrics)
        
        # Generate AI review
        prompt = self._create_review_prompt(context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(file_path, ai_response)
            
        except Exception as e:
            return AIReview(
                file_path=file_path,
                overall_score=0.0,
                summary=f"AI review failed: {str(e)}",
                strengths=[],
                improvements=[],
                suggestions=[],
                security_concerns=[],
                performance_notes=[]
            )
    
    def _prepare_context(self, file_path: str, code_content: str, 
                        issues: List[CodeIssue] = None, metrics: CodeMetrics = None) -> Dict[str, Any]:
        """Prepare context for AI analysis."""
        context = {
            'file_path': file_path,
            'code_content': code_content,
            'file_size': len(code_content.split('\n')),
            'issues': []
        }
        
        if issues:
            context['issues'] = [
                {
                    'severity': issue.severity,
                    'category': issue.category,
                    'message': issue.message,
                    'line': issue.line_number,
                    'suggestion': issue.suggestion
                }
                for issue in issues
            ]
        
        if metrics:
            context['metrics'] = {
                'lines_of_code': metrics.lines_of_code,
                'cyclomatic_complexity': metrics.cyclomatic_complexity,
                'function_count': metrics.function_count,
                'class_count': metrics.class_count,
                'comment_ratio': metrics.comment_ratio
            }
        
        return context
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI code review."""
        return """You are an expert code reviewer and software engineer. Your task is to provide comprehensive, constructive code reviews that help developers improve their code quality, security, and maintainability.

Guidelines for your review:
1. Be constructive and helpful, not critical
2. Focus on actionable suggestions
3. Consider security implications
4. Evaluate code readability and maintainability
5. Check for performance issues
6. Suggest best practices
7. Rate the code on a scale of 1-10

Provide your response in the following JSON format:
{
    "overall_score": 8.5,
    "summary": "Brief summary of the code quality",
    "strengths": ["List of positive aspects"],
    "improvements": ["Areas that need improvement"],
    "suggestions": [
        {
            "line": 15,
            "type": "security",
            "message": "Specific suggestion",
            "code_example": "Suggested improvement"
        }
    ],
    "security_concerns": ["Security issues found"],
    "performance_notes": ["Performance considerations"]
}"""
    
    def _create_review_prompt(self, context: Dict[str, Any]) -> str:
        """Create the review prompt for AI."""
        prompt = f"""Please review the following code file:

File: {context['file_path']}
Lines of code: {context['file_size']}

Code:
```python
{context['code_content']}
```

"""
        
        if context.get('metrics'):
            metrics = context['metrics']
            prompt += f"""
Code Metrics:
- Lines of code: {metrics['lines_of_code']}
- Cyclomatic complexity: {metrics['cyclomatic_complexity']}
- Functions: {metrics['function_count']}
- Classes: {metrics['class_count']}
- Comment ratio: {metrics['comment_ratio']:.2%}

"""
        
        if context.get('issues'):
            prompt += "Static Analysis Issues Found:\n"
            for issue in context['issues']:
                prompt += f"- Line {issue['line']}: [{issue['severity'].upper()}] {issue['message']}\n"
                if issue.get('suggestion'):
                    prompt += f"  Suggestion: {issue['suggestion']}\n"
            prompt += "\n"
        
        prompt += """Please provide a comprehensive code review focusing on:
1. Code quality and readability
2. Security vulnerabilities
3. Performance implications
4. Best practices adherence
5. Maintainability
6. Specific actionable suggestions

Respond in the JSON format specified in the system prompt."""
        
        return prompt
    
    def _parse_ai_response(self, file_path: str, response: str) -> AIReview:
        """Parse AI response into AIReview object."""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                return AIReview(
                    file_path=file_path,
                    overall_score=float(data.get('overall_score', 0)),
                    summary=data.get('summary', ''),
                    strengths=data.get('strengths', []),
                    improvements=data.get('improvements', []),
                    suggestions=data.get('suggestions', []),
                    security_concerns=data.get('security_concerns', []),
                    performance_notes=data.get('performance_notes', [])
                )
        except (json.JSONDecodeError, ValueError, KeyError):
            pass
        
        # Fallback if JSON parsing fails
        return AIReview(
            file_path=file_path,
            overall_score=5.0,
            summary="AI review completed but response format was unexpected",
            strengths=[],
            improvements=[],
            suggestions=[],
            security_concerns=[],
            performance_notes=[]
        )
    
    def batch_review(self, files_data: List[Dict[str, Any]]) -> List[AIReview]:
        """Review multiple files in batch."""
        reviews = []
        
        for file_data in files_data:
            review = self.review_code(
                file_data['file_path'],
                file_data['code_content'],
                file_data.get('issues'),
                file_data.get('metrics')
            )
            reviews.append(review)
        
        return reviews
    
    def generate_summary_report(self, reviews: List[AIReview]) -> Dict[str, Any]:
        """Generate a summary report from multiple reviews."""
        if not reviews:
            return {}
        
        total_score = sum(review.overall_score for review in reviews)
        avg_score = total_score / len(reviews)
        
        all_strengths = []
        all_improvements = []
        all_security_concerns = []
        all_performance_notes = []
        
        for review in reviews:
            all_strengths.extend(review.strengths)
            all_improvements.extend(review.improvements)
            all_security_concerns.extend(review.security_concerns)
            all_performance_notes.extend(review.performance_notes)
        
        return {
            'total_files_reviewed': len(reviews),
            'average_score': avg_score,
            'top_strengths': self._get_top_items(all_strengths),
            'common_improvements': self._get_top_items(all_improvements),
            'security_summary': self._get_top_items(all_security_concerns),
            'performance_summary': self._get_top_items(all_performance_notes),
            'file_scores': [
                {'file': review.file_path, 'score': review.overall_score}
                for review in reviews
            ]
        }
    
    def _get_top_items(self, items: List[str], limit: int = 5) -> List[str]:
        """Get the most common items from a list."""
        from collections import Counter
        return [item for item, count in Counter(items).most_common(limit)]


class CodeSuggestionEngine:
    """Engine for generating code suggestions and improvements."""
    
    def __init__(self, ai_reviewer: AIReviewer):
        self.ai_reviewer = ai_reviewer
    
    def suggest_refactoring(self, code_content: str, file_path: str) -> List[Dict[str, str]]:
        """Suggest refactoring opportunities."""
        prompt = f"""Analyze the following code and suggest specific refactoring opportunities:

File: {file_path}
Code:
```python
{code_content}
```

Please provide specific refactoring suggestions with:
1. The current problematic code pattern
2. The suggested improvement
3. Explanation of why the refactoring is beneficial

Format as JSON:
{{
    "suggestions": [
        {{
            "pattern": "current code pattern",
            "suggestion": "improved code",
            "explanation": "why this is better"
        }}
    ]
}}"""
        
        try:
            response = self.ai_reviewer.client.chat.completions.create(
                model=self.ai_reviewer.model,
                messages=[
                    {"role": "system", "content": "You are an expert software engineer specializing in code refactoring and best practices."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.2
            )
            
            ai_response = response.choices[0].message.content
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = ai_response[json_start:json_end]
                data = json.loads(json_str)
                return data.get('suggestions', [])
                
        except Exception:
            pass
        
        return []
    
    def suggest_test_cases(self, code_content: str, file_path: str) -> List[Dict[str, str]]:
        """Suggest test cases for the code."""
        prompt = f"""Analyze the following code and suggest comprehensive test cases:

File: {file_path}
Code:
```python
{code_content}
```

Please suggest test cases covering:
1. Normal operation scenarios
2. Edge cases
3. Error conditions
4. Boundary values

Format as JSON:
{{
    "test_cases": [
        {{
            "name": "test case name",
            "description": "what this test verifies",
            "test_code": "pytest test code",
            "expected_result": "expected outcome"
        }}
    ]
}}"""
        
        try:
            response = self.ai_reviewer.client.chat.completions.create(
                model=self.ai_reviewer.model,
                messages=[
                    {"role": "system", "content": "You are an expert in software testing and test-driven development."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.2
            )
            
            ai_response = response.choices[0].message.content
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = ai_response[json_start:json_end]
                data = json.loads(json_str)
                return data.get('test_cases', [])
                
        except Exception:
            pass
        
        return []
