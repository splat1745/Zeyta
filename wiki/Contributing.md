# 🤝 Contributing to Zeyta

Thank you for your interest in contributing to Zeyta! This guide will help you get started.

## 📋 Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Workflow](#contribution-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community Guidelines](#community-guidelines)

---

## 🎯 Ways to Contribute

There are many ways to contribute to Zeyta:

### 💻 Code Contributions

- **Bug Fixes** - Fix issues and improve stability
- **New Features** - Add new capabilities
- **Performance** - Optimize speed and efficiency
- **Integrations** - Create new integration modules
- **Testing** - Write and improve tests

### 📚 Documentation

- **Improve Guides** - Clarify existing documentation
- **Add Examples** - Show how to use features
- **Tutorials** - Create step-by-step walkthroughs
- **Translations** - Help translate documentation
- **Fix Typos** - Correct errors and improve clarity

### 🐛 Bug Reports

- Report issues you encounter
- Provide detailed reproduction steps
- Include system information
- Suggest possible solutions

### 💡 Feature Requests

- Propose new features
- Discuss use cases
- Provide implementation ideas
- Help prioritize features

### 🤗 Community Support

- Help answer questions
- Share your experience
- Participate in discussions
- Welcome new contributors

---

## 🚀 Getting Started

### Prerequisites

Before contributing, make sure you have:

- **Python 3.11+** installed
- **Git** installed and configured
- **GitHub account** created
- **Basic knowledge** of Python and Git

### Find an Issue

