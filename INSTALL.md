# ReviewRabbit - Installation and Setup Guide

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (for AI-powered reviews)
- Git (for cloning the repository)

## Installation Methods

### Method 1: From Source (Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/ReviewRabbit.git
cd ReviewRabbit
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install ReviewRabbit:**
```bash
pip install -e .
```

### Method 2: Using pip (when published)

```bash
pip install reviewrabbit
```

## Configuration Setup

1. **Set up your OpenAI API key:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

2. **Initialize configuration:**
```bash
reviewrabbit init
```

This creates a `config.yaml` file with default settings.

3. **Customize configuration (optional):**
Edit `config.yaml` to adjust analysis settings, file patterns, and output preferences.

## Quick Test

Test ReviewRabbit with the included sample code:

```bash
# Analyze the sample file
reviewrabbit analyze sample_code.py

# Generate AI review
reviewrabbit review sample_code.py --ai-review

# Export report
reviewrabbit export sample_code.py --format html
```

## Troubleshooting

### Common Issues

1. **"OpenAI API key is required" error:**
   - Make sure you've set the `OPENAI_API_KEY` environment variable
   - Or add it to your `config.yaml` file

2. **Import errors:**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **Permission errors:**
   - Make sure you have read access to the files you're analyzing
   - Check write permissions for report directory

### Getting Help

- Check the [README.md](README.md) for detailed usage instructions
- Review the [examples/](examples/) directory for code samples
- Open an issue on GitHub for bug reports or feature requests

## Next Steps

1. **Try analyzing your own code:**
```bash
reviewrabbit analyze path/to/your/project/
```

2. **Explore AI features:**
```bash
reviewrabbit review your_file.py --suggestions --test-cases
```

3. **Customize analysis:**
   - Edit `config.yaml` to enable/disable specific checks
   - Add custom file patterns for your project

4. **Integrate with CI/CD:**
   - Use ReviewRabbit in your build pipeline
   - Export reports for automated code quality checks
