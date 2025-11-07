# Contributing to Google Chat Viewer

Thank you for considering contributing to Google Chat Viewer! 🎉

This document provides guidelines and information for contributing to this project.

## 🤝 Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow:

- **Be respectful** and inclusive to all community members
- **Use welcoming and inclusive language**
- **Focus on what is best for the community**
- **Be graceful in accepting constructive criticism**
- **Show empathy towards other community members**

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git for version control
- Basic knowledge of Python and Streamlit

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/google-chat-viewer.git
   cd google-chat-viewer
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Development Server**
   ```bash
   python run.py
   ```

## 🛠️ How to Contribute

### Reporting Bugs 🐛

Before creating a bug report:
- **Check existing issues** to avoid duplicates
- **Use the latest version** to ensure the bug still exists
- **Provide detailed information** about your environment

When creating a bug report, include:
- **Clear title** describing the issue
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **Screenshots** if applicable
- **System information** (OS, Python version, etc.)

### Suggesting Features 💡

We welcome feature suggestions! Please:
- **Check existing issues** for similar requests
- **Clearly describe** the feature and its benefits
- **Provide use cases** and examples
- **Consider implementation complexity**

### Submitting Changes 📝

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests if applicable
   - Update documentation

3. **Test Your Changes**
   ```bash
   # Test the application
   python run.py
   
   # Test with sample data
   # Ensure no regression in existing features
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## 📋 Development Guidelines

### Code Style

- **Follow PEP 8** Python style guidelines
- **Use type hints** for function parameters and return types
- **Write descriptive variable names** and function names
- **Add docstrings** to all functions and classes
- **Keep functions small** and focused on single responsibility

### Code Structure

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of parameter
        param2: Description of parameter
        
    Returns:
        bool: Description of return value
        
    Example:
        >>> function_name("hello", 42)
        True
    """
    # Implementation here
    pass
```

### Documentation

- **Update README.md** for significant changes
- **Add inline comments** for complex logic
- **Include examples** in docstrings
- **Update feature descriptions** when adding new functionality

### Testing

- **Test your changes** thoroughly before submitting
- **Test edge cases** and error conditions
- **Verify backwards compatibility** with existing features
- **Test with different file sizes** and formats

## 🎯 Areas for Contribution

### High Priority
- **🐛 Bug Fixes**: Help identify and fix issues
- **🔒 Privacy Features**: Enhance anonymization capabilities
- **📊 Analytics**: Add new statistics and insights
- **🎨 UI/UX**: Improve user interface and experience

### Medium Priority
- **📖 Documentation**: Improve guides and examples
- **🌐 Internationalization**: Add multi-language support
- **⚡ Performance**: Optimize for large datasets
- **🧪 Testing**: Add unit tests and integration tests

### Ideas for New Features
- **Sentiment Analysis**: Analyze chat sentiment over time
- **Word Clouds**: Generate visual word frequency displays
- **Export Formats**: PDF, CSV, and other output formats
- **Batch Processing**: Handle multiple chat files at once
- **Themes**: Customizable UI themes and colors
- **Advanced Filtering**: Filter messages by date, user, keywords
- **Data Visualization**: Charts and graphs for chat metrics
- **Plugin System**: Extensible architecture for custom features

## 📝 Pull Request Guidelines

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] Changes are tested and working
- [ ] Documentation is updated if needed
- [ ] Commit messages are clear and descriptive
- [ ] No merge conflicts with main branch

### PR Description Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
Describe how you tested your changes:
- [ ] Tested with sample data
- [ ] Verified no regression in existing features
- [ ] Tested edge cases

## Screenshots (if applicable)
Add screenshots for UI changes.

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have made corresponding changes to documentation
- [ ] My changes generate no new warnings
- [ ] I have tested my changes thoroughly
```

### Review Process

1. **Automated Checks**: Code style and basic validation
2. **Manual Review**: Functionality and code quality review
3. **Testing**: Verify changes work as expected
4. **Feedback**: Address any review comments
5. **Merge**: Approved changes are merged to main branch

## 🎖️ Recognition

Contributors will be:
- **Listed in README.md** acknowledgments section
- **Mentioned in release notes** for significant contributions
- **Given credit** in commit messages and documentation

## 📞 Getting Help

If you need help contributing:
- 💬 **Ask Questions**: Open a GitHub Discussion
- 📖 **Read Documentation**: Check existing docs and code comments
- 🤝 **Join Community**: Participate in discussions and issues
- 📧 **Contact Maintainers**: gopichand.busam@nyu.edu

## 🎉 Thank You!

Thank you for taking the time to contribute! Every contribution, no matter how small, helps make this project better for everyone.

Your efforts help:
- 🛡️ **Protect Privacy**: Better anonymization features
- 📊 **Improve Analytics**: More insights from chat data  
- 🎨 **Enhance UX**: Better user experience
- 🐛 **Fix Issues**: More stable and reliable software
- 📖 **Better Documentation**: Easier for others to contribute

Together, we're building a powerful, privacy-focused tool for chat data analysis! 🚀