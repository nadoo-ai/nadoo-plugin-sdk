# Contributing to nadoo-plugin-sdk

Thank you for your interest in contributing to nadoo-plugin-sdk! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Plugin Development Guidelines](#plugin-development-guidelines)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up your development environment
4. Create a new branch for your changes
5. Make your changes
6. Test your changes
7. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Poetry (recommended) or pip
- git

### Setup with Poetry (Recommended)

```bash
# Install Poetry if you haven't
curl -sSL https://install.python-poetry.org | python3 -

# Clone your fork
git clone https://github.com/YOUR_USERNAME/nadoo-plugin-sdk.git
cd nadoo-plugin-sdk

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Setup with pip

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/nadoo-plugin-sdk.git
cd nadoo-plugin-sdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Verify Installation

```bash
# Check CLI is working
nadoo-plugin --version

# Run tests
pytest

# Or with Poetry
poetry run pytest
```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-decorator` - for new features
- `fix/validation-bug` - for bug fixes
- `docs/update-api-reference` - for documentation
- `test/add-cli-tests` - for tests
- `refactor/simplify-loader` - for refactoring

### Commit Messages

Follow conventional commits:
```
feat: add @async_tool decorator
fix: resolve plugin loading race condition
docs: update quick start guide
test: add tests for parameter validation
refactor: simplify plugin context API
chore: update dependencies
```

## Code Style

We use automated tools to maintain code quality:

### Formatting with Black

```bash
# Format code
poetry run black .

# Check formatting
poetry run black --check .
```

### Import Sorting with isort

```bash
# Sort imports
poetry run isort .

# Check import order
poetry run isort --check-only .
```

### Linting with Flake8

```bash
# Run linter
poetry run flake8 nadoo_plugin tests
```

### Type Checking with mypy

```bash
# Type check
poetry run mypy nadoo_plugin
```

### Run All Checks

```bash
# Run all quality checks at once
poetry run black --check . && \
poetry run isort --check-only . && \
poetry run flake8 nadoo_plugin tests && \
poetry run mypy nadoo_plugin
```

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=nadoo_plugin --cov-report=html

# Run specific test file
poetry run pytest tests/test_decorators.py

# Run specific test
poetry run pytest tests/test_decorators.py::test_tool_decorator

# Run with verbose output
poetry run pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Aim for high coverage of new code

Example:
```python
import pytest
from nadoo_plugin import tool, parameter

def test_tool_decorator():
    """Test that @tool decorator works correctly"""
    @tool(name="test_tool", description="Test tool")
    @parameter("input", type="string", required=True)
    def my_tool(input: str) -> dict:
        return {"result": input.upper()}

    assert hasattr(my_tool, "_nadoo_tool")
    assert my_tool._nadoo_tool.name == "test_tool"
```

### Testing CLI Commands

```bash
# Test plugin creation
poetry run nadoo-plugin create test-plugin --output /tmp

# Test plugin building
cd examples/hello-world
poetry run nadoo-plugin build

# Test plugin testing
poetry run nadoo-plugin test --tool greet --params '{"name": "World"}'
```

## Submitting Changes

### Pull Request Process

1. **Update your branch**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Run all checks**
   ```bash
   poetry run black .
   poetry run isort .
   poetry run flake8 nadoo_plugin tests
   poetry run mypy nadoo_plugin
   poetry run pytest
   ```

3. **Push to your fork**
   ```bash
   git push origin your-branch
   ```

4. **Create Pull Request**
   - Go to GitHub and create a PR
   - Fill out the PR template
   - Link any related issues

### PR Requirements

- ✅ All tests pass
- ✅ Code is formatted (Black)
- ✅ Imports are sorted (isort)
- ✅ No linting errors (Flake8)
- ✅ Type checks pass (mypy)
- ✅ New code has tests
- ✅ Documentation is updated
- ✅ CHANGELOG.md is updated (for significant changes)

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] New decorator
- [ ] CLI improvement

## Related Issues
Fixes #123

## Testing
How was this tested?

## Checklist
- [ ] Tests pass
- [ ] Code formatted (Black)
- [ ] Imports sorted (isort)
- [ ] No lint errors (Flake8)
- [ ] Type checks pass (mypy)
- [ ] Documentation updated
- [ ] CHANGELOG updated
```

## Plugin Development Guidelines

### Best Practices

1. **Use Type Hints**
   ```python
   from typing import Dict, Any

   def my_tool(input: str) -> Dict[str, Any]:
       return {"result": input}
   ```

2. **Validate Inputs**
   ```python
   @parameter("count", type="integer", min=1, max=100)
   def process(count: int) -> dict:
       if not isinstance(count, int):
           raise ValueError("Count must be an integer")
       # ...
   ```

3. **Handle Errors Gracefully**
   ```python
   def my_tool(url: str) -> dict:
       try:
           response = requests.get(url)
           response.raise_for_status()
           return {"data": response.json()}
       except requests.RequestException as e:
           self.context.log_error(f"Request failed: {e}")
           return {"error": str(e)}
   ```

4. **Use Context Logging**
   ```python
   def on_initialize(self):
       self.context.log("Plugin initialized")
       self.context.log_debug("Debug information")
       self.context.log_error("Error occurred")
   ```

5. **Document Your Tools**
   ```python
   @tool(
       name="summarize_text",
       description="Summarize text using AI with customizable length"
   )
   @parameter("text", type="string", required=True,
              description="Text to summarize")
   @parameter("max_length", type="integer", default=100,
              description="Maximum length of summary")
   def summarize(self, text: str, max_length: int = 100) -> dict:
       """
       Summarize the provided text.

       Args:
           text: Input text to summarize
           max_length: Maximum summary length in words

       Returns:
           dict: Contains 'summary' and 'word_count'
       """
       # ...
   ```

## Development Workflow

### Adding a New Decorator

1. Add decorator to `nadoo_plugin/decorators.py`
2. Add tests to `tests/test_decorators.py`
3. Update documentation
4. Add example usage

### Adding a New CLI Command

1. Add command to `nadoo_plugin/cli/`
2. Register in `cli/main.py`
3. Add tests
4. Update CLI documentation

### Improving Plugin Loader

1. Modify `nadoo_plugin/loader.py`
2. Add comprehensive tests
3. Ensure backward compatibility
4. Update migration guide if breaking

## Questions?

- Open a [GitHub Discussion](https://github.com/nadoo-ai/nadoo-plugin-sdk/discussions)
- Check existing [Issues](https://github.com/nadoo-ai/nadoo-plugin-sdk/issues)
- Email: dev@nadoo.ai

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉
