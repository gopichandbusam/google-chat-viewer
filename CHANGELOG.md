# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.4.0] - 2025-12-02

### ⚡ Performance
- **Optimized Anonymization Engine**: Implemented pre-compiled regex patterns and efficient looping, significantly reducing processing time for large datasets.
- **Faster Data Handling**: Switched to optimized object copying methods for better memory usage and speed.

### 🛠️ Refactoring
- **Modular Architecture**: Moved core parsing and mapping logic (`parse_chat_message`, `compile_mappings`) to `ui.py` to resolve circular dependencies and improve code organization.
- **Clean Imports**: Streamlined import statements across the application.

### 🐛 Fixed
- **Session State Warning**: Resolved Streamlit widget warning in the Quick Anonymization panel by decoupling widget values from session state.

## [2.3.0] - 2025-11-14

### 🚀 Added
- **Bulk Import Interface**: Paste key-value pairs (e.g., "Name=Alias") to create multiple mappings at once.
- **Smart Quick Anonymization**: Auto-generates initials (e.g., "John Doe" -> "J.D.") and domain-based email replacements.
- **Duplicate Detection**: Warns users if a mapping for a specific name or email already exists.
- **Collapsible Data Preview**: Anonymized JSON preview is now hidden by default in an expander to reduce clutter.

### 🛠️ Changed
- **UI Refinements**: Improved layout for mapping tools and preview sections.

## [2.1.0] - 2025-11-07

## [2.2.0] - 2025-11-13

### 🚀 Added
- **Quick Anonymization Panel**: Create name and email replacements directly from participant statistics
- **Always-On Download Button**: Export anonymized data immediately after processing
- **File Insight Messaging**: Display absolute path for local files and size/source details for uploads
- **Session Clear Control**: One-click button to clear session state and cached data

### 🛠️ Changed
- **Manual-Only Anonymization**: Removed automatic and mixed modes to simplify workflow and improve predictability
- **Email Coverage**: Ensured creator, quoted-message, reaction, and inline text emails honor custom mappings
- **Documentation Refresh**: Updated README and guidance to reflect new UX and manual-first approach

### 🐛 Fixed
- **Email Display in Statistics**: Anonymized names now map back to original emails for correct column display
- **Uploaded File Handling**: Resolved errors when using non-filesystem `UploadedFile` objects during save operations

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