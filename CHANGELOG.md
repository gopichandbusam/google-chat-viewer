# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-11-07

### 🚀 Added
- **Virtual Environment Management**: Complete setup with automated scripts
  - `setup.sh` - Automated environment setup and dependency installation
  - `start.sh` - One-command application startup with environment activation
  - `stop.sh` - Clean application shutdown with process management
- **Legal Disclaimers**: Comprehensive liability protection and user responsibility notices
  - In-app legal disclaimer with expandable warning section
  - Updated README with detailed legal responsibilities
  - Author disclaimer in code headers and documentation
- **Enhanced Project Structure**: Professional deployment-ready configuration
  - Updated requirements.txt with all necessary dependencies
  - Improved .gitignore with comprehensive exclusion patterns
  - VS Code configuration for virtual environment integration

## [2.0.0] - 2025-11-07

### 🚀 Added
- **Comprehensive Link Anonymization**: Support for all major web services
  - Google Workspace (Docs, Sheets, Slides, Drive, Meet, Calendar, etc.)
  - Development platforms (GitHub, GitLab, Stack Overflow, NPM, PyPI)
  - Communication tools (Slack, Discord, Zoom, Teams, WebEx)
  - File sharing (Dropbox, OneDrive, Box, iCloud)
  - Social media (LinkedIn, Twitter, Facebook, YouTube, Instagram)
  - Generic HTTP/HTTPS URLs, IP addresses, and file paths
- **Multi-Level Link Anonymization**: Domain-aware vs full anonymization modes
- **Enhanced Privacy Controls**: Granular control over what gets anonymized
- **Professional Documentation**: Comprehensive README with badges and examples
- **Open Source Licensing**: MIT License with contribution guidelines
- **Type Safety**: Complete type annotations throughout codebase
- **Performance Optimizations**: Better handling of large datasets with progress tracking

### 🔧 Improved  
- **Code Architecture**: Modular design with clear separation of concerns
- **Error Handling**: Comprehensive validation and graceful error recovery
- **User Interface**: Enhanced anonymization settings with better organization
- **Documentation**: Detailed docstrings and inline comments throughout
- **Configuration**: Centralized constants for easy maintenance
- **File Handling**: Robust file validation and temporary file cleanup

### 🛠️ Changed
- **Anonymization Engine**: Complete rewrite with pattern-based approach
- **Function Structure**: Split large functions into focused, reusable components  
- **UI Layout**: Reorganized anonymization interface for better user experience
- **Link Processing**: Unified link handling for all service types
- **Code Style**: Consistent formatting and naming conventions

### 📚 Documentation
- **README.md**: Complete rewrite with comprehensive feature documentation
- **CONTRIBUTING.md**: Detailed contribution guidelines and development setup
- **LICENSE**: MIT License for open source distribution
- **CHANGELOG.md**: Version history and change tracking
- **Code Comments**: Extensive documentation of complex logic

## [1.0.0] - 2025-11-06

### 🚀 Initial Release
- **Basic Chat Viewing**: Load and display Google Chat JSON exports
- **Name Anonymization**: Replace names with Person 1, Person 2, etc.
- **Email Anonymization**: Convert emails to person1@example.com format
- **Google Drive Link Anonymization**: Replace document IDs with placeholders
- **Custom Mappings**: User-defined text replacements
- **Statistics Dashboard**: Message counts and activity analytics
- **Export Functionality**: Save anonymized data
- **Multiple Anonymization Modes**: Automatic, Manual, and Mixed modes
- **Interactive UI**: Streamlit-based web interface
- **File Validation**: JSON format verification and error handling
- **Progress Tracking**: Visual feedback during processing
- **Pagination**: Efficient handling of large message sets

### 🛠️ Technical Features
- **Streamlit Framework**: Web-based user interface
- **JSON Processing**: Native Google Takeout format support
- **Regex Engine**: Pattern matching for text replacement
- **Session Management**: State persistence during app usage
- **Virtual Environment**: Automated dependency management
- **Error Recovery**: Graceful handling of malformed data

### 📋 Core Functionality
- **File Upload**: Drag-and-drop JSON file support
- **Data Parsing**: Extract messages, creators, and metadata
- **Text Processing**: Comprehensive content anonymization
- **Message Display**: Chat-like interface with timestamps
- **Attachment Handling**: Display file attachment information
- **Export Options**: Save processed data with user choice

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions  
- **PATCH** version for backwards-compatible bug fixes

## Types of Changes

- **🚀 Added** for new features
- **🔧 Improved** for enhancements to existing features
- **🛠️ Changed** for changes in existing functionality
- **🗑️ Deprecated** for soon-to-be removed features
- **🚫 Removed** for now removed features
- **🐛 Fixed** for bug fixes
- **🛡️ Security** for vulnerability fixes
- **📚 Documentation** for documentation changes