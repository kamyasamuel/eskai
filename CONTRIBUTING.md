# Contributing to ESKAI

Thank you for your interest in contributing to ESKAI! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Development Setup

1. **Fork and clone the repository:**
```bash
git clone https://github.com/yourusername/eskai.git
cd eskai
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install development dependencies:**
```bash
pip install -r requirements.txt
pip install -e .[dev]
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys for testing
```

5. **Run tests to verify setup:**
```bash
pytest
```

## 📋 How to Contribute

### 1. Find or Create an Issue
- Check existing [issues](https://github.com/kamyasamuel/eskai/issues)
- Create a new issue for bugs or feature requests
- Comment on issues you'd like to work on

### 2. Development Workflow

1. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**
- Follow the coding standards (see below)
- Add tests for new functionality
- Update documentation if needed

3. **Test your changes:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=eskai

# Run linting
flake8 eskai/
black --check eskai/
mypy eskai/
```

4. **Commit and push:**
```bash
git add .
git commit -m "feat: add new feature description"
git push origin feature/your-feature-name
```

5. **Create a Pull Request:**
- Use the PR template
- Link to related issues
- Provide clear description of changes

## 🎨 Coding Standards

### Code Style
- Use [Black](https://github.com/psf/black) for code formatting
- Follow [PEP 8](https://pep8.org/) guidelines
- Use type hints where appropriate
- Maximum line length: 88 characters (Black default)

### Naming Conventions
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_private_method`

### Documentation
- Use docstrings for all public classes and methods
- Follow Google-style docstrings
- Update README.md for significant changes
- Add inline comments for complex logic

### Example:
```python
class ExampleClass:
    """
    Brief description of the class.
    
    Longer description with more details about the class purpose
    and usage patterns.
    """
    
    def __init__(self, param: str):
        """
        Initialize the class.
        
        Args:
            param: Description of the parameter
        """
        self.param = param
    
    def example_method(self, input_data: Dict[str, Any]) -> str:
        """
        Example method with proper documentation.
        
        Args:
            input_data: Dictionary containing input parameters
            
        Returns:
            Processed result as string
            
        Raises:
            ValueError: If input_data is invalid
        """
        if not input_data:
            raise ValueError("input_data cannot be empty")
        
        # Process the data
        result = self._process_data(input_data)
        return result
    
    def _process_data(self, data: Dict[str, Any]) -> str:
        """Private method for data processing."""
        return str(data)
```

## 🧪 Testing Guidelines

### Test Structure
- Tests are located in the `tests/` directory
- Mirror the package structure: `tests/test_core/test_layer1.py`
- Use descriptive test names: `test_layer1_classifies_chat_intent_correctly`

### Writing Tests
- Use pytest framework
- Mock external dependencies (API calls, file system, etc.)
- Test both success and failure cases
- Aim for high test coverage (>80%)

### Test Categories
- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows

### Example Test:
```python
def test_prompt_assessor_chat_classification():
    """Test that PromptAssessor correctly identifies chat prompts."""
    # Arrange
    assessor = PromptAssessor(mock_provider_manager, test_config)
    chat_prompt = "Hello, how are you?"
    
    # Act
    result = assessor.assess_intent(chat_prompt)
    
    # Assert
    assert result["intent"] == "chat"
    assert result["confidence"] > 0.7
    assert "reasoning" in result
```

## 📚 Documentation

### Types of Documentation
1. **Code Documentation**: Docstrings and inline comments
2. **API Documentation**: Auto-generated from docstrings
3. **User Documentation**: README, examples, tutorials
4. **Architecture Documentation**: Design decisions and patterns

### Documentation Standards
- Keep documentation up-to-date with code changes
- Use clear, concise language
- Provide practical examples
- Include troubleshooting information

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information:**
   - Python version
   - ESKAI version
   - Operating system
   - AI provider APIs being used

2. **Reproduction Steps:**
   - Minimal code example
   - Input that causes the issue
   - Expected vs actual behavior

3. **Error Information:**
   - Full error traceback
   - Log files (if applicable)
   - Configuration details (anonymized)

## 💡 Feature Requests

For feature requests, please provide:

1. **Problem Description:** What problem does this solve?
2. **Proposed Solution:** How should it work?
3. **Use Cases:** When would this be useful?
4. **Alternatives:** What alternatives exist?
5. **Implementation Ideas:** Any technical suggestions?

## 🏷️ Commit Message Guidelines

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples:
```
feat(layer1): add confidence scoring for intent classification
fix(providers): handle API timeout errors gracefully
docs(readme): update installation instructions
test(core): add tests for objective formulation
```

## 🏆 Recognition

Contributors will be:
- Listed in the project's contributors section
- Mentioned in release notes for significant contributions
- Invited to join the maintainer team for outstanding contributions

## 📞 Getting Help

- **Questions:** Open a [discussion](https://github.com/kamyasamuel/eskai/discussions)
- **Chat:** Join our [Discord server](https://discord.gg/eskai)
- **Issues:** Use [GitHub Issues](https://github.com/kamyasamuel/eskai/issues)

## 📋 Code of Conduct

We are committed to fostering a welcoming community. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) for details on our community standards.

## 📄 License

By contributing to ESKAI, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to ESKAI! 🎉