1. **Browse Issues**: Visit [GitHub Issues](https://github.com/relfayoumi/Zeyta/issues)
2. **Look for Labels**:
   - `good first issue` - Great for beginners
   - `help wanted` - Community help needed
   - `bug` - Bug fixes needed
   - `enhancement` - New features
   - `documentation` - Doc improvements

3. **Comment**: Express interest in working on the issue
4. **Get Assigned**: Wait for maintainer to assign you

### Communication

- **GitHub Issues**: For bugs and features
- **GitHub Discussions**: For questions and ideas
- **Pull Requests**: For code reviews

---

## 🛠️ Development Setup

### 1. Fork the Repository

```bash
# Click "Fork" button on GitHub
# Then clone your fork:
git clone https://github.com/YOUR_USERNAME/Zeyta.git
cd Zeyta
```

### 2. Add Upstream Remote

```bash
# Add original repository as upstream
git remote add upstream https://github.com/relfayoumi/Zeyta.git

# Verify remotes
git remote -v
# Should show:
# origin    https://github.com/YOUR_USERNAME/Zeyta.git (fetch)
# origin    https://github.com/YOUR_USERNAME/Zeyta.git (push)
# upstream  https://github.com/relfayoumi/Zeyta.git (fetch)
# upstream  https://github.com/relfayoumi/Zeyta.git (push)
```

### 3. Create Development Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (if any)
pip install pytest black flake8
```

### 4. Create Configuration

```bash
# Copy example configuration
cp config.example.py config.py

# Edit for your development setup
nano config.py
```

### 5. Verify Setup

```bash
# Run tests (if available)
pytest

# Try running Zeyta
python app.py

# Check imports
python -c "
from core import brain, context, controller
from IO import stt, tts
print('✅ All imports successful')
"
```

---

## 🔄 Contribution Workflow

### 1. Create a Branch

Always create a new branch for your work:

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes:
git checkout -b fix/issue-number-description
```

**Branch Naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `test/` - Tests
- `refactor/` - Code refactoring

### 2. Make Changes

```bash
# Edit files as needed
nano core/brain.py

# Check status
git status

# See changes
git diff
```

### 3. Test Your Changes

```bash
# Run existing tests
pytest

# Manual testing
python app.py
# Test your feature thoroughly

# Run specific tests
pytest tests/test_brain.py
```

### 4. Commit Changes

```bash
# Stage changes
git add core/brain.py

# Commit with clear message
git commit -m "Add feature: voice activity detection improvement

- Improved VAD sensitivity
- Reduced false positives
- Added configuration options

Fixes #123"
```

**Commit Message Format:**
```
<type>: <short description>

<detailed description>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Code refactoring
- `style:` - Code style (formatting)
- `perf:` - Performance improvement

### 5. Push to Your Fork

```bash
# Push to your fork
git push origin feature/your-feature-name
```

### 6. Create Pull Request

1. Go to your fork on GitHub
2. Click "Compare & pull request"
3. Fill in the PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Other (please describe)

## Testing
How you tested the changes

## Checklist
- [ ] Code follows project style
- [ ] Self-reviewed code
- [ ] Added comments for complex code
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Added tests (if applicable)
- [ ] All tests pass

## Related Issues
Fixes #123
Related to #456
```

4. Submit the PR

### 7. Code Review Process

**What to Expect:**

1. **Automated Checks**: CI/CD runs tests
2. **Maintainer Review**: Code review within 3-7 days
3. **Feedback**: Respond to comments and suggestions
4. **Updates**: Make requested changes
5. **Approval**: Once approved, PR is merged

**Responding to Feedback:**

```bash
# Make requested changes
nano core/brain.py

# Commit changes
git add core/brain.py
git commit -m "Address review feedback: improve error handling"

# Push updates
git push origin feature/your-feature-name
# PR automatically updates
```

### 8. After Merge

```bash
# Update your main branch
git checkout main
git pull upstream main

# Delete feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## 📝 Code Standards

### Python Style Guide

**Follow PEP 8:**

```python
# Good: Clear, readable code
def generate_response(messages: list, initial: bool = False) -> str:
    """
    Generate AI response from messages.
    
    Args:
        messages: List of conversation messages
        initial: Whether this is initial greeting
    
    Returns:
        Generated response text
    """
    if not messages:
        return ""
    
    gen_args = INITIAL_GEN_ARGS if initial else GENERATION_ARGS
    output = self.pipe(messages, **gen_args)
    return output[0]['generated_text']


# Bad: Unclear, cramped code
def gen(m,i=False):
    if not m:return ""
    g=INITIAL_GEN_ARGS if i else GENERATION_ARGS
    o=self.pipe(m,**g)
    return o[0]['generated_text']
```

### Code Formatting

```bash
# Use Black for formatting
black core/ IO/ utils/

# Check style with flake8
flake8 core/ IO/ utils/

# Fix common issues
autopep8 --in-place --aggressive core/brain.py
```

### Documentation

**Docstrings:**

```python
def my_function(param1: str, param2: int = 0) -> bool:
    """
    Brief description of function.
    
    Longer description explaining what the function does,
    how it works, and any important details.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter (default: 0)
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param2 is negative
        
    Example:
        >>> my_function("test", 5)
        True
    """
    if param2 < 0:
        raise ValueError("param2 must be non-negative")
    
    # Implementation
    return True
```

### Type Hints

```python
from typing import List, Dict, Optional, Tuple

def process_messages(
    messages: List[Dict[str, str]], 
    config: Optional[Dict[str, any]] = None
) -> Tuple[str, float]:
    """Process messages with optional config"""
    # Implementation
    return result, confidence
```

### Error Handling

```python
# Good: Specific exception handling
try:
    result = risky_operation()
except FileNotFoundError as e:
    logging.error(f"File not found: {e}")
    return default_value
except PermissionError as e:
    logging.error(f"Permission denied: {e}")
    raise

# Bad: Catching all exceptions
try:
    result = risky_operation()
except:  # Too broad!
    pass  # Silent failure!
```

### Logging

```python
import logging

# Good: Informative logging
logging.info("Loading model: {LLM_MODEL_ID}")
logging.debug(f"Generation args: {gen_args}")
logging.warning("CUDA not available, using CPU")
logging.error(f"Failed to load model: {e}")

# Bad: Print statements
print("Loading model")  # Use logging instead
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_brain.py

# Run with coverage
pytest --cov=core --cov=IO

# Run with verbose output
pytest -v

# Run only failed tests
pytest --lf
```

### Writing Tests

```python
# tests/test_brain.py

import pytest
from core.brain import Brain
from core.context import ContextManager

def test_brain_initialization():
    """Test Brain initializes correctly"""
    context = ContextManager("Test prompt")
    brain = Brain(context_manager=context)
    
    assert brain.pipe is not None
    assert brain.context_manager is context

def test_generate_response():
    """Test response generation"""
    context = ContextManager("You are helpful")
    brain = Brain(context_manager=context)
    
    messages = [
        {"role": "user", "content": "Hello"}
    ]
    
    response = brain.generate_response(messages)
    
    assert response is not None
    assert len(response) > 0
    assert isinstance(response, str)

def test_error_handling():
    """Test error handling"""
    brain = Brain()
    
    # Test with invalid messages
    with pytest.raises(ValueError):
        brain.generate_response(None)
```

### Test Structure

```
tests/
├── __init__.py
├── test_brain.py           # Brain module tests
├── test_context.py         # Context manager tests
├── test_controller.py      # Controller tests
├── test_stt.py            # STT tests
├── test_tts.py            # TTS tests
└── test_integrations.py   # Integration tests
```

---

## 📖 Documentation

### Documentation Standards

**Update Documentation When:**
- Adding new features
- Changing existing behavior
- Fixing bugs that affect usage
- Adding configuration options

**Documentation Locations:**
- `README.md` - Project overview
- `wiki/` - Comprehensive guides
- Code docstrings - API documentation
- `docs/` - Additional documentation

### Writing Good Documentation

**Be Clear and Concise:**

```markdown
# Good
## Installing FFmpeg

FFmpeg is required for audio processing.

**Windows:**
```bash
choco install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

# Bad
## FFmpeg

You need to install FFmpeg because it's used for audio stuff.
Just download it from somewhere and install it.
```

**Include Examples:**

```markdown
# Good
### Using Voice Cloning

Configure your reference audio:

```python
TTS_BACKEND = "coqui"
COQUI_REFERENCE_WAV = "my_voice.wav"
```

Then test:

```bash
python testing/test_tts_clean.py
```

# Bad
### Voice Cloning

Configure TTS settings and test it.
```

---

## 👥 Community Guidelines

### Code of Conduct

**Be Respectful:**
- Treat everyone with respect
- Welcome diverse perspectives
- Be constructive in criticism
- Help create a positive environment

**Be Collaborative:**
- Share knowledge freely
- Help others learn
- Give credit where due
- Work together on solutions

**Be Professional:**
- Keep discussions on-topic
- Avoid personal attacks
- Respect maintainer decisions
- Follow project guidelines

### Getting Help

**Before Asking:**
1. Check existing documentation
2. Search closed issues
3. Try troubleshooting steps
4. Prepare minimal reproduction

**When Asking:**
1. Be specific about the problem
2. Include relevant details
3. Show what you've tried
4. Be patient for responses

---

## 🎓 Learning Resources

### Understanding the Codebase

1. **Start with README**: [README.md](../README.md)
2. **Read Architecture**: [Architecture](Architecture.md)
3. **Study Core Modules**: [Core Modules](Core-Modules.md)
4. **Explore Examples**: `/examples` directory

### Python Resources

- [Python Documentation](https://docs.python.org/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Git Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Writing Good Commits](https://chris.beams.io/posts/git-commit/)

---

## 🏆 Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes
- Project documentation

**Significant contributions may lead to:**
- Collaborator status
- Maintainer role
- Project steering

---

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/relfayoumi/Zeyta/issues)
- **Discussions**: [GitHub Discussions](https://github.com/relfayoumi/Zeyta/discussions)
- **Email**: See GitHub profile

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

<div align="center">

**[⬆️ Back to Top](#-contributing-to-zeyta)** | **[🏠 Home](Home.md)**

**Thank you for contributing to Zeyta! 🎉**

</div>
