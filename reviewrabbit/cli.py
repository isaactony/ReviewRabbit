"""
Command-line interface for ReviewRabbit.
Provides easy-to-use CLI for code analysis and review.
"""

import click
import os
import sys
from pathlib import Path
from typing import List, Optional
import json
from datetime import datetime

from .analyzer import CodeAnalyzer
from .ai_reviewer import AIReviewer, CodeSuggestionEngine
from .config import ConfigManager
from .reporter import ReportGenerator


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """ReviewRabbit - AI-powered code review and analysis tool."""
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--output', '-o', type=click.Choice(['console', 'json', 'html', 'markdown']), 
              help='Output format')
@click.option('--save-report', is_flag=True, help='Save report to file')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--ai-review', is_flag=True, help='Include AI-powered code review')
@click.option('--max-files', type=int, help='Maximum number of files to analyze')
def analyze(path: str, config: Optional[str], output: Optional[str], 
           save_report: bool, verbose: bool, ai_review: bool, max_files: Optional[int]):
    """Analyze code for bugs, security issues, and quality problems."""
    
    # Load configuration
    config_manager = ConfigManager(config or 'config.yaml')
    try:
        config_obj = config_manager.load_config()
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        sys.exit(1)
    
    # Override config with CLI options
    if output:
        config_obj.output.format = output
    if save_report:
        config_obj.output.save_report = True
    if verbose:
        config_obj.output.verbose = True
    if max_files:
        config_obj.review.max_files_per_review = max_files
    
    # Initialize analyzer
    analyzer = CodeAnalyzer()
    
    # Initialize AI reviewer if requested
    ai_reviewer = None
    suggestion_engine = None
    if ai_review:
        try:
            ai_reviewer = AIReviewer(
                api_key=config_obj.openai.api_key,
                model=config_obj.openai.model,
                max_tokens=config_obj.openai.max_tokens
            )
            suggestion_engine = CodeSuggestionEngine(ai_reviewer)
        except Exception as e:
            click.echo(f"Warning: AI review disabled due to error: {e}", err=True)
            ai_review = False
    
    # Analyze files
    click.echo(f"Analyzing code in: {path}")
    
    if os.path.isfile(path):
        # Analyze single file
        if not config_manager.should_analyze_file(path):
            click.echo(f"Skipping file {path} (excluded by patterns)")
            return
        
        issues, metrics = analyzer.analyze_file(path)
        ai_reviews = []
        
        if ai_review and ai_reviewer:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                ai_review = ai_reviewer.review_code(path, content, issues, metrics)
                ai_reviews = [ai_review]
            except Exception as e:
                click.echo(f"AI review failed for {path}: {e}", err=True)
        
        # Generate report
        reporter = ReportGenerator(config_obj)
        report = reporter.generate_report([path], {path: issues}, {path: metrics}, ai_reviews)
        
    else:
        # Analyze directory
        results = analyzer.analyze_directory(
            path,
            include_patterns=config_obj.file_patterns.include,
            exclude_patterns=config_obj.file_patterns.exclude
        )
        
        # Limit files if specified
        files_to_review = list(results['metrics'].keys())[:config_obj.review.max_files_per_review]
        
        ai_reviews = []
        if ai_review and ai_reviewer:
            click.echo("Generating AI reviews...")
            files_data = []
            
            for file_path in files_to_review:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check file size limit
                    if len(content.encode('utf-8')) > config_manager.get_file_size_limit_bytes():
                        click.echo(f"Skipping {file_path} (file too large)")
                        continue
                    
                    file_issues = [issue for issue in results['issues'] if issue.file_path == file_path]
                    file_metrics = results['metrics'][file_path]
                    
                    files_data.append({
                        'file_path': file_path,
                        'code_content': content,
                        'issues': file_issues,
                        'metrics': file_metrics
                    })
                    
                except Exception as e:
                    click.echo(f"Error reading {file_path}: {e}", err=True)
            
            if files_data:
                ai_reviews = ai_reviewer.batch_review(files_data)
        
        # Generate report
        reporter = ReportGenerator(config_obj)
        report = reporter.generate_report(
            files_to_review,
            {fp: [issue for issue in results['issues'] if issue.file_path == fp] for fp in files_to_review},
            results['metrics'],
            ai_reviews
        )
    
    # Display report
    reporter.display_report(report)
    
    # Save report if requested
    if config_obj.output.save_report:
        reporter.save_report(report)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--suggestions', is_flag=True, help='Include refactoring suggestions')
