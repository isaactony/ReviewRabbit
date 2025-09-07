"""
Configuration management for ReviewRabbit.
Handles loading and validation of configuration files.
"""

import os
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class OpenAIConfig:
    """OpenAI API configuration."""
    api_key: str = ""
    model: str = "gpt-4"
    max_tokens: int = 2000
    temperature: float = 0.3


@dataclass
class AnalysisConfig:
    """Analysis configuration."""
    enabled_checks: List[str] = field(default_factory=lambda: [
        "syntax_errors", "security_vulnerabilities", "code_quality", 
        "performance_issues", "best_practices", "documentation"
    ])
    severity_levels: Dict[str, int] = field(default_factory=lambda: {
        "critical": 1, "high": 2, "medium": 3, "low": 4, "info": 5
    })


@dataclass
class FilePatternsConfig:
    """File patterns configuration."""
    include: List[str] = field(default_factory=lambda: [
        "*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.java", 
        "*.cpp", "*.c", "*.cs", "*.go", "*.rs", "*.php", "*.rb"
    ])
    exclude: List[str] = field(default_factory=lambda: [
        "*/node_modules/*", "*/venv/*", "*/env/*", "*/.git/*",
        "*/__pycache__/*", "*/build/*", "*/dist/*", "*/target/*"
    ])


@dataclass
class OutputConfig:
    """Output configuration."""
    format: str = "console"
    save_report: bool = True
    report_directory: str = "./reports"
    verbose: bool = False


@dataclass
class ReviewConfig:
    """Review configuration."""
    max_files_per_review: int = 10
    max_file_size_mb: int = 1
    include_suggestions: bool = True
    include_examples: bool = True
    language: str = "english"


