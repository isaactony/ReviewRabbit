"""
Advanced bug detection patterns and vulnerability scanning.
Extends the core analyzer with additional bug detection capabilities.
"""

import re
import ast
from typing import List, Dict, Any
from .analyzer import CodeIssue


class AdvancedBugDetector:
    """Advanced bug detection patterns."""
    
    def __init__(self):
        self.bug_patterns = {
            'null_pointer': [
                r'\.\w+\s*\(\s*None\s*\)',
                r'if\s+\w+\s*==\s*None\s*:',
                r'if\s+\w+\s*is\s*None\s*:',
            ],
            'resource_leak': [
                r'open\s*\([^)]+\)(?!\s*as\s+)',
                r'file\s*\([^)]+\)(?!\s*as\s+)',
                r'requests\.get\s*\([^)]+\)(?!\s*as\s+)',
            ],
            'infinite_loop': [
                r'while\s+True\s*:',
                r'for\s+\w+\s+in\s+\w+\s*:.*continue',
            ],
            'type_confusion': [
                r'str\s*\(\s*\w+\s*\)\s*\+\s*\d+',
                r'int\s*\(\s*["\'][^"\']*["\']\s*\)',
            ],
            'race_condition': [
                r'threading\.Thread\s*\(',
                r'multiprocessing\.Process\s*\(',
            ]
        }
    
    def detect_bugs(self, file_path: str, content: str) -> List[CodeIssue]:
        """Detect potential bugs in code."""
        issues = []
        lines = content.split('\n')
        
        for category, patterns in self.bug_patterns.items():
            for pattern in patterns:
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        severity = self._get_severity_for_bug(category)
                        suggestion = self._get_suggestion_for_bug(category)
                        
                        issues.append(CodeIssue(
                            file_path=file_path,
                            line_number=i,
                            column=0,
                            severity=severity,
                            category=f"bug_{category}",
                            message=f"Potential {category.replace('_', ' ')} bug detected",
                            suggestion=suggestion,
                            code_snippet=line.strip()
                        ))
        
        return issues
    
    def _get_severity_for_bug(self, category: str) -> str:
        """Get severity for bug category."""
        severity_map = {
            'null_pointer': 'high',
            'resource_leak': 'high',
            'infinite_loop': 'critical',
            'type_confusion': 'medium',
            'race_condition': 'high'
        }
        return severity_map.get(category, 'medium')
    
    def _get_suggestion_for_bug(self, category: str) -> str:
        """Get suggestion for bug category."""
        suggestions = {
            'null_pointer': 'Add null checks before accessing object methods',
            'resource_leak': 'Use context managers (with statements) for resource management',
            'infinite_loop': 'Add proper loop termination conditions',
            'type_confusion': 'Ensure proper type conversion and validation',
            'race_condition': 'Use proper synchronization mechanisms'
        }
        return suggestions.get(category, 'Review this code for potential issues')
