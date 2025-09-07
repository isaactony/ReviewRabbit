"""
Reporting system for ReviewRabbit.
Handles generation and display of analysis reports in various formats.
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

from .analyzer import CodeIssue, CodeMetrics
from .ai_reviewer import AIReview
from .config import Config


@dataclass
class ReportData:
    """Container for report data."""
    files_analyzed: List[str]
    issues_by_file: Dict[str, List[CodeIssue]]
    metrics_by_file: Dict[str, CodeMetrics]
    ai_reviews: List[AIReview]
    total_issues: int
    total_files: int
    analysis_time: float
    timestamp: datetime


class ReportGenerator:
    """Generates and displays analysis reports."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def generate_report(self, files_analyzed: List[str], 
                      issues_by_file: Dict[str, List[CodeIssue]],
                      metrics_by_file: Dict[str, CodeMetrics],
                      ai_reviews: List[AIReview],
                      analysis_time: float = 0.0) -> ReportData:
        """Generate report data."""
        
        total_issues = sum(len(issues) for issues in issues_by_file.values())
        
        return ReportData(
            files_analyzed=files_analyzed,
            issues_by_file=issues_by_file,
            metrics_by_file=metrics_by_file,
            ai_reviews=ai_reviews,
            total_issues=total_issues,
            total_files=len(files_analyzed),
            analysis_time=analysis_time,
            timestamp=datetime.now()
        )
    
    def display_report(self, report: ReportData):
        """Display report in console format."""
        if self.config.output.format == 'console':
            self._display_console_report(report)
        elif self.config.output.format == 'json':
            self._display_json_report(report)
        else:
            self._display_console_report(report)
    
    def _display_console_report(self, report: ReportData):
        """Display console-formatted report."""
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.text import Text
        from rich import box
        
        console = Console()
        
        # Header
        console.print("\n" + "="*80)
        console.print("🐰 ReviewRabbit - Code Analysis Report", style="bold blue")
        console.print("="*80)
        
        # Summary
        summary_table = Table(title="Analysis Summary", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Files Analyzed", str(report.total_files))
        summary_table.add_row("Total Issues", str(report.total_issues))
        summary_table.add_row("Analysis Time", f"{report.analysis_time:.2f}s")
        summary_table.add_row("Timestamp", report.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        
        console.print(summary_table)
        
        # Issues by severity
        if report.total_issues > 0:
            severity_counts = self._count_issues_by_severity(report.issues_by_file)
            
            severity_table = Table(title="Issues by Severity", box=box.ROUNDED)
            severity_table.add_column("Severity", style="bold")
            severity_table.add_column("Count", style="yellow")
            
            severity_colors = {
                'critical': 'red',
                'high': 'orange3',
                'medium': 'yellow',
                'low': 'blue',
                'info': 'green'
            }
            
            for severity, count in severity_counts.items():
                color = severity_colors.get(severity, 'white')
                severity_table.add_row(
                    Text(severity.upper(), style=f"bold {color}"),
                    str(count)
                )
            
            console.print(severity_table)
        
        # AI Reviews Summary
        if report.ai_reviews:
            console.print("\n" + "="*80)
            console.print("🤖 AI Code Reviews", style="bold magenta")
            console.print("="*80)
            
            avg_score = sum(review.overall_score for review in report.ai_reviews) / len(report.ai_reviews)
            console.print(f"Average Code Quality Score: {avg_score:.1f}/10", style="bold")
            
            for review in report.ai_reviews:
                score_color = self._get_score_color(review.overall_score)
                console.print(f"\n📁 {review.file_path}")
                console.print(f"   Score: {review.overall_score}/10", style=f"bold {score_color}")
                console.print(f"   Summary: {review.summary}")
                
                if review.strengths:
                    console.print("   Strengths:", style="green")
                    for strength in review.strengths[:3]:  # Show top 3
                        console.print(f"     ✓ {strength}")
                
                if review.improvements:
                    console.print("   Improvements:", style="yellow")
                    for improvement in review.improvements[:3]:  # Show top 3
                        console.print(f"     • {improvement}")
        
        # Detailed Issues
        if report.total_issues > 0:
            console.print("\n" + "="*80)
            console.print("🔍 Detailed Issues", style="bold red")
            console.print("="*80)
            
            for file_path, issues in report.issues_by_file.items():
                if not issues:
                    continue
                
                console.print(f"\n📄 {file_path}")
                
                # Group issues by severity
                issues_by_severity = {}
                for issue in issues:
                    if issue.severity not in issues_by_severity:
                        issues_by_severity[issue.severity] = []
                    issues_by_severity[issue.severity].append(issue)
                
                for severity in ['critical', 'high', 'medium', 'low', 'info']:
                    if severity in issues_by_severity:
                        color = severity_colors.get(severity, 'white')
                        console.print(f"  {severity.upper()}:", style=f"bold {color}")
                        
                        for issue in issues_by_severity[severity]:
                            console.print(f"    Line {issue.line_number}: {issue.message}")
                            if issue.suggestion:
                                console.print(f"      💡 {issue.suggestion}")
                            if issue.code_snippet:
                                console.print(f"      Code: {issue.code_snippet}")
        
        # Code Metrics
        if report.metrics_by_file:
            console.print("\n" + "="*80)
            console.print("📊 Code Metrics", style="bold cyan")
            console.print("="*80)
            
            metrics_table = Table(title="File Metrics", box=box.ROUNDED)
            metrics_table.add_column("File", style="cyan")
            metrics_table.add_column("Lines", style="green")
            metrics_table.add_column("Functions", style="blue")
            metrics_table.add_column("Classes", style="magenta")
            metrics_table.add_column("Complexity", style="yellow")
            metrics_table.add_column("Comments", style="dim")
            
            for file_path, metrics in report.metrics_by_file.items():
                metrics_table.add_row(
                    Path(file_path).name,
                    str(metrics.lines_of_code),
                    str(metrics.function_count),
                    str(metrics.class_count),
                    str(metrics.cyclomatic_complexity),
                    f"{metrics.comment_ratio:.1%}"
                )
            
            console.print(metrics_table)
        
        console.print("\n" + "="*80)
        console.print("Analysis Complete! 🎉", style="bold green")
        console.print("="*80)
    
    def _display_json_report(self, report: ReportData):
        """Display JSON-formatted report."""
        report_dict = {
            'summary': {
                'files_analyzed': report.total_files,
                'total_issues': report.total_issues,
                'analysis_time': report.analysis_time,
                'timestamp': report.timestamp.isoformat()
            },
            'issues_by_severity': self._count_issues_by_severity(report.issues_by_file),
            'files': []
        }
        
        for file_path in report.files_analyzed:
            file_data = {
                'path': file_path,
                'issues': [],
                'metrics': None,
                'ai_review': None
            }
            
            # Add issues
            if file_path in report.issues_by_file:
                for issue in report.issues_by_file[file_path]:
                    file_data['issues'].append({
                        'line': issue.line_number,
                        'column': issue.column,
                        'severity': issue.severity,
                        'category': issue.category,
                        'message': issue.message,
                        'suggestion': issue.suggestion,
                        'code_snippet': issue.code_snippet
                    })
            
            # Add metrics
            if file_path in report.metrics_by_file:
                metrics = report.metrics_by_file[file_path]
                file_data['metrics'] = {
                    'lines_of_code': metrics.lines_of_code,
                    'cyclomatic_complexity': metrics.cyclomatic_complexity,
                    'function_count': metrics.function_count,
                    'class_count': metrics.class_count,
                    'import_count': metrics.import_count,
                    'comment_ratio': metrics.comment_ratio
                }
            
            # Add AI review
            ai_review = next((r for r in report.ai_reviews if r.file_path == file_path), None)
            if ai_review:
                file_data['ai_review'] = {
                    'overall_score': ai_review.overall_score,
                    'summary': ai_review.summary,
                    'strengths': ai_review.strengths,
                    'improvements': ai_review.improvements,
                    'suggestions': ai_review.suggestions,
                    'security_concerns': ai_review.security_concerns,
                    'performance_notes': ai_review.performance_notes
                }
            
            report_dict['files'].append(file_data)
        
        print(json.dumps(report_dict, indent=2))
    
    def save_report(self, report: ReportData):
        """Save report to file."""
        if not self.config.output.save_report:
            return
        
        timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
        
        if self.config.output.format == 'json':
            filename = f"reviewrabbit_report_{timestamp}.json"
            self._save_json_report(report, filename)
        elif self.config.output.format == 'html':
            filename = f"reviewrabbit_report_{timestamp}.html"
            self._save_html_report(report, filename)
        elif self.config.output.format == 'markdown':
            filename = f"reviewrabbit_report_{timestamp}.md"
            self._save_markdown_report(report, filename)
        else:
            filename = f"reviewrabbit_report_{timestamp}.txt"
            self._save_text_report(report, filename)
    
    def export_report(self, report: ReportData, filepath: str, format: str):
        """Export report in specified format."""
        if format == 'json':
            self._save_json_report(report, filepath)
        elif format == 'html':
            self._save_html_report(report, filepath)
        elif format == 'markdown':
            self._save_markdown_report(report, filepath)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _save_json_report(self, report: ReportData, filepath: str):
        """Save report as JSON."""
        report_dict = {
            'summary': {
                'files_analyzed': report.total_files,
                'total_issues': report.total_issues,
                'analysis_time': report.analysis_time,
                'timestamp': report.timestamp.isoformat()
            },
            'issues_by_severity': self._count_issues_by_severity(report.issues_by_file),
            'files': []
        }
        
        for file_path in report.files_analyzed:
            file_data = {
                'path': file_path,
                'issues': [],
                'metrics': None,
                'ai_review': None
            }
            
            if file_path in report.issues_by_file:
                for issue in report.issues_by_file[file_path]:
                    file_data['issues'].append({
                        'line': issue.line_number,
                        'column': issue.column,
                        'severity': issue.severity,
                        'category': issue.category,
                        'message': issue.message,
                        'suggestion': issue.suggestion,
                        'code_snippet': issue.code_snippet
                    })
            
            if file_path in report.metrics_by_file:
                metrics = report.metrics_by_file[file_path]
                file_data['metrics'] = {
                    'lines_of_code': metrics.lines_of_code,
                    'cyclomatic_complexity': metrics.cyclomatic_complexity,
                    'function_count': metrics.function_count,
                    'class_count': metrics.class_count,
                    'import_count': metrics.import_count,
                    'comment_ratio': metrics.comment_ratio
                }
            
            ai_review = next((r for r in report.ai_reviews if r.file_path == file_path), None)
            if ai_review:
                file_data['ai_review'] = {
                    'overall_score': ai_review.overall_score,
                    'summary': ai_review.summary,
                    'strengths': ai_review.strengths,
                    'improvements': ai_review.improvements,
                    'suggestions': ai_review.suggestions,
                    'security_concerns': ai_review.security_concerns,
                    'performance_notes': ai_review.performance_notes
                }
            
            report_dict['files'].append(file_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2)
    
    def _save_html_report(self, report: ReportData, filepath: str):
        """Save report as HTML."""
        html_content = self._generate_html_report(report)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _save_markdown_report(self, report: ReportData, filepath: str):
        """Save report as Markdown."""
        md_content = self._generate_markdown_report(report)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def _save_text_report(self, report: ReportData, filepath: str):
        """Save report as plain text."""
        # This would be similar to console output but without rich formatting
        pass
    
    def _generate_html_report(self, report: ReportData) -> str:
        """Generate HTML report content."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ReviewRabbit Report - {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .issue {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }}
        .critical {{ border-left-color: #d32f2f; }}
        .high {{ border-left-color: #f57c00; }}
        .medium {{ border-left-color: #fbc02d; }}
        .low {{ border-left-color: #1976d2; }}
        .info {{ border-left-color: #388e3c; }}
        .metrics {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
        .ai-review {{ background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🐰 ReviewRabbit Code Analysis Report</h1>
        <p>Generated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Files Analyzed: {report.total_files}</p>
        <p>Total Issues: {report.total_issues}</p>
        <p>Analysis Time: {report.analysis_time:.2f}s</p>
    </div>
"""
        
        # Add issues
        if report.total_issues > 0:
            html += "<h2>Issues Found</h2>"
            for file_path, issues in report.issues_by_file.items():
                if issues:
                    html += f"<h3>{file_path}</h3>"
                    for issue in issues:
                        html += f"""
                        <div class="issue {issue.severity}">
                            <strong>Line {issue.line_number}:</strong> {issue.message}<br>
                            <em>Category:</em> {issue.category}<br>
                            {f'<em>Suggestion:</em> {issue.suggestion}<br>' if issue.suggestion else ''}
                        </div>
                        """
        
        # Add AI reviews
        if report.ai_reviews:
            html += "<h2>AI Code Reviews</h2>"
            for review in report.ai_reviews:
                html += f"""
                <div class="ai-review">
                    <h3>{review.file_path}</h3>
                    <p><strong>Score:</strong> {review.overall_score}/10</p>
                    <p><strong>Summary:</strong> {review.summary}</p>
                    {f'<p><strong>Strengths:</strong> {", ".join(review.strengths)}</p>' if review.strengths else ''}
                    {f'<p><strong>Improvements:</strong> {", ".join(review.improvements)}</p>' if review.improvements else ''}
                </div>
                """
        
        html += "</body></html>"
        return html
    
    def _generate_markdown_report(self, report: ReportData) -> str:
        """Generate Markdown report content."""
        md = f"""# 🐰 ReviewRabbit Code Analysis Report

**Generated:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Files Analyzed:** {report.total_files}
- **Total Issues:** {report.total_issues}
- **Analysis Time:** {report.analysis_time:.2f}s

"""
        
        # Add issues by severity
        severity_counts = self._count_issues_by_severity(report.issues_by_file)
        if severity_counts:
            md += "## Issues by Severity\n\n"
            for severity, count in severity_counts.items():
                md += f"- **{severity.upper()}:** {count}\n"
            md += "\n"
        
        # Add detailed issues
        if report.total_issues > 0:
            md += "## Detailed Issues\n\n"
            for file_path, issues in report.issues_by_file.items():
                if issues:
                    md += f"### {file_path}\n\n"
                    for issue in issues:
                        md += f"- **Line {issue.line_number}:** {issue.message}\n"
                        md += f"  - *Category:* {issue.category}\n"
                        md += f"  - *Severity:* {issue.severity}\n"
                        if issue.suggestion:
                            md += f"  - *Suggestion:* {issue.suggestion}\n"
                        md += "\n"
        
        # Add AI reviews
        if report.ai_reviews:
            md += "## AI Code Reviews\n\n"
            for review in report.ai_reviews:
                md += f"### {review.file_path}\n\n"
                md += f"**Score:** {review.overall_score}/10\n\n"
                md += f"**Summary:** {review.summary}\n\n"
                
                if review.strengths:
                    md += "**Strengths:**\n"
                    for strength in review.strengths:
                        md += f"- {strength}\n"
                    md += "\n"
                
                if review.improvements:
                    md += "**Areas for Improvement:**\n"
                    for improvement in review.improvements:
                        md += f"- {improvement}\n"
                    md += "\n"
        
        return md
    
    def _count_issues_by_severity(self, issues_by_file: Dict[str, List[CodeIssue]]) -> Dict[str, int]:
        """Count issues by severity level."""
        severity_counts = {}
        for issues in issues_by_file.values():
            for issue in issues:
                severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        return severity_counts
    
    def _get_score_color(self, score: float) -> str:
        """Get color for score display."""
        if score >= 8:
            return "green"
        elif score >= 6:
            return "yellow"
        else:
            return "red"
