"""
Core code analyzer module for ReviewRabbit.
Handles AST parsing, static analysis, and code structure analysis.
"""

import ast
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile


@dataclass
class CodeIssue:
    """Represents a code issue found during analysis."""
    file_path: str
    line_number: int
    column: int
    severity: str
    category: str
    message: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None


@dataclass
class CodeMetrics:
    """Represents code quality metrics."""
    file_path: str
    lines_of_code: int
    cyclomatic_complexity: int
    function_count: int
    class_count: int
    import_count: int
    comment_ratio: float


class PythonASTAnalyzer:
    """Analyzes Python code using AST parsing."""
    
    def __init__(self):
        self.issues: List[CodeIssue] = []
        self.metrics: Dict[str, CodeMetrics] = {}
    
    def analyze_file(self, file_path: str) -> Tuple[List[CodeIssue], CodeMetrics]:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            issues = self._analyze_ast(tree, file_path, content)
            metrics = self._calculate_metrics(tree, file_path, content)
            
            return issues, metrics
            
        except SyntaxError as e:
            return [CodeIssue(
                file_path=file_path,
                line_number=e.lineno or 0,
                column=e.offset or 0,
                severity="critical",
                category="syntax_error",
                message=f"Syntax error: {e.msg}",
                code_snippet=content.split('\n')[e.lineno - 1] if e.lineno else None
            )], CodeMetrics(file_path, 0, 0, 0, 0, 0, 0.0)
        except Exception as e:
            return [CodeIssue(
                file_path=file_path,
                line_number=0,
                column=0,
                severity="high",
                category="analysis_error",
                message=f"Analysis error: {str(e)}"
            )], CodeMetrics(file_path, 0, 0, 0, 0, 0, 0.0)
    
    def _analyze_ast(self, tree: ast.AST, file_path: str, content: str) -> List[CodeIssue]:
        """Analyze AST for common issues."""
        issues = []
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            # Check for unused imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if not self._is_import_used(tree, alias.name):
                        issues.append(CodeIssue(
                            file_path=file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            severity="low",
                            category="unused_import",
                            message=f"Unused import: {alias.name}",
                            suggestion=f"Remove unused import: {alias.name}"
                        ))
            
            # Check for long functions
            elif isinstance(node, ast.FunctionDef):
                if len(node.body) > 50:
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        severity="medium",
                        category="code_quality",
                        message=f"Function '{node.name}' is too long ({len(node.body)} lines)",
                        suggestion="Consider breaking this function into smaller functions"
                    ))
                
                # Check for too many parameters
                if len(node.args.args) > 7:
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        severity="medium",
                        category="code_quality",
                        message=f"Function '{node.name}' has too many parameters ({len(node.args.args)})",
                        suggestion="Consider using a data class or dictionary to group related parameters"
                    ))
            
            # Check for hardcoded strings
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                if len(node.value) > 50 and not node.value.startswith(('http', 'https', 'file://')):
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        severity="low",
                        category="best_practices",
                        message="Consider moving long string to a constant or configuration file",
                        suggestion="Extract long strings to module-level constants"
                    ))
            
            # Check for bare except clauses
            elif isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        severity="high",
                        category="error_handling",
                        message="Bare except clause catches all exceptions",
                        suggestion="Specify the exception type or use 'except Exception as e:'"
                    ))
            
            # Check for TODO/FIXME comments
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, str):
                    comment = node.value.value.strip()
                    if comment.upper().startswith(('TODO', 'FIXME', 'HACK', 'XXX')):
                        issues.append(CodeIssue(
                            file_path=file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            severity="info",
                            category="documentation",
                            message=f"Code comment: {comment}",
                            suggestion="Address the TODO/FIXME comment"
                        ))
        
        return issues
    
    def _is_import_used(self, tree: ast.AST, import_name: str) -> bool:
        """Check if an import is used in the AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == import_name:
                return True
            elif isinstance(node, ast.Attribute):
                # Check for module.attribute usage
                if isinstance(node.value, ast.Name) and node.value.id == import_name:
                    return True
        return False
    
    def _calculate_metrics(self, tree: ast.AST, file_path: str, content: str) -> CodeMetrics:
        """Calculate code metrics."""
        lines_of_code = len([line for line in content.split('\n') if line.strip()])
        comment_lines = len([line for line in content.split('\n') if line.strip().startswith('#')])
        comment_ratio = comment_lines / lines_of_code if lines_of_code > 0 else 0.0
        
        function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
        import_count = len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))])
        
        # Calculate cyclomatic complexity
        complexity = 1  # Base complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return CodeMetrics(
            file_path=file_path,
            lines_of_code=lines_of_code,
            cyclomatic_complexity=complexity,
            function_count=function_count,
            class_count=class_count,
            import_count=import_count,
            comment_ratio=comment_ratio
        )


class SecurityAnalyzer:
    """Analyzes code for security vulnerabilities."""
    
    def __init__(self):
        self.security_patterns = {
            'sql_injection': [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'cursor\.execute\s*\(\s*["\'].*%.*["\']',
                r'query\s*=\s*["\'].*%.*["\']',
            ],
            'command_injection': [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
                r'subprocess\.run\s*\(',
                r'eval\s*\(',
                r'exec\s*\(',
            ],
            'path_traversal': [
                r'open\s*\(\s*["\'].*\.\./.*["\']',
                r'file\s*\(\s*["\'].*\.\./.*["\']',
                r'Path\s*\(\s*["\'].*\.\./.*["\']',
            ],
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
            ],
            'insecure_random': [
                r'random\.random\s*\(',
                r'random\.randint\s*\(',
                r'random\.choice\s*\(',
            ]
        }
    
    def analyze_file(self, file_path: str) -> List[CodeIssue]:
        """Analyze file for security vulnerabilities."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for category, patterns in self.security_patterns.items():
                for pattern in patterns:
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            severity = self._get_severity_for_category(category)
                            suggestion = self._get_suggestion_for_category(category)
                            
                            issues.append(CodeIssue(
                                file_path=file_path,
                                line_number=i,
                                column=0,
                                severity=severity,
                                category=f"security_{category}",
                                message=f"Potential {category.replace('_', ' ')} vulnerability",
                                suggestion=suggestion,
                                code_snippet=line.strip()
                            ))
            
        except Exception as e:
            issues.append(CodeIssue(
                file_path=file_path,
                line_number=0,
                column=0,
                severity="high",
                category="analysis_error",
                message=f"Security analysis error: {str(e)}"
            ))
        
        return issues
    
    def _get_severity_for_category(self, category: str) -> str:
        """Get severity level for security category."""
        severity_map = {
            'sql_injection': 'critical',
            'command_injection': 'critical',
            'path_traversal': 'high',
            'hardcoded_secrets': 'high',
            'insecure_random': 'medium'
        }
        return severity_map.get(category, 'medium')
    
    def _get_suggestion_for_category(self, category: str) -> str:
        """Get suggestion for security category."""
        suggestions = {
            'sql_injection': 'Use parameterized queries or an ORM to prevent SQL injection',
            'command_injection': 'Use subprocess with shell=False and validate input',
            'path_traversal': 'Validate and sanitize file paths before use',
            'hardcoded_secrets': 'Use environment variables or secure configuration management',
            'insecure_random': 'Use secrets module for cryptographic purposes'
        }
        return suggestions.get(category, 'Review this code for security implications')


