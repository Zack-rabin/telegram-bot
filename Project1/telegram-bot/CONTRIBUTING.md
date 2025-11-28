# Contributing to Telegram Motivational Bot 🤝

Thank you for your interest in contributing! This document provides guidelines for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on the code, not the person
- Help others learn and grow

## How to Contribute

### Reporting Bugs 🐛

Found a bug? Please create an issue with:

1. **Title**: Clear, descriptive title
2. **Description**: What happened and what should happen
3. **Steps to Reproduce**: How to reproduce the issue
4. **Environment**: Python version, OS, bot version
5. **Screenshots**: If applicable

### Suggesting Features 💡

Have an idea? Open an issue with:

1. **Title**: Feature request - [brief description]
2. **Use Case**: Why you need this feature
3. **Proposed Solution**: How it should work
4. **Alternatives**: Other possible solutions

### Pull Requests 🔀

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes
4. **Test** your code
5. **Commit**: `git commit -m 'Add amazing feature'`
6. **Push**: `git push origin feature/amazing-feature`
7. **Open** a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/telegram-motivational-bot.git
cd telegram-motivational-bot

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # macOS/Linux

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Copy .env.example to .env and configure
cp .env.example .env
# Edit .env with your test bot token
```

## Coding Standards

### Style Guide
- Use Python PEP 8 style guide
- Run `black` to format code
- Use `flake8` for linting

```bash
# Format code
black telegram_bot.py

# Check code quality
flake8 telegram_bot.py
```

### Naming Conventions
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Comments and Docstrings
- Use docstrings for functions and classes
- Add comments for complex logic
- Keep comments up-to-date

```python
def send_daily_motivation(context):
    """
    Send daily motivational messages to subscribers.
    
    Args:
        context: APScheduler job context
        
    Returns:
        None
    """
```

## Testing

```bash
# Run tests
pytest

# Run specific test
pytest tests/test_bot.py::test_function_name

# Run with coverage
pytest --cov=telegram_bot
```

## Commit Messages

- Use present tense: "Add feature" not "Added feature"
- Be specific: "Add /subscribe command" not "Update code"
- Reference issues: "Fixes #123"

Examples:
```
Add daily motivation scheduling
Fix network reconnection bug
Update README with setup instructions
Refactor error handling in send_message
```

## Pull Request Process

1. **Update README** if needed
2. **Add tests** for new features
3. **Run linting**: `black` and `flake8`
4. **Pass all tests** before submitting
5. **Describe changes** clearly in PR description

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Tested locally
- [ ] Added tests

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No breaking changes
```

## Areas to Contribute

### Easy (Good for Beginners)
- Documentation improvements
- Bug fixes
- Code comments
- Error messages

### Medium
- New commands
- UI improvements
- Testing
- Refactoring

### Advanced
- Database integration
- Docker support
- Performance optimization
- Architecture improvements

## Review Process

1. **Maintainer Review**: Will review within 3-5 days
2. **Feedback**: Changes may be requested
3. **Approval**: Once approved, PR will be merged
4. **Thanks**: You'll be added to contributors!

## Questions?

- Open a GitHub Discussion
- Check existing issues
- Read the documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Happy contributing! 🎉
