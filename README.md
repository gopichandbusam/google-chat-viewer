# 💬 Google Chat Viewer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)

*Created by Gopichand Busam* ✨

A comprehensive, open-source Streamlit application for viewing, analyzing, and anonymizing Google Chat data from JSON exports. Perfect for data analysis, privacy protection, and sharing sanitized chat histories.

## 🚀 Features

### � **Data Analysis & Visualization**
- **Smart File Upload**: Drag-and-drop JSON files with validation and error handling
- **Comprehensive Statistics**: Detailed analytics with message counts, activity patterns, and participation metrics
- **Interactive Chat Interface**: View messages in a beautiful, paginated chat-like format
- **Attachment Support**: Display and analyze attached file information
- **Date Range Analysis**: Explore conversation timeframes and activity patterns

### 🔒 **Advanced Privacy Protection**
- **Multi-Level Anonymization**: Automatic, Manual, and Mixed anonymization modes
- **Name & Identity Protection**: Replace names with Person 1, Person 2, etc. or custom mappings
- **Email Anonymization**: Convert emails to person1@example.com, person2@example.com
- **Comprehensive Link Anonymization**: 
  - Google Services (Docs, Sheets, Drive, Meet, Calendar, etc.)
  - Development platforms (GitHub, GitLab, Stack Overflow, etc.)
  - Communication tools (Slack, Discord, Zoom, Teams, etc.)
  - File sharing (Dropbox, OneDrive, Box, iCloud, etc.)
  - Social media (LinkedIn, Twitter, Facebook, YouTube, etc.)
  - Generic HTTP/HTTPS URLs, IP addresses, file paths
- **Company & Project Protection**: Anonymize organization names and project identifiers
- **Attachment Anonymization**: Sanitize filenames and metadata

### 🛠️ **Technical Features**
- **Performance Optimized**: Handle large chat histories (200MB+ files) efficiently
- **Progress Tracking**: Visual feedback during processing with progress bars  
- **Export Options**: Save anonymized data in JSON format for sharing
- **Error Handling**: Robust validation with helpful error messages and recovery
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- macOS, Linux, or Windows with bash support

### Installation & Setup

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd google-chat-viewer
   ```

2. **Set up virtual environment and install dependencies**:
   ```bash
   ./setup.sh
   ```
   This script will:
   - Create a Python virtual environment in `venv/`
   - Install all required dependencies
   - Set up the project for first use

3. **Start the application**:
   ```bash
   ./start.sh
   ```
   This will:
   - Activate the virtual environment
   - Launch the Streamlit application
   - Open your browser to `http://localhost:8501`

4. **Stop the application**:
   ```bash
   ./stop.sh
   ```
   Or press `Ctrl+C` in the terminal where it's running

5. **Upload your file**: Use the web interface to upload your Google Chat JSON file

6. **View your data**: Browse through your chat messages in a clean interface

### Manual Installation (Alternative)

If you prefer manual setup:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

## What you need

- **Python 3.8+**
- **Google Chat JSON export** (from Google Takeout)

## 📥 Getting Your Chat Data from Google Takeout

**Important**: If you are not an administrator, you can only export your own data using Google Takeout.

### Step-by-Step Instructions:

