# 💬 Google Chat Viewer & Anonymization

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)

*Created by Gopichand Busam* ✨

A comprehensive, open-source Streamlit application for viewing, analyzing, and anonymizing Google Chat data from JSON exports. Perfect for data analysis, privacy protection, and sharing sanitized chat histories.

## 🚀 Features

### 📊 Data Analysis & Visualization
- **Flexible File Intake**: Upload from browser or pick local files with instant validation and helpful path/size info
- **Comprehensive Statistics**: Message counts, participation breakdown, activity ranges, and most-active-day insights
- **Quick Anonymization Dashboard**: Smart auto-suggestions for initials and emails directly from the participant list
- **Chat-Style Viewer**: Paginated message stream with quotes, reactions, and attachment highlights
- **High-Performance Processing**: Optimized engine with pre-compiled patterns handles large Google Takeout exports efficiently

### 🔒 Privacy Controls
- **Manual-First Anonymization**: You decide exactly what gets replaced via custom mappings and quick-add shortcuts
- **Bulk Import**: Paste key-value pairs to create multiple mappings instantly
- **Email Coverage Everywhere**: Creator fields, quoted messages, reactions, and message text all respect your mappings
- **Link Scrubbing**: Domain-aware or fully generic link anonymization to remove sensitive URLs
- **Filename Sanitizing**: Attachments and embedded references are cleaned alongside message content
- **Download-Ready Output**: One-click download button and optional same-folder save keep exports under your control
- **Collapsible Preview**: Inspect your anonymized JSON data without cluttering the interface

### 🧰 Productivity Enhancements
- **Session Reset Button**: Clear memory and cached data instantly when switching files or starting fresh
- **Duplicate Mapping Guardrails**: Automatic warnings when the same original or replacement is added twice
- **Progress Feedback**: Spinners and status messages during parsing, statistics, and anonymization steps
- **Error Guidance**: Friendly messaging for malformed JSON, missing fields, or encoding issues
- **Cross-Platform Support**: Runs consistently on macOS, Windows, and Linux with Streamlit 1.28+

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- macOS, Linux, or Windows with bash support

### Installation & Setup

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/gopichandbusam/google-chat-viewer.git
   cd google-chat-viewer
   ```

2. **Set up virtual environment and install dependencies** (choose one):
   - **Automatic:**
     ```bash
     ./setup.sh
     ```
     This script creates a Python virtual environment in `venv/`, installs dependencies, and sets up the project.
   - **Manual:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     pip install -r requirements.txt
     ```

3. **Start the application**:
   - With script:
     ```bash
     ./start.sh
     ```
   - Or manually:
     ```bash
     streamlit run app.py
     ```

4. **Stop the application**:
   ```bash
   ./stop.sh
   ```
   Or press `Ctrl+C` in the terminal where it's running

5. **Upload your file**: Use the web interface to upload your Google Chat JSON file

6. **View your data**: Browse through your chat messages in a clean interface

#### File Structure
```
google-chat-viewer/
├── app.py           # Main application
├── ui.py            # UI components and layout
├── run.py           # Setup and launch script
├── requirements.txt # Dependencies
├── README.md        # This file
└── venv/            # Virtual environment (created automatically)
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

## 🎭 Using Custom Mappings

The viewer runs in **manual anonymization mode only**, putting you in full control.

### Quick Add From Statistics
1. Load your chat file and review *Messages per Participant*
2. Open **Quick Anonymization** to pick a participant from the list
3. Supply replacement name and email (auto-suggested but editable)
4. Click **Add** to store both mappings instantly

### Manual Mapping Table
- Expand **Custom Name Mappings** to add or edit arbitrary replacements
- Use it for project names, locations, or any other sensitive text
- Remove entries with a single click when no longer needed

### Coverage
- ✅ Creator names and emails
- ✅ Message text, quotes, reactions, and attachments
- ✅ Participant statistics (email column uses original-name lookups)

### Smart Matching
- **Word boundaries** protect substrings such as "John" vs "Johnson"
- **Case-insensitive** replacements cover "john", "JOHN", etc.
- **Punctuation-aware** rules handle commas, quotes, and multi-word phrases

#### File Structure
```
google-chat-viewer/
├── app.py           # Main application
├── ui.py            # UI components and layout
├── run.py           # Setup and launch script
├── requirements.txt # Dependencies
├── README.md        # This file
└── venv/            # Virtual environment (created automatically)
```

## 🎯 Advanced Features

### 🔒 Advanced Data Anonymization

- **Manual-Only Workflow**: Transparent replacements driven entirely by your mapping list
- **Quick Add UX**: Build mappings straight from participant statistics for rapid setup
- **Smart Defaults**: Initials-based name/email suggestions when selecting a participant to anonymize
- **Comprehensive Protection**: Names, emails, links, company/project names, file/network paths, attachments
- **Smart Pattern Matching**: Word boundaries, punctuation awareness, and case-insensitive replacements
- **Download & Preview Options**: Immediate download button, first-50-line JSON preview, and optional same-folder write-out

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
   git clone https://github.com/gopichandbusam/google-chat-viewer.git
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
## 🤝 Contributing

We welcome contributions! This project is open source and community-driven.

### How to Contribute
See the steps above in "Quick Start" for cloning and setup. To contribute:
1. 🍴 Fork the repository
2. 🌿 Create a feature branch
3. 🔧 Make your changes (features, bug fixes, docs, tests)
4. ✅ Test your changes
5. 📝 Commit and push
6. 🔄 Create a pull request (include clear description, screenshots for UI changes, reference issues)

### Areas We Need Help With
- 🌐 Internationalization: Multi-language support
- 🎨 UI/UX Improvements
- 🔧 New Anonymization Features
- 📊 Analytics Features
- 🐛 Bug Fixes
- 📖 Documentation
- 🧪 Testing

### Development Setup
Refer to "Quick Start" above for environment setup. For development mode:
```bash
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
- 🐛 **Bug Reports**: [Open an issue](https://github.com/gopichandbusam/google-chat-viewer/issues)
- 💡 **Feature Requests**: [Request a feature](https://github.com/gopichandbusam/google-chat-viewer/issues)
- 🤔 **Questions**: [Start a discussion](https://github.com/gopichandbusam/google-chat-viewer/discussions)

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