@click.option('--test-cases', is_flag=True, help='Suggest test cases')
def review(file_path: str, config: Optional[str], suggestions: bool, test_cases: bool):
    """Generate detailed AI review for a single file."""
    
    # Load configuration
    config_manager = ConfigManager(config or 'config.yaml')
    try:
        config_obj = config_manager.load_config()
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        sys.exit(1)
    
    # Initialize AI reviewer
    try:
        ai_reviewer = AIReviewer(
            api_key=config_obj.openai.api_key,
            model=config_obj.openai.model,
            max_tokens=config_obj.openai.max_tokens
        )
        suggestion_engine = CodeSuggestionEngine(ai_reviewer)
    except Exception as e:
        click.echo(f"Error initializing AI reviewer: {e}", err=True)
        sys.exit(1)
    
    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        click.echo(f"Error reading file: {e}", err=True)
        sys.exit(1)
    
    # Check file size
    if len(content.encode('utf-8')) > config_manager.get_file_size_limit_bytes():
        click.echo(f"File too large. Maximum size: {config_obj.review.max_file_size_mb}MB", err=True)
        sys.exit(1)
    
    # Analyze file first
    analyzer = CodeAnalyzer()
    issues, metrics = analyzer.analyze_file(file_path)
    
    # Generate AI review
    click.echo(f"Generating AI review for: {file_path}")
    ai_review = ai_reviewer.review_code(file_path, content, issues, metrics)
    
    # Display review
    click.echo("\n" + "="*80)
    click.echo(f"AI CODE REVIEW: {file_path}")
    click.echo("="*80)
    
    click.echo(f"\nOverall Score: {ai_review.overall_score}/10")
    click.echo(f"\nSummary: {ai_review.summary}")
    
    if ai_review.strengths:
        click.echo("\nStrengths:")
        for strength in ai_review.strengths:
            click.echo(f"  ✓ {strength}")
    
    if ai_review.improvements:
        click.echo("\nAreas for Improvement:")
        for improvement in ai_review.improvements:
            click.echo(f"  • {improvement}")
    
    if ai_review.suggestions:
        click.echo("\nSpecific Suggestions:")
        for suggestion in ai_review.suggestions:
            click.echo(f"  Line {suggestion.get('line', 'N/A')}: {suggestion.get('message', '')}")
            if suggestion.get('code_example'):
                click.echo(f"    Example: {suggestion['code_example']}")
    
    if ai_review.security_concerns:
        click.echo("\nSecurity Concerns:")
        for concern in ai_review.security_concerns:
            click.echo(f"  ⚠ {concern}")
    
    if ai_review.performance_notes:
        click.echo("\nPerformance Notes:")
        for note in ai_review.performance_notes:
            click.echo(f"  📈 {note}")
    
    # Generate additional suggestions if requested
    if suggestions:
        click.echo("\n" + "="*80)
        click.echo("REFACTORING SUGGESTIONS")
        click.echo("="*80)
        
        refactoring_suggestions = suggestion_engine.suggest_refactoring(content, file_path)
        for suggestion in refactoring_suggestions:
            click.echo(f"\nPattern: {suggestion.get('pattern', '')}")
            click.echo(f"Suggestion: {suggestion.get('suggestion', '')}")
            click.echo(f"Explanation: {suggestion.get('explanation', '')}")
    
    if test_cases:
        click.echo("\n" + "="*80)
        click.echo("SUGGESTED TEST CASES")
        click.echo("="*80)
        
        test_suggestions = suggestion_engine.suggest_test_cases(content, file_path)
        for test_case in test_suggestions:
            click.echo(f"\nTest: {test_case.get('name', '')}")
            click.echo(f"Description: {test_case.get('description', '')}")
            click.echo(f"Code: {test_case.get('test_code', '')}")
            click.echo(f"Expected: {test_case.get('expected_result', '')}")


@cli.command()
@click.option('--config', '-c', type=click.Path(), help='Configuration file path')
def init(config: Optional[str]):
    """Initialize ReviewRabbit configuration file."""
    config_path = config or 'config.yaml'
    
    if os.path.exists(config_path):
        if not click.confirm(f"Configuration file {config_path} already exists. Overwrite?"):
            click.echo("Configuration initialization cancelled.")
            return
    
    # Create default configuration
    config_manager = ConfigManager(config_path)
    config_obj = config_manager.load_config()
    
    # Prompt for OpenAI API key if not set
    if not config_obj.openai.api_key:
        api_key = click.prompt("Enter your OpenAI API key", hide_input=True)
        config_obj.openai.api_key = api_key
    
    # Save configuration
    config_manager.save_config(config_obj)
    click.echo(f"Configuration saved to {config_path}")
    click.echo("You can now run 'reviewrabbit analyze <path>' to analyze your code!")


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--format', '-f', type=click.Choice(['json', 'html', 'markdown']), 
              default='json', help='Export format')
def export(path: str, config: Optional[str], format: str):
    """Export analysis results to file."""
    
    # Load configuration
    config_manager = ConfigManager(config or 'config.yaml')
    try:
        config_obj = config_manager.load_config()
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        sys.exit(1)
    
    # Analyze files
    analyzer = CodeAnalyzer()
    
    if os.path.isfile(path):
        issues, metrics = analyzer.analyze_file(path)
        files_data = {path: issues}
        metrics_data = {path: metrics}
    else:
        results = analyzer.analyze_directory(
            path,
            include_patterns=config_obj.file_patterns.include,
            exclude_patterns=config_obj.file_patterns.exclude
        )
        files_data = {fp: [issue for issue in results['issues'] if issue.file_path == fp] 
                     for fp in results['metrics'].keys()}
        metrics_data = results['metrics']
    
    # Generate report
    reporter = ReportGenerator(config_obj)
    report = reporter.generate_report(list(files_data.keys()), files_data, metrics_data, [])
    
    # Export report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reviewrabbit_report_{timestamp}.{format}"
    filepath = os.path.join(config_obj.output.report_directory, filename)
    
    reporter.export_report(report, filepath, format)
    click.echo(f"Report exported to: {filepath}")


if __name__ == '__main__':
    cli()