1. 🌐 **Go to [takeout.google.com](https://takeout.google.com)**
2. 🔄 **Click "Deselect all"** 
3. 📱 **Scroll down and check the box for "Chat"**
4. ➡️ **Click "Next step"**
5. 📧 **Choose your delivery method** (e.g., email link) and file type (leave as .zip)
6. ✅ **Click "Create export"**

### What You'll Receive:
- A ZIP file containing your chat history in JSON format
- Extract the ZIP file and look for `messages.json`
- This is the file you'll upload to the Google Chat Viewer

### 📖 Need More Help?
For detailed instructions, visit the [Google Takeout Tutorial](https://support.google.com/accounts/answer/3024190)

## 🎭 Using Custom Name Mappings

The anonymization feature provides a powerful way to protect privacy:

### **How to Add Custom Mappings:**
1. **Enable anonymization** in the app
2. **Expand "Custom Name Mappings"** section
3. **Add mappings** using the table interface:
   - Enter original text (e.g., "Gopichand Busam")
   - Enter replacement (e.g., "Manager")
   - Click "Add"

### **What Gets Replaced:**
- ✅ **Sender names** in chat messages
- ✅ **Names within message text** (e.g., "Hey Gopichand, how are you?")
- ✅ **Quoted message content**
- ✅ **Attachment file names**
- ✅ **Company names, project names, any text**

### **Examples of Useful Mappings:**
```
Original Text          →  Replacement
Gopichand Busam       →  Manager
John Smith            →  Developer
Acme Corporation      →  Company A
Project Phoenix       →  Project X
confidential-data.pdf →  document.pdf
```

### **Smart Matching:**
The app uses intelligent pattern matching:
- **Word boundaries**: "John" won't replace "Johnson"
- **Case insensitive**: Matches "john", "John", "JOHN"
- **Punctuation aware**: Handles "John," and "John!" correctly
- **Multi-word support**: "John Smith" replaces the full name

## File Structure

```
google-chat-viewer/
├── app.py           # Main application
├── run.py          # Setup and launch script
├── requirements.txt # Dependencies
├── README.md       # This file
└── venv/          # Virtual environment (created automatically)
```

## Manual Setup (Optional)

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies  
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## 🎯 Advanced Features

### 🔒 Advanced Data Anonymization

### **Multi-Mode Anonymization System**
- **🤖 Automatic Mode**: Auto-generate all replacements (Person 1, person1@example.com, [GITHUB_LINK])
- **✋ Manual Mode**: Only anonymize what you specify with custom mappings
- **🔀 Mixed Mode**: Combine automatic generation with custom replacements

### **Comprehensive Content Protection**
- **Names & Identity**: Replace in sender fields AND message content using smart pattern matching
- **Email Addresses**: Full email anonymization with domain preservation options
- **Link & URL Anonymization**: 
  - **Google Workspace**: Docs, Sheets, Slides, Drive, Meet, Calendar → [DOCS_LINK], [SHEETS_LINK], etc.
  - **Development**: GitHub, GitLab, Stack Overflow, NPM, PyPI → [GITHUB_LINK], [GITLAB_LINK], etc.
  - **Communication**: Slack, Discord, Zoom, Teams → [SLACK_LINK], [DISCORD_LINK], etc.
  - **File Sharing**: Dropbox, OneDrive, Box, iCloud → [DROPBOX_LINK], [ONEDRIVE_LINK], etc.
  - **Social Media**: LinkedIn, Twitter, Facebook, YouTube → [LINKEDIN_LINK], [TWITTER_LINK], etc.
  - **Generic URLs**: All HTTP/HTTPS links, IP addresses, file paths
- **File & Network Paths**: Anonymize file paths, network shares, and attachment names
- **Company & Projects**: Replace organization names and sensitive project identifiers

### **Advanced Anonymization Features**
- **Interactive Mapping Interface**: User-friendly table for adding/removing custom mappings
- **Smart Pattern Matching**: Multiple strategies (word boundaries, punctuation-aware, exact match)
- **Live Preview**: Test anonymization with sample text before processing
- **Anonymization Levels**: Choose between domain-aware ([GITHUB_LINK]) or full anonymization ([LINK])
- **Comprehensive Coverage**: Processes main messages, quoted content, and attachments
- **Export Options**: Save anonymized data while preserving originals

### 📊 Comprehensive Analytics
- **Message Statistics**: See who sent how many messages
- **Activity Patterns**: Find the most active days and participants
- **Date Ranges**: View conversation timeframes
- **Participation Metrics**: Detailed breakdown of chat activity

### 💬 Enhanced Chat Display
- **Pagination**: Handle large chat histories smoothly
- **Rich Formatting**: Support for attachments, reactions, and quotes
- **Error Handling**: Graceful handling of corrupted or invalid data
- **Progress Tracking**: Visual feedback during processing

### 🛡️ Data Safety
- **Local Processing**: All data stays on your computer
- **Temporary File Cleanup**: Automatic cleanup of uploaded files
- **Validation**: Comprehensive file format validation
- **Privacy First**: Optional anonymization for data sharing

## Troubleshooting

**Problem**: "No module named streamlit"
**Solution**: Run `python3 run.py` which handles setup automatically

**Problem**: Can't find JSON file
**Solution**: Use the upload button in the web interface

**Problem**: Permission errors
**Solution**: Make sure you have write permissions in the current directory

## 🤝 Contributing

We welcome contributions! This project is open source and community-driven.

### **How to Contribute**

1. **🍴 Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/google-chat-viewer.git
   cd google-chat-viewer
   ```

2. **🌿 Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

3. **🔧 Make Your Changes**
   - Add new features
   - Fix bugs
   - Improve documentation
   - Add tests

4. **✅ Test Your Changes**
   ```bash
   python run.py
   # Test with sample data
   ```

5. **📝 Commit and Push**
   ```bash
   git add .
   git commit -m "Add amazing new feature"
   git push origin feature/amazing-new-feature
   ```

6. **🔄 Create a Pull Request**
   - Open a PR with a clear description
   - Include screenshots for UI changes
   - Reference any related issues

### **Areas We Need Help With**
- 🌐 **Internationalization**: Multi-language support
- 🎨 **UI/UX Improvements**: Better design and user experience  
- 🔧 **New Anonymization Features**: Additional privacy protection methods
- 📊 **Analytics Features**: More detailed statistics and insights
- 🐛 **Bug Fixes**: Help us squash bugs and improve stability
- 📖 **Documentation**: Improve guides, examples, and API docs
- 🧪 **Testing**: Unit tests, integration tests, and test coverage

### **Development Setup**

```bash
# Clone the repository
git clone https://github.com/yourusername/google-chat-viewer.git
cd google-chat-viewer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Run in development mode
streamlit run app.py --server.runOnSave true
```

---

## ⚠️ Legal Disclaimer

**IMPORTANT: READ BEFORE USE**

### Data Responsibility
- **User Responsibility**: Users are solely responsible for ensuring they have proper authorization to process any chat data
- **Privacy Compliance**: Users must comply with all applicable privacy laws (GDPR, CCPA, etc.) when processing personal data
- **Data Security**: Users are responsible for securing their data during processing and storage
- **Consent**: Ensure you have proper consent from all parties whose data appears in your chat exports

### Limitation of Liability
- **No Warranty**: This software is provided "AS IS" without any warranty of any kind
- **Author Disclaimer**: The author takes NO responsibility for:
  - Data breaches or privacy violations
  - Legal consequences of data processing
  - Compliance with local or international laws
  - Loss or corruption of data
  - Misuse of the software

### Best Practices
- Only process chat data you are legally authorized to access
- Anonymize data when sharing or distributing
- Delete processed files when no longer needed
- Use in secure, private environments only
- Review and comply with your organization's data policies

**By using this software, you acknowledge and accept full responsibility for legal compliance and data security.**

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### **MIT License Summary**
- ✅ **Commercial use** - Use in commercial projects
- ✅ **Modification** - Modify and distribute
- ✅ **Distribution** - Share with others
- ✅ **Private use** - Use for personal projects
- ❌ **Liability** - No warranty provided
- ❌ **Warranty** - Use at your own risk

## 📞 Support & Community

### **Getting Help**
- 📖 **Documentation**: Check this README and in-app help
- 🐛 **Bug Reports**: [Open an issue](https://github.com/yourusername/google-chat-viewer/issues)
- 💡 **Feature Requests**: [Request a feature](https://github.com/yourusername/google-chat-viewer/issues)
- 🤔 **Questions**: [Start a discussion](https://github.com/yourusername/google-chat-viewer/discussions)

### **Project Stats**
- 🌟 **Stars**: Help us grow by starring the repository
- 🍴 **Forks**: Fork to contribute or customize
- 🐛 **Issues**: Report bugs or request features
- 👥 **Contributors**: Join our growing community

## 🙏 Acknowledgments

- **Streamlit Team** - For the amazing web app framework
- **Google** - For Google Takeout and Chat export capabilities
- **Open Source Community** - For inspiration and contributions
- **Contributors** - Thank you to everyone who helps improve this project

## 🔮 Roadmap

### **Upcoming Features**
- 📱 **Mobile Optimization**: Better mobile device support
- 🌐 **Multi-Language Support**: Internationalization (i18n)
- 📊 **Advanced Analytics**: Sentiment analysis, word clouds, activity heatmaps
- 🔄 **Batch Processing**: Handle multiple chat exports simultaneously
- 🔌 **Plugin System**: Extensible architecture for custom features
- 💾 **Database Support**: Store and query large chat histories
- 🎨 **Themes**: Customizable UI themes and styling
- 📤 **Export Formats**: PDF, CSV, and other export options

### **Long-term Goals**
- 🤖 **AI Integration**: Smart categorization and insights
- 🔒 **Enterprise Features**: Advanced security and compliance features
- ☁️ **Cloud Deployment**: Easy cloud hosting options
- 📈 **Real-time Processing**: Live chat analysis capabilities

---

⭐ **If you find this project helpful, please consider giving it a star!** ⭐