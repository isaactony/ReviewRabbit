# 🐰 ReviewRabbit - AI-Powered Code Review Tool

ReviewRabbit is an intelligent code analysis and review tool that combines static analysis with AI-powered insights to automatically catch bugs, security vulnerabilities, and provide actionable suggestions for code improvement.

##  Features

- ** Static Code Analysis**: Comprehensive AST-based analysis for Python code
- ** AI-Powered Reviews**: Intelligent code review using OpenAI's GPT models
- ** Security Scanning**: Detection of common security vulnerabilities
- ** Bug Detection**: Advanced pattern matching for potential bugs
- ** Code Metrics**: Detailed metrics including complexity, maintainability scores
- ** Multiple Output Formats**: Console, JSON, HTML, and Markdown reports
- ** Configurable**: Customizable rules and analysis settings
- ** Easy CLI**: Simple command-line interface for quick analysis

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ReviewRabbit.git
cd ReviewRabbit
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Basic Usage

1. **Initialize configuration**:
```bash
python main.py init
```

2. **Analyze a single file**:
```bash
python main.py analyze path/to/your/file.py
```

3. **Analyze a directory**:
```bash
python main.py analyze path/to/your/project/
```

4. **Generate AI-powered review**:
```bash
python main.py review path/to/your/file.py --ai-review
```

## 📖 Detailed Usage

### Command Line Interface

#### `analyze` - Code Analysis
```bash
python main.py analyze <path> [options]
```

**Options:**
- `--config, -c`: Specify configuration file path
- `--output, -o`: Output format (console, json, html, markdown)
- `--save-report`: Save report to file
- `--verbose, -v`: Verbose output
- `--ai-review`: Include AI-powered code review
- `--max-files`: Maximum number of files to analyze

**Examples:**
```bash
# Basic analysis
python main.py analyze src/

# With AI review and HTML output
python main.py analyze src/ --ai-review --output html --save-report

# Analyze specific file with verbose output
python main.py analyze main.py --verbose --ai-review
```

#### `review` - AI Code Review
```bash
python main.py review <file_path> [options]
```

**Options:**
- `--config, -c`: Configuration file path
- `--suggestions`: Include refactoring suggestions
- `--test-cases`: Suggest test cases

**Examples:**
```bash
# Basic AI review
python main.py review main.py

# With refactoring suggestions
python main.py review main.py --suggestions

# With test case suggestions
python main.py review main.py --test-cases
```

#### `export` - Export Reports
```bash
python main.py export <path> [options]
```

**Options:**
- `--config, -c`: Configuration file path
- `--format, -f`: Export format (json, html, markdown)

### Configuration

ReviewRabbit uses a YAML configuration file (`config.yaml`) for customization:

```yaml
# OpenAI API Configuration
openai:
  api_key: ""  # Set via OPENAI_API_KEY environment variable
  model: "gpt-4"
  max_tokens: 2000
  temperature: 0.3

# Analysis Settings
analysis:
  enabled_checks:
    - syntax_errors
    - security_vulnerabilities
    - code_quality
    - performance_issues
    - best_practices
    - documentation
  
  severity_levels:
    critical: 1
    high: 2
    medium: 3
    low: 4
    info: 5

# File Patterns
file_patterns:
  include:
    - "*.py"
    - "*.js"
    - "*.ts"
  
  exclude:
    - "*/node_modules/*"
    - "*/venv/*"
    - "*/.git/*"

# Output Settings
output:
  format: "console"
  save_report: true
  report_directory: "./reports"
  verbose: false

# Review Settings
review:
  max_files_per_review: 10
  max_file_size_mb: 1
  include_suggestions: true
  include_examples: true
  language: "english"
```

## 🔧 Analysis Types

### Static Analysis
- **Syntax Errors**: Detection of Python syntax issues
- **Code Quality**: Long functions, too many parameters, complexity analysis
- **Best Practices**: Unused imports, hardcoded strings, bare except clauses
- **Documentation**: TODO/FIXME comment detection

### Security Analysis
- **SQL Injection**: Detection of unsafe SQL query patterns
- **Command Injection**: Identification of unsafe subprocess calls
- **Path Traversal**: Detection of directory traversal vulnerabilities
- **Hardcoded Secrets**: Identification of exposed credentials
- **Insecure Random**: Detection of weak random number generation

### Bug Detection
- **Null Pointer**: Potential null reference issues
- **Resource Leaks**: Unclosed file handles and connections
- **Infinite Loops**: Detection of potentially infinite loops
- **Type Confusion**: Mixed type operations
- **Race Conditions**: Threading and concurrency issues

### AI-Powered Analysis
- **Code Quality Scoring**: Overall code quality assessment (1-10 scale)
- **Intelligent Suggestions**: Context-aware improvement recommendations
- **Security Assessment**: AI-powered security vulnerability analysis
- **Performance Analysis**: Performance optimization suggestions
- **Refactoring Opportunities**: Specific refactoring recommendations
- **Test Case Generation**: Automated test case suggestions

## 📊 Report Formats

### Console Output
Rich, colorized console output with tables and formatted text.

### JSON Export
```json
{
  "summary": {
    "files_analyzed": 5,
    "total_issues": 12,
    "analysis_time": 2.34,
    "timestamp": "2024-01-15T10:30:00"
  },
  "issues_by_severity": {
    "critical": 1,
    "high": 3,
    "medium": 5,
    "low": 3
  },
  "files": [...]
}
```

### HTML Report
Interactive HTML report with styling and collapsible sections.

### Markdown Report
GitHub-compatible markdown format for documentation and PR comments.

## 🛠️ API Usage

You can also use ReviewRabbit programmatically:

```python
from reviewrabbit import CodeAnalyzer, AIReviewer, ConfigManager

# Load configuration
config_manager = ConfigManager()
config = config_manager.load_config()

# Initialize analyzer
analyzer = CodeAnalyzer()

# Analyze a file
issues, metrics = analyzer.analyze_file('example.py')

# Initialize AI reviewer
ai_reviewer = AIReviewer(api_key=config.openai.api_key)

# Generate AI review
with open('example.py', 'r') as f:
    content = f.read()

ai_review = ai_reviewer.review_code('example.py', content, issues, metrics)

print(f"Code Quality Score: {ai_review.overall_score}/10")
print(f"Summary: {ai_review.summary}")
```

## 🔒 Security Considerations

- **API Key Security**: Never commit your OpenAI API key to version control
- **File Access**: ReviewRabbit only reads files you specify
- **Network Usage**: AI reviews require internet connection for OpenAI API calls
- **Data Privacy**: Code content is sent to OpenAI for analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT models
- The Python community for excellent static analysis tools
- Contributors and users who help improve ReviewRabbit


---

**Made with ❤️ by the Isaac Tonyloi **