@dataclass
class Config:
    """Main configuration class."""
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    file_patterns: FilePatternsConfig = field(default_factory=FilePatternsConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    review: ReviewConfig = field(default_factory=ReviewConfig)


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = Config()
    
    def load_config(self) -> Config:
        """Load configuration from file and environment variables."""
        # Load from file if it exists
        if os.path.exists(self.config_path):
            self._load_from_file()
        
        # Override with environment variables
        self._load_from_env()
        
        # Validate configuration
        self._validate_config()
        
        return self.config
    
    def _load_from_file(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                return
            
            # Load OpenAI config
            if 'openai' in data:
                openai_data = data['openai']
                self.config.openai = OpenAIConfig(
                    api_key=openai_data.get('api_key', ''),
                    model=openai_data.get('model', 'gpt-4'),
                    max_tokens=openai_data.get('max_tokens', 2000),
                    temperature=openai_data.get('temperature', 0.3)
                )
            
            # Load analysis config
            if 'analysis' in data:
                analysis_data = data['analysis']
                self.config.analysis = AnalysisConfig(
                    enabled_checks=analysis_data.get('enabled_checks', self.config.analysis.enabled_checks),
                    severity_levels=analysis_data.get('severity_levels', self.config.analysis.severity_levels)
                )
            
            # Load file patterns config
            if 'file_patterns' in data:
                patterns_data = data['file_patterns']
                self.config.file_patterns = FilePatternsConfig(
                    include=patterns_data.get('include', self.config.file_patterns.include),
                    exclude=patterns_data.get('exclude', self.config.file_patterns.exclude)
                )
            
            # Load output config
            if 'output' in data:
                output_data = data['output']
                self.config.output = OutputConfig(
                    format=output_data.get('format', 'console'),
                    save_report=output_data.get('save_report', True),
                    report_directory=output_data.get('report_directory', './reports'),
                    verbose=output_data.get('verbose', False)
                )
            
            # Load review config
            if 'review' in data:
                review_data = data['review']
                self.config.review = ReviewConfig(
                    max_files_per_review=review_data.get('max_files_per_review', 10),
                    max_file_size_mb=review_data.get('max_file_size_mb', 1),
                    include_suggestions=review_data.get('include_suggestions', True),
                    include_examples=review_data.get('include_examples', True),
                    language=review_data.get('language', 'english')
                )
                
        except Exception as e:
            print(f"Warning: Failed to load config file {self.config_path}: {e}")
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # OpenAI configuration
        if os.getenv('OPENAI_API_KEY'):
            self.config.openai.api_key = os.getenv('OPENAI_API_KEY')
        
        if os.getenv('OPENAI_MODEL'):
            self.config.openai.model = os.getenv('OPENAI_MODEL')
        
        if os.getenv('OPENAI_MAX_TOKENS'):
            try:
                self.config.openai.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS'))
            except ValueError:
                pass
        
        if os.getenv('OPENAI_TEMPERATURE'):
            try:
                self.config.openai.temperature = float(os.getenv('OPENAI_TEMPERATURE'))
            except ValueError:
                pass
        
        # Output configuration
        if os.getenv('OUTPUT_FORMAT'):
            self.config.output.format = os.getenv('OUTPUT_FORMAT')
        
        if os.getenv('VERBOSE'):
            self.config.output.verbose = os.getenv('VERBOSE').lower() in ('true', '1', 'yes')
        
        if os.getenv('REPORT_DIRECTORY'):
            self.config.output.report_directory = os.getenv('REPORT_DIRECTORY')
    
    def _validate_config(self):
        """Validate configuration values."""
        # Validate OpenAI API key
        if not self.config.openai.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or configure in config.yaml")
        
        # Validate model
        valid_models = ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']
        if self.config.openai.model not in valid_models:
            print(f"Warning: Model {self.config.openai.model} may not be supported. Valid models: {valid_models}")
        
        # Validate output format
        valid_formats = ['console', 'json', 'html', 'markdown']
        if self.config.output.format not in valid_formats:
            raise ValueError(f"Invalid output format: {self.config.output.format}. Valid formats: {valid_formats}")
        
        # Validate severity levels
        required_severities = ['critical', 'high', 'medium', 'low', 'info']
        for severity in required_severities:
            if severity not in self.config.analysis.severity_levels:
                raise ValueError(f"Missing required severity level: {severity}")
        
        # Create report directory if it doesn't exist
        if self.config.output.save_report:
            os.makedirs(self.config.output.report_directory, exist_ok=True)
    
    def save_config(self, config: Config = None):
        """Save current configuration to file."""
        if config is None:
            config = self.config
        
        config_data = {
            'openai': {
                'api_key': config.openai.api_key,
                'model': config.openai.model,
                'max_tokens': config.openai.max_tokens,
                'temperature': config.openai.temperature
            },
            'analysis': {
                'enabled_checks': config.analysis.enabled_checks,
                'severity_levels': config.analysis.severity_levels
            },
            'file_patterns': {
                'include': config.file_patterns.include,
                'exclude': config.file_patterns.exclude
            },
            'output': {
                'format': config.output.format,
                'save_report': config.output.save_report,
                'report_directory': config.output.report_directory,
                'verbose': config.output.verbose
            },
            'review': {
                'max_files_per_review': config.review.max_files_per_review,
                'max_file_size_mb': config.review.max_file_size_mb,
                'include_suggestions': config.review.include_suggestions,
                'include_examples': config.review.include_examples,
                'language': config.review.language
            }
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config file {self.config_path}: {e}")
    
    def get_file_size_limit_bytes(self) -> int:
        """Get file size limit in bytes."""
        return self.config.review.max_file_size_mb * 1024 * 1024
    
    def should_analyze_file(self, file_path: str) -> bool:
        """Check if a file should be analyzed based on patterns."""
        path = Path(file_path)
        
        # Check include patterns
        include_match = any(path.match(pattern) for pattern in self.config.file_patterns.include)
        if not include_match:
            return False
        
        # Check exclude patterns
        exclude_match = any(path.match(pattern) for pattern in self.config.file_patterns.exclude)
        if exclude_match:
            return False
        
        return True
    
    def is_check_enabled(self, check_name: str) -> bool:
        """Check if a specific analysis check is enabled."""
        return check_name in self.config.analysis.enabled_checks
