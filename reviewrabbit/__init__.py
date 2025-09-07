"""
ReviewRabbit - AI-powered code review and analysis tool.

A comprehensive code analysis solution that combines static analysis
with AI-powered code review to catch bugs, security vulnerabilities,
and provide intelligent suggestions for code improvement.
"""

__version__ = "1.0.0"
__author__ = "ReviewRabbit Team"
__email__ = "team@reviewrabbit.dev"

from .analyzer import CodeAnalyzer, CodeIssue, CodeMetrics
from .ai_reviewer import AIReviewer, AIReview, CodeSuggestionEngine
from .config import Config, ConfigManager
from .reporter import ReportGenerator, ReportData
from .cli import cli

__all__ = [
    'CodeAnalyzer',
    'CodeIssue', 
    'CodeMetrics',
    'AIReviewer',
    'AIReview',
    'CodeSuggestionEngine',
    'Config',
    'ConfigManager',
    'ReportGenerator',
    'ReportData',
    'cli'
]