class CodeAnalyzer:
    """Main code analyzer that coordinates different analysis types."""
    
    def __init__(self):
        self.python_analyzer = PythonASTAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
    
    def analyze_file(self, file_path: str) -> Tuple[List[CodeIssue], CodeMetrics]:
        """Analyze a single file."""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.py':
            ast_issues, metrics = self.python_analyzer.analyze_file(file_path)
            security_issues = self.security_analyzer.analyze_file(file_path)
            all_issues = ast_issues + security_issues
            return all_issues, metrics
        else:
            # For non-Python files, return basic analysis
            return [], CodeMetrics(file_path, 0, 0, 0, 0, 0, 0.0)
    
    def analyze_directory(self, directory_path: str, include_patterns: List[str] = None, 
                         exclude_patterns: List[str] = None) -> Dict[str, Any]:
        """Analyze all files in a directory."""
        if include_patterns is None:
            include_patterns = ['*.py']
        if exclude_patterns is None:
            exclude_patterns = ['*/__pycache__/*', '*/venv/*', '*/node_modules/*']
        
        all_issues = []
        all_metrics = {}
        
        for root, dirs, files in os.walk(directory_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(Path(root) / d in Path(p).parents for p in exclude_patterns)]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check if file matches include patterns
                if any(Path(file_path).match(pattern) for pattern in include_patterns):
                    issues, metrics = self.analyze_file(file_path)
                    all_issues.extend(issues)
                    all_metrics[file_path] = metrics
        
        return {
            'issues': all_issues,
            'metrics': all_metrics,
            'total_files': len(all_metrics),
            'total_issues': len(all_issues)
        }
