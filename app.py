"""
Google Chat Viewer - A comprehensive Streamlit application for viewing and analyzing Google Chat data.

This application provides a user-friendly interface to:
- View and analyze Google Chat messages from Takeout exports
- Anonymize sensitive data (names, emails, Google Drive links) for privacy
- Generate comprehensive statistics and analytics
- Export anonymized data in various formats

Author: Gopichand Busam <gopichand.busam@nyu.edu>
Version: 2.0
License: MIT

DISCLAIMER: The author takes NO responsibility for data privacy, legal compliance, 
or any consequences of using this software. Users are solely responsible for:
- Ensuring proper authorization to process chat data
- Compliance with applicable privacy laws (GDPR, CCPA, etc.)
- Data security and handling
- Obtaining proper consent from all parties

This software is provided "AS IS" without warranty. Use at your own risk.

Features:
- 📊 Comprehensive message statistics and analytics
- 🔒 Multi-mode data anonymization (Automatic/Manual/Mixed)
- 📁 File validation and error handling
- 🎯 Pagination for large datasets
- 💾 Multiple export options
- 🔍 Search and filtering capabilities
- 📈 Interactive data visualization

Usage: 
    Run with `python run.py` or directly with `streamlit run app.py`

Requirements:
    - Python 3.8+
    - Streamlit >= 1.28.0
    - Standard library modules (json, re, datetime, pathlib, collections)
"""

# Standard library imports
import json
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Third-party imports
import streamlit as st

# ===== APPLICATION CONFIGURATION =====
APP_TITLE = "Google Chat Viewer"
APP_VERSION = "2.0"
APP_AUTHOR = "Gopichand Busam"

# File handling configuration
MAX_FILE_SIZE_MB = 200  # Maximum upload file size in MB
SUPPORTED_FILE_TYPES = ['json']  # Supported file extensions
TARGET_FILENAME = "messages.json"  # Primary target file from Google Takeout

# Display configuration
MESSAGES_PER_PAGE = 50  # Number of messages to display per page
MAX_PREVIEW_LENGTH = 100  # Maximum length for message preview text

# Anonymization configuration
DEFAULT_EMAIL_DOMAIN = "example.com"  # Domain for anonymized emails
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Regex for email detection

# Google Drive link patterns for anonymization
DRIVE_LINK_PATTERNS = {
    'docs': r'https://docs\.google\.com/document/d/([a-zA-Z0-9-_]+)',
    'sheets': r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)', 
    'slides': r'https://docs\.google\.com/presentation/d/([a-zA-Z0-9-_]+)',
    'forms': r'https://docs\.google\.com/forms/d/([a-zA-Z0-9-_]+)',
    'drive': r'https://drive\.google\.com/(?:file/d/|open\?id=)([a-zA-Z0-9-_]+)'
}
# =====================================

def get_json_files() -> List[str]:
    """
    Discover and prioritize JSON files in the current directory.
    
    Searches for JSON files in the current working directory and prioritizes
    'messages.json' files as they are the standard output from Google Takeout.
    
    Returns:
        List[str]: Sorted list of JSON filenames with messages.json first
        
    Note:
        - Prioritizes messages.json files (Google Takeout standard)
        - Returns empty list if no JSON files found
        - Handles file system errors gracefully
    """
    try:
        current_dir = Path.cwd()
        json_files = list(current_dir.glob("*.json"))
        
        if not json_files:
            return []
        
        # Prioritize messages.json files (Google Takeout standard)
        messages_files = [f.name for f in json_files if f.name.lower() == TARGET_FILENAME]
        other_files = sorted([f.name for f in json_files if f.name.lower() != TARGET_FILENAME])
        
        return messages_files + other_files
        
    except (OSError, PermissionError) as e:
        st.error(f"❌ Error accessing directory: {e}")
        return []

def select_json_file() -> Tuple[Optional[str], Optional[str]]:
    """
    Provide user interface for selecting Google Chat JSON files.
    
    Offers two methods for file selection:
    1. File upload widget for remote files
    2. Local file selection from current directory
    
    Returns:
        Tuple[Optional[str], Optional[str]]: (file_path, display_name) or (None, None)
        
    Features:
        - File size validation for performance and security
        - Prioritization of messages.json files
        - Temporary file handling for uploads
        - Graceful error handling and user feedback
    """
    st.subheader("📁 Select Google Chat JSON File")
    
    # Informational guidance for users
    with st.container():
        st.info("💡 **Google Takeout Instructions**: Look for `messages.json` file in your Google Chat export")
        with st.expander("📖 Need help finding your file?"):
            st.markdown("""
            **Google Takeout Process:**
            1. Go to [Google Takeout](https://takeout.google.com)
            2. Select "Chat" service
            3. Download your archive
            4. Extract and look for `messages.json` files
            """)
    
    # Method 1: File Upload Widget
    st.write("**Option 1: Upload File**")
    uploaded_file = st.file_uploader(
        f"Upload your Google Chat JSON file ({TARGET_FILENAME} recommended):",
        type=SUPPORTED_FILE_TYPES,
        help=f"Select the {TARGET_FILENAME} file from your Google Takeout export"
    )
    
    if uploaded_file is not None:
        return _handle_uploaded_file(uploaded_file)
    
    # Method 2: Local File Selection
    return _handle_local_file_selection()

def _handle_uploaded_file(uploaded_file) -> Tuple[Optional[str], Optional[str]]:
    """
    Process uploaded file with validation and temporary storage.
    
    Args:
        uploaded_file: Streamlit file upload object
        
    Returns:
        Tuple[Optional[str], Optional[str]]: (temp_file_path, original_name) or (None, None)
    """
    # File size validation for performance and security
    max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if uploaded_file.size > max_size_bytes:
        st.error(f"⚠️ File too large! Maximum size: {MAX_FILE_SIZE_MB}MB (Your file: {uploaded_file.size / 1024 / 1024:.1f}MB)")
        return None, None
    
    # File type validation (additional safety check)
    file_extension = Path(uploaded_file.name).suffix.lower()
    if file_extension not in [f".{ext}" for ext in SUPPORTED_FILE_TYPES]:
        st.error(f"⚠️ Unsupported file type! Supported: {', '.join(SUPPORTED_FILE_TYPES)}")
        return None, None
        
    # Create temporary file with safe naming
    temp_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
    
    try:
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"✅ File uploaded successfully: {uploaded_file.name}")
        return temp_path, uploaded_file.name
        
    except (OSError, PermissionError) as e:
        st.error(f"❌ Error saving uploaded file: {str(e)}")
        return None, None
    except Exception as e:
        st.error(f"❌ Unexpected error during file upload: {str(e)}")
        return None, None

def _handle_local_file_selection() -> Tuple[Optional[str], Optional[str]]:
    """
    Handle local file selection from current directory.
    
    Returns:
        Tuple[Optional[str], Optional[str]]: (file_path, display_name) or (None, None)
    """
    # Discover local JSON files
    json_files = get_json_files()
    
    if not json_files:
        st.info("ℹ️ No JSON files found in current directory. Use file upload above.")
        return None, None
    
    st.divider()
    st.write("**Option 2: Select Local File**")
    
    # Highlight target file if available
    if TARGET_FILENAME in json_files:
        st.success(f"✅ Found `{TARGET_FILENAME}` - this is typically the correct file!")
    
    selected_file = st.selectbox(
        "Available JSON files:",
        ["Select a file..."] + json_files,
        help=f"JSON files in current directory ({TARGET_FILENAME} recommended)",
        key="local_file_selector"
    )
    
    if selected_file and selected_file != "Select a file...":
        # Validate file exists and is accessible
        file_path = Path(selected_file)
        if not file_path.exists():
            st.error(f"❌ File not found: {selected_file}")
            return None, None
        
        if not file_path.is_file():
            st.error(f"❌ Path is not a file: {selected_file}")
            return None, None
            
        return str(file_path), selected_file
    
    return None, None

def create_anonymization_mappings(data: Dict[str, Any], custom_mappings: Optional[Dict[str, str]] = None, 
                                mode: str = "automatic") -> Dict[str, str]:
    """
    Generate comprehensive anonymization mappings for names and emails.
    
    Analyzes chat data to extract all unique names and email addresses, then creates
    appropriate anonymization mappings based on the selected mode and user preferences.
    
    Args:
        data: Parsed JSON data containing Google Chat messages
        custom_mappings: User-defined mappings for specific terms (default: None)
        mode: Anonymization strategy - 'automatic', 'manual', or 'mixed' (default: 'automatic')
        
    Returns:
        Dict[str, str]: Mapping dictionary where keys are original terms and values are replacements
        
    Modes:
        - automatic: Auto-generate all anonymizations (Person 1, person1@example.com)
        - manual: Only use custom mappings, leave others unchanged
        - mixed: Use custom mappings where available, auto-generate for others
        
    Raises:
        ValueError: If mode is not one of the supported values
        
    Example:
        >>> mappings = create_anonymization_mappings(data, {"John": "Manager"}, "mixed")
        >>> print(mappings)
        {"John": "Manager", "Jane": "Person 1", "john@email.com": "person1@example.com"}
    """
    # Input validation
    if mode not in ["automatic", "manual", "mixed"]:
        raise ValueError(f"Invalid mode '{mode}'. Must be 'automatic', 'manual', or 'mixed'")
    
    if custom_mappings is None:
        custom_mappings = {}
    
    # Extract unique entities from chat data
    try:
        names, emails = _extract_entities_from_messages(data)
        
        # Generate mappings based on selected mode
        all_mappings = {}
        
        # Process name anonymization
        name_mappings = _create_name_mappings(names, custom_mappings, mode)
        all_mappings.update(name_mappings)
        
        # Process email anonymization
        email_mappings = _create_email_mappings(emails, custom_mappings, mode)
        all_mappings.update(email_mappings)
        
        # Log mapping statistics for debugging
        _log_mapping_statistics(names, emails, all_mappings, mode)
        
        return all_mappings
        
    except Exception as e:
        st.error(f"❌ Error creating anonymization mappings: {str(e)}")
        return {}

def _extract_entities_from_messages(data: Dict[str, Any]) -> Tuple[set, set]:
    """
    Extract all unique names and email addresses from chat messages.
    
    Args:
        data: Parsed JSON chat data
        
    Returns:
        Tuple[set, set]: (unique_names, unique_emails)
    """
    names = set()
    emails = set()
    
    messages = data.get('messages', [])
    if not messages:
        st.warning("⚠️ No messages found in data")
        return names, emails
    
    for message in messages:
        # Extract names from message creators
        if 'creator' in message and 'name' in message['creator']:
            creator_name = message['creator']['name'].strip()
            if creator_name:  # Avoid empty names
                names.add(creator_name)
        
        # Extract emails from message text using regex
        if 'text' in message and message['text']:
            text = message['text']
            found_emails = re.findall(EMAIL_PATTERN, text)
            # Filter out malformed emails and normalize
            valid_emails = {email.strip().lower() for email in found_emails if '@' in email and '.' in email.split('@')[1]}
            emails.update(valid_emails)
    
    return names, emails

def _create_name_mappings(names: set, custom_mappings: Dict[str, str], mode: str) -> Dict[str, str]:
    """
    Generate name anonymization mappings based on mode.
    
    Args:
        names: Set of unique names found in messages
        custom_mappings: User-provided custom mappings
        mode: Anonymization mode
        
    Returns:
        Dict[str, str]: Name to anonymized name mappings
    """
    name_mappings = {}
    person_counter = 1
    
    # Sort names for consistent ordering across runs
    sorted_names = sorted(names, key=str.lower)
    
    for name in sorted_names:
        if mode == "manual":
            # Manual: Only map names with custom mappings
            if name in custom_mappings:
                name_mappings[name] = custom_mappings[name]
        
        elif mode == "mixed":
            # Mixed: Custom first, then auto-generate
            if name in custom_mappings:
                name_mappings[name] = custom_mappings[name]
            else:
                name_mappings[name] = f"Person {person_counter}"
                person_counter += 1
        
        else:  # automatic
            # Automatic: Generate for all names
            name_mappings[name] = f"Person {person_counter}"
            person_counter += 1
    
    return name_mappings

def _create_email_mappings(emails: set, custom_mappings: Dict[str, str], mode: str) -> Dict[str, str]:
    """
    Generate email anonymization mappings based on mode.
    
    Args:
        emails: Set of unique email addresses found in messages
        custom_mappings: User-provided custom mappings
        mode: Anonymization mode
        
    Returns:
        Dict[str, str]: Email to anonymized email mappings
    """
    email_mappings = {}
    email_counter = 1
    
    # Sort emails for consistent ordering
    sorted_emails = sorted(emails)
    
    for email in sorted_emails:
        if mode == "manual":
            # Manual: Only map emails with custom mappings
            if email in custom_mappings:
                email_mappings[email] = custom_mappings[email]
        
        elif mode == "mixed":
            # Mixed: Custom first, then auto-generate
            if email in custom_mappings:
                email_mappings[email] = custom_mappings[email]
            else:
                email_mappings[email] = f"person{email_counter}@{DEFAULT_EMAIL_DOMAIN}"
                email_counter += 1
        
        else:  # automatic
            # Automatic: Generate for all emails
            email_mappings[email] = f"person{email_counter}@{DEFAULT_EMAIL_DOMAIN}"
            email_counter += 1
    
    return email_mappings

def _log_mapping_statistics(names: set, emails: set, mappings: Dict[str, str], mode: str) -> None:
    """
    Log anonymization statistics for debugging and user feedback.
    
    Args:
        names: Set of original names
        emails: Set of original emails  
        mappings: Generated mappings
        mode: Anonymization mode used
    """
    total_entities = len(names) + len(emails)
    mapped_entities = len(mappings)
    
    print(f"Anonymization Statistics:")
    print(f"  Mode: {mode}")
    print(f"  Names found: {len(names)}")
    print(f"  Emails found: {len(emails)}")
    print(f"  Total entities: {total_entities}")
    print(f"  Entities mapped: {mapped_entities}")
    print(f"  Mapping coverage: {mapped_entities/total_entities*100 if total_entities > 0 else 0:.1f}%")

def anonymize_all_links(text: str, anonymization_level: str = "domain") -> str:
    """
    Anonymize all types of links and URLs in text content.
    
    Provides comprehensive link anonymization including:
    - Google Drive/Workspace services (docs, sheets, slides, etc.)
    - General web URLs (http/https)
    - Email addresses  
    - File paths and network shares
    - Custom domain anonymization
    
    Args:
        text: Input text that may contain links/URLs
        anonymization_level: Level of anonymization - "domain" (preserve domain type) or "full" (generic placeholder)
        
    Returns:
        str: Text with all links anonymized
        
    Anonymization Levels:
        - "domain": Preserves service context (e.g., [GOOGLE_LINK], [GITHUB_LINK])
        - "full": Uses generic placeholders (e.g., [LINK], [URL])
        
    Supported Link Types:
        - Google Services (Docs, Sheets, Drive, Meet, etc.)
        - Social Media (Twitter, LinkedIn, Facebook, etc.)
        - Development (GitHub, GitLab, Stack Overflow, etc.)  
        - Communication (Slack, Discord, Zoom, etc.)
        - File sharing (Dropbox, OneDrive, etc.)
        - Generic HTTP/HTTPS URLs
        - Email addresses
        - IP addresses and network paths
        
    Example:
        >>> text = "Check https://github.com/user/repo and https://docs.google.com/document/d/abc123"
        >>> anonymize_all_links(text, "domain")
        "Check [GITHUB_LINK] and [DOCS_LINK]"
    """
    if not text or not isinstance(text, str):
        return text
    
    # Define comprehensive link patterns with service-specific anonymization
    link_patterns = {
        # Google Services (most specific first)
        'google_docs': (r'https://docs\.google\.com/document/d/[a-zA-Z0-9-_]+[^\s]*', '[DOCS_LINK]'),
        'google_sheets': (r'https://docs\.google\.com/spreadsheets/d/[a-zA-Z0-9-_]+[^\s]*', '[SHEETS_LINK]'),
        'google_slides': (r'https://docs\.google\.com/presentation/d/[a-zA-Z0-9-_]+[^\s]*', '[SLIDES_LINK]'),
        'google_forms': (r'https://docs\.google\.com/forms/d/[a-zA-Z0-9-_]+[^\s]*', '[FORMS_LINK]'),
        'google_drive': (r'https://drive\.google\.com/[^\s]*', '[DRIVE_LINK]'),
        'google_meet': (r'https://meet\.google\.com/[^\s]*', '[MEET_LINK]'),
        'google_calendar': (r'https://calendar\.google\.com/[^\s]*', '[CALENDAR_LINK]'),
        'google_classroom': (r'https://classroom\.google\.com/[^\s]*', '[CLASSROOM_LINK]'),
        'gmail': (r'https://mail\.google\.com/[^\s]*', '[GMAIL_LINK]'),
        'google_other': (r'https://[a-zA-Z0-9.-]*\.google\.com/[^\s]*', '[GOOGLE_LINK]'),
        
        # Development & Code Hosting
        'github': (r'https://(?:www\.)?github\.com/[^\s]*', '[GITHUB_LINK]'),
        'gitlab': (r'https://(?:www\.)?gitlab\.com/[^\s]*', '[GITLAB_LINK]'),
        'bitbucket': (r'https://(?:www\.)?bitbucket\.org/[^\s]*', '[BITBUCKET_LINK]'),
        'stackoverflow': (r'https://(?:www\.)?stackoverflow\.com/[^\s]*', '[STACKOVERFLOW_LINK]'),
        'npm': (r'https://(?:www\.)?npmjs\.com/[^\s]*', '[NPM_LINK]'),
        'pypi': (r'https://(?:www\.)?pypi\.org/[^\s]*', '[PYPI_LINK]'),
        
        # Communication & Collaboration
        'slack': (r'https://[a-zA-Z0-9.-]+\.slack\.com/[^\s]*', '[SLACK_LINK]'),
        'discord': (r'https://(?:www\.)?discord\.(?:gg|com)/[^\s]*', '[DISCORD_LINK]'),
        'zoom': (r'https://[a-zA-Z0-9.-]*\.zoom\.us/[^\s]*', '[ZOOM_LINK]'),
        'teams': (r'https://teams\.microsoft\.com/[^\s]*', '[TEAMS_LINK]'),
        'webex': (r'https://[a-zA-Z0-9.-]*\.webex\.com/[^\s]*', '[WEBEX_LINK]'),
        
        # File Sharing & Cloud Storage  
        'dropbox': (r'https://(?:www\.)?dropbox\.com/[^\s]*', '[DROPBOX_LINK]'),
        'onedrive': (r'https://[a-zA-Z0-9.-]*\.sharepoint\.com/[^\s]*', '[ONEDRIVE_LINK]'),
        'box': (r'https://[a-zA-Z0-9.-]*\.box\.com/[^\s]*', '[BOX_LINK]'),
        'icloud': (r'https://(?:www\.)?icloud\.com/[^\s]*', '[ICLOUD_LINK]'),
        
        # Social Media & Professional Networks
        'linkedin': (r'https://(?:www\.)?linkedin\.com/[^\s]*', '[LINKEDIN_LINK]'),
        'twitter': (r'https://(?:www\.)?(?:twitter|x)\.com/[^\s]*', '[TWITTER_LINK]'),
        'facebook': (r'https://(?:www\.)?facebook\.com/[^\s]*', '[FACEBOOK_LINK]'),
        'instagram': (r'https://(?:www\.)?instagram\.com/[^\s]*', '[INSTAGRAM_LINK]'),
        'youtube': (r'https://(?:www\.)?(?:youtube\.com|youtu\.be)/[^\s]*', '[YOUTUBE_LINK]'),
        
        # Documentation & Knowledge
        'notion': (r'https://(?:www\.)?notion\.so/[^\s]*', '[NOTION_LINK]'),
        'confluence': (r'https://[a-zA-Z0-9.-]*\.atlassian\.net/[^\s]*', '[CONFLUENCE_LINK]'),
        'jira': (r'https://[a-zA-Z0-9.-]*\.atlassian\.net/[^\s]*', '[JIRA_LINK]'),
        
        # Generic patterns (applied last)
        'ftp': (r'ftp://[^\s]*', '[FTP_LINK]'),
        'file_path': (r'file://[^\s]*', '[FILE_PATH]'),
        'network_share': (r'\\\\[a-zA-Z0-9.-]+\\[^\s]*', '[NETWORK_PATH]'),
        'ip_address': (r'https?://(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?[^\s]*', '[IP_ADDRESS]'),
        'generic_https': (r'https://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\s]*', '[HTTPS_LINK]'),
        'generic_http': (r'http://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\s]*', '[HTTP_LINK]'),
    }
    
    # Apply anonymization based on level
    if anonymization_level == "full":
        # Use generic placeholders for all links
        generic_replacements = {
            'web_url': (r'https?://[^\s]+', '[LINK]'),
            'email': (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
            'file_path': (r'(?:file://|[A-Z]:\\|/)[^\s]*', '[PATH]'),
        }
        
        for pattern_name, (pattern, replacement) in generic_replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    else:  # domain level - preserve service context
        # Apply service-specific patterns in order of specificity
        for service_name, (pattern, replacement) in link_patterns.items():
            if re.search(pattern, text, flags=re.IGNORECASE):
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

# Maintain backward compatibility
def anonymize_google_drive_links(text: str) -> str:
    """
    Legacy function for Google Drive link anonymization.
    Now redirects to the comprehensive anonymize_all_links function.
    
    Args:
        text: Input text containing links
        
    Returns:
        str: Text with Google links anonymized
    """
    return anonymize_all_links(text, "domain")

def anonymize_data_interface() -> Tuple[bool, Dict[str, str], Optional[str], Optional[str]]:
    """
    Render the data anonymization configuration interface.
    
    Provides a comprehensive UI for configuring anonymization settings including:
    - Enable/disable anonymization toggle
    - Mode selection (automatic, manual, mixed)
    - Custom mapping interface for specific replacements
    - Save options for anonymized output
    
    Returns:
        Tuple[bool, Dict[str, str], Optional[str], Optional[str]]: 
        (should_anonymize, custom_mappings, save_option, anonymization_mode)
        
    UI Components:
        - Checkbox for enabling anonymization
        - Radio buttons for mode selection  
        - Expandable sections for custom mappings
        - Save option selector
        
    Modes:
        - Automatic: Auto-generate all replacements
        - Manual: Only user-specified replacements
        - Mixed: Combination of automatic and custom
    """
    st.subheader("🔒 Data Anonymization (Optional)")
    
    # Main anonymization toggle
    anonymize = st.checkbox(
        "Enable data anonymization",
        help="Replace real names, emails, and links with anonymous identifiers for privacy protection",
        key="anonymization_enabled"
    )
    
    # Early return if anonymization is disabled
    if not anonymize:
        return False, {}, None, None
    
    # Configuration section
    st.info("📝 **Configure your anonymization settings below:**")
    
    # Anonymization capabilities overview
    _display_anonymization_features()
    
    # Mode selection interface
    mode = _render_mode_selection()
    
    # Mode-specific configuration
    custom_mappings = _render_mode_specific_interface(mode)
    
    # Save options
    save_option = _render_save_options()
    
    return True, custom_mappings, save_option, mode

def _display_anonymization_features() -> None:
    """Display overview of anonymization features and capabilities."""
    st.subheader("⚙️ Comprehensive Anonymization Features")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **👥 Names & Identity**
            • Names → Person 1, Person 2...
            • Custom replacements supported
            • Creator fields & message content
            • Company/organization names
            """)
            
            st.info("""
            **🔗 Links & URLs**
            • All web links anonymized
            • Service context preserved
            • Google Drive/Workspace
            • GitHub, Slack, Zoom, etc.
            • Generic HTTP/HTTPS URLs
            """)
        
        with col2:
            st.info("""
            **📧 Contact Information**  
            • Emails → person1@example.com...
            • Auto-detection via regex
            • Full privacy protection
            • Domain anonymization
            """)
            
            st.info("""
            **� File & Network Paths**
            • File paths anonymized
            • Network shares protected
            • IP addresses masked
            • Attachment filenames
            • Complete privacy coverage
            """)

def _render_mode_selection() -> str:
    """
    Render the anonymization mode selection interface.
    
    Returns:
        str: Selected anonymization mode ('automatic', 'manual', 'mixed')
    """
    st.subheader("🎯 Anonymization Mode")
    
    mode_options = [
        "🤖 Automatic - Auto-generate all replacements",
        "✋ Manual - I'll specify each replacement myself", 
        "🔀 Mixed - Automatic + Custom mappings"
    ]
    
    anonymization_mode = st.radio(
        "Select your anonymization strategy:",
        mode_options,
        help="Choose how you want to handle name and email anonymization",
        key="anonymization_mode_selector"
    )
    
    # Link anonymization settings
    st.subheader("🔗 Link Anonymization Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        link_anonymization = st.checkbox(
            "🔗 Anonymize all links and URLs",
            value=True,
            help="Replace all web links, file paths, and URLs with generic placeholders",
            key="link_anonymization_enabled"
        )
    
    with col2:
        if link_anonymization:
            link_level = st.selectbox(
                "Anonymization level:",
                ["Domain-aware (preserve service type)", "Full anonymization (generic placeholders)"],
                index=0,
                help="Domain-aware: [GITHUB_LINK], [GOOGLE_LINK] vs Full: [LINK], [URL]",
                key="link_anonymization_level"
            )
        else:
            link_level = "Domain-aware (preserve service type)"
    
    # Parse selected mode
    parsed_mode = "automatic"
    if "🤖 Automatic" in anonymization_mode:
        parsed_mode = "automatic"
    elif "✋ Manual" in anonymization_mode:
        parsed_mode = "manual"
    else:
        parsed_mode = "mixed"
    
    # Store link settings in session state for later use
    st.session_state['link_anonymization'] = link_anonymization
    st.session_state['link_level'] = "domain" if "Domain-aware" in link_level else "full"
    
    return parsed_mode

def _render_mode_specific_interface(mode: str) -> Dict[str, str]:
    """
    Render mode-specific configuration interface.
    
    Args:
        mode: Selected anonymization mode
        
    Returns:
        Dict[str, str]: Custom mappings from user input
    """
    if mode == "manual":
        # Manual mode - only custom mappings, no automatic generation
        with st.expander("🎭 Manual Anonymization Settings", expanded=True):
            st.warning("⚠️ **Manual Mode**: Only names/emails you specify below will be anonymized. All other names will remain unchanged. Google Drive links will still be anonymized for privacy.")
            show_custom_mapping_interface()
    
    elif mode == "mixed":
        # Mixed mode - both automatic and custom  
        with st.expander("🎭 Custom Anonymization Settings", expanded=True):
            st.info("🔀 **Mixed Mode**: Names/emails you specify below will use your custom replacement. All other names/emails will get automatic replacements. Google Drive links are always anonymized.")
            show_custom_mapping_interface()
    
    else:  # automatic mode
        # Automatic mode - show preview but no custom mappings needed
        st.success("🤖 **Automatic Mode**: All names → 'Person 1, 2, 3...', All emails → 'person1@example.com, person2@example.com...', All Google Drive links → '[DOCS_LINK], [SHEETS_LINK], etc.'")
        
        # Optional preview for automatic mode
        if st.checkbox("Show automatic anonymization preview", help="Preview how content will be automatically anonymized", key="auto_preview"):
            with st.container():
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**👥 Names (alphabetical order):**")
                    st.write("• First person → Person 1")
                    st.write("• Second person → Person 2")
                    st.write("• Third person → Person 3")
                    
                    st.write("**📧 Emails (discovery order):**")
                    st.write("• First email → person1@example.com")
                    st.write("• Second email → person2@example.com")
                
                with col2:
                    st.write("**🔗 Google Drive Links:**")
                    st.write("• Google Docs → [DOCS_LINK]")
                    st.write("• Google Sheets → [SHEETS_LINK]") 
                    st.write("• Google Slides → [SLIDES_LINK]")
                    st.write("• Google Forms → [FORMS_LINK]")
                    st.write("• Other Drive files → [DRIVE_LINK]")
    
    # Extract custom mappings from session state
    return _get_custom_mappings_from_session()

def _render_save_options() -> str:
    """
    Render the save options interface for anonymized data.
    
    Returns:
        str: Selected save option
    """
    st.subheader("💾 Save Anonymized Data")
    
    save_options = [
        "Don't save (view only)",
        "Save to same folder", 
        "Ask me where to save"
    ]
    
    save_option = st.radio(
        "Choose where to save anonymized data:",
        save_options,
        help="Select how you want to handle the anonymized output file",
        key="save_option_selector"
    )
    
    # Provide additional context based on selection
    if save_option == "Don't save (view only)":
        st.info("💡 Data will only be displayed in the app, no file will be saved")
    elif save_option == "Save to same folder":
        st.info("📁 Anonymized file will be saved with '_anonymized' suffix in the same directory")
    else:
        st.info("📂 You'll be prompted to choose a save location when processing completes")
    
    return save_option

def _get_custom_mappings_from_session() -> Dict[str, str]:
    """
    Extract custom mappings from Streamlit session state.
    
    Returns:
        Dict[str, str]: Custom mappings dictionary
    """
    custom_mappings = {}
    
    if 'custom_mappings' in st.session_state and st.session_state.custom_mappings:
        for mapping in st.session_state.custom_mappings:
            if isinstance(mapping, dict) and 'original' in mapping and 'replacement' in mapping:
                original = mapping['original'].strip()
                replacement = mapping['replacement'].strip()
                if original and replacement:  # Ensure non-empty values
                    custom_mappings[original] = replacement
    
    return custom_mappings


def show_custom_mapping_interface() -> None:
    """
    Render the custom mapping interface for user-defined anonymization rules.
    
    Provides an interactive interface for users to specify custom text replacements
    including names, emails, company names, and other sensitive information.
    
    Features:
        - Input fields for original and replacement text
        - Duplicate detection and validation
        - Live preview of current mappings
        - Individual and bulk deletion options
        - Real-time feedback and error handling
    
    Session State:
        Uses 'custom_mappings' key to store list of mapping dictionaries
        Each mapping: {'original': str, 'replacement': str}
    """
    # Feature overview
    st.markdown("""
    **📝 Create Custom Text Replacements:**
    - **👥 Names**: Replace in sender fields AND message content
    - **📧 Emails**: Custom email anonymization (e.g., john@company.com → manager@example.com)  
    - **🏢 Organizations**: Replace company/project names
    - **🔗 Links**: Google Drive links are auto-anonymized regardless
    """)
    
    # Initialize session state
    _initialize_mapping_session_state()
    
    # Add new mapping section
    _render_add_mapping_interface()
    
    # Display existing mappings
    _render_existing_mappings()
    
    # Show preview of replacements
    _render_mapping_preview()

def _initialize_mapping_session_state() -> None:
    """Initialize session state for custom mappings if not already present."""
    if 'custom_mappings' not in st.session_state:
        st.session_state.custom_mappings = []

def _render_add_mapping_interface() -> None:
    """Render the interface for adding new custom mappings."""
    st.write("**➕ Add New Text Replacement:**")
    
    col1, col2, col3 = st.columns([3, 3, 1])
    
    with col1:
        original_text = st.text_input(
            "Original text to replace:", 
            key="new_original",
            placeholder="e.g., John Smith, company@email.com"
        )
    
    with col2:
        replacement_text = st.text_input(
            "Replace with:", 
            key="new_replacement",
            placeholder="e.g., Manager, team@example.com"
        )
    
    with col3:
        st.write("")  # Spacing
        if st.button("➕ Add", help="Add this mapping to your anonymization rules"):
            _handle_add_mapping(original_text, replacement_text)

def _handle_add_mapping(original: str, replacement: str) -> None:
    """
    Handle adding a new mapping with validation.
    
    Args:
        original: Original text to replace
        replacement: Replacement text
    """
    # Input validation
    if not original or not original.strip():
        st.error("❌ Original text cannot be empty")
        return
    
    if not replacement or not replacement.strip():
        st.error("❌ Replacement text cannot be empty")
        return
    
    # Clean input
    original_clean = original.strip()
    replacement_clean = replacement.strip()
    
    # Check for duplicates
    existing_originals = {m['original'] for m in st.session_state.custom_mappings}
    
    if original_clean in existing_originals:
        st.warning("⚠️ This mapping already exists! Remove the existing one first.")
        return
    
    # Add new mapping
    new_mapping = {
        'original': original_clean,
        'replacement': replacement_clean
    }
    
    st.session_state.custom_mappings.append(new_mapping)
    st.success(f"✅ Added mapping: `{original_clean}` → `{replacement_clean}`")
    st.rerun()

def _render_existing_mappings() -> None:
    """Render the list of existing custom mappings with management options."""
    if not st.session_state.custom_mappings:
        st.info("💡 No custom mappings added yet. Add some above to get started!")
        return
    
    st.write("**📋 Your Custom Mappings:**")
    
    # Display each mapping with delete option
    for i, mapping in enumerate(st.session_state.custom_mappings):
        col1, col2, col3 = st.columns([4, 4, 1])
        
        with col1:
            st.write(f"**{mapping['original']}**")
        
        with col2:
            st.write(f"→ *{mapping['replacement']}*")
        
        with col3:
            if st.button("🗑️", key=f"delete_mapping_{i}", help="Remove this mapping"):
                st.session_state.custom_mappings.pop(i)
                st.success("✅ Mapping removed")
                st.rerun()
    
    # Bulk actions
    if len(st.session_state.custom_mappings) > 1:
        st.write("")  # Spacing
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🗑️ Clear All Mappings", help="Remove all custom mappings"):
                st.session_state.custom_mappings = []
                st.success("✅ All mappings cleared")
                st.rerun()

def _render_mapping_preview() -> None:
    """Render a preview of what will be replaced based on current mappings."""
    if not st.session_state.custom_mappings:
        return
    
    st.write("**👀 Replacement Preview:**")
    st.caption("These replacements will be applied to chat messages:")
    
    # Create preview in a nice format
    with st.container():
        for mapping in st.session_state.custom_mappings:
            col1, col2, col3 = st.columns([4, 1, 4])
            with col1:
                st.code(mapping['original'], language=None)
            with col2:
                st.write("→")
            with col3:
                st.code(mapping['replacement'], language=None)

def apply_anonymization(data: Dict[str, Any], name_mappings: Dict[str, str]) -> Dict[str, Any]:
    """
    Apply comprehensive anonymization to Google Chat data.
    
    Performs deep anonymization of chat messages including:
    - Message creator names in sender fields
    - Names and emails within message text content
    - Quoted message creators and content
    - Google Drive links (docs, sheets, slides, etc.)
    - Attachment filenames containing sensitive information
    
    Args:
        data: Original parsed JSON chat data
        name_mappings: Dictionary mapping original terms to anonymized replacements
        
    Returns:
        Dict[str, Any]: Fully anonymized copy of the original data
        
    Anonymization Strategy:
        1. Creates deep copy to preserve original data
        2. Sorts mappings by length (longest first) to prevent partial replacements
        3. Applies text replacement using multiple regex strategies
        4. Handles Google Drive links with specialized anonymization
        5. Processes quoted messages and attachments
        
    Error Handling:
        - Returns original data if anonymization fails
        - Logs errors for debugging
        - Continues processing even if individual messages fail
    """
    try:
        anonymized_data = json.loads(json.dumps(data))  # Deep copy
        
        # Sort mappings by length (longest first) to avoid partial replacements
        sorted_mappings = sorted(name_mappings.items(), key=lambda x: len(x[0]), reverse=True)
        
        # Anonymize message creators and content
        for message in anonymized_data.get('messages', []):
            # 1. Anonymize message creator names
            if 'creator' in message and 'name' in message['creator']:
                original_name = message['creator']['name']
                if original_name in name_mappings:
                    message['creator']['name'] = name_mappings[original_name]
            
            # 2. Anonymize quoted message creators
            if 'quoted_message_metadata' in message:
                quoted_creator = message['quoted_message_metadata'].get('creator', {})
                if 'name' in quoted_creator:
                    original_name = quoted_creator['name']
                    if original_name in name_mappings:
                        quoted_creator['name'] = name_mappings[original_name]
                
                # Also anonymize quoted message text content
                if 'text' in message['quoted_message_metadata']:
                    quoted_text = message['quoted_message_metadata']['text']
                    for original, replacement in sorted_mappings:
                        # Multiple pattern approaches for better matching
                        patterns = [
                            r'\b' + re.escape(original) + r'\b',  # Word boundaries
                            re.escape(original)  # Exact match (fallback)
                        ]
                        for pattern in patterns:
                            quoted_text = re.sub(pattern, replacement, quoted_text, flags=re.IGNORECASE)
                    
                    # Anonymize all links in quoted text if enabled
                    if st.session_state.get('link_anonymization', True):
                        link_level = st.session_state.get('link_level', 'domain')
                        quoted_text = anonymize_all_links(quoted_text, link_level)
                    message['quoted_message_metadata']['text'] = quoted_text
            
            # 3. Anonymize main message text content
            if 'text' in message and message['text']:
                text = message['text']
                original_text = text  # Keep for debugging
                
                # Apply name/email mappings with multiple strategies
                for original, replacement in sorted_mappings:
                    if original.lower() in text.lower():  # Quick check before regex
                        # Strategy 1: Word boundaries (best for names)
                        word_pattern = r'\b' + re.escape(original) + r'\b'
                        text = re.sub(word_pattern, replacement, text, flags=re.IGNORECASE)
                        
                        # Strategy 2: Handle names with punctuation/quotes
                        punct_pattern = r'(?<=["\'\s])' + re.escape(original) + r'(?=["\'\s\.,!?])'
                        text = re.sub(punct_pattern, replacement, text, flags=re.IGNORECASE)
                        
                        # Strategy 3: Exact match (fallback for phrases/companies)
                        if len(original.split()) > 1:  # Multi-word terms
                            exact_pattern = re.escape(original)
                            text = re.sub(exact_pattern, replacement, text, flags=re.IGNORECASE)
                
                # Anonymize all links if enabled
                if st.session_state.get('link_anonymization', True):
                    link_level = st.session_state.get('link_level', 'domain')
                    text = anonymize_all_links(text, link_level)
                
                message['text'] = text
                
                # Debug logging (optional - can be removed in production)
                if original_text != text:
                    print(f"Text anonymized: '{original_text[:50]}...' -> '{text[:50]}...'")
            
            # 4. Anonymize attachment names if they contain sensitive info
            if 'attached_files' in message:
                for attachment in message['attached_files']:
                    if 'original_name' in attachment:
                        file_name = attachment['original_name']
                        for original, replacement in sorted_mappings:
                            file_name = re.sub(re.escape(original), replacement, file_name, flags=re.IGNORECASE)
                        attachment['original_name'] = file_name
        
        return anonymized_data
        
    except Exception as e:
        st.error(f"❌ Error during anonymization: {e}")
        st.error(f"Details: {str(e)}")
        return data

def save_anonymized_data(data, original_filename, save_option):
    """
    Save anonymized data based on user preference.
    
    Args:
        data: Anonymized JSON data
        original_filename: Original file name
        save_option: Where to save the data
    """
    if save_option == "Don't save (view only)":
        return
    
    try:
        # Generate anonymized filename
        name_parts = original_filename.rsplit('.', 1)
        if len(name_parts) == 2:
            anonymized_filename = f"{name_parts[0]}_anonymized.{name_parts[1]}"
        else:
            anonymized_filename = f"{original_filename}_anonymized"
        
        if save_option == "Save to same folder":
            # Save in current directory
            with open(anonymized_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            st.success(f"✅ Anonymized data saved as: `{anonymized_filename}`")
            
        elif save_option == "Ask me where to save":
            # Provide download option
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Download Anonymized Data",
                data=json_str,
                file_name=anonymized_filename,
                mime="application/json",
                help="Click to download the anonymized JSON file"
            )
            
    except Exception as e:
        st.error(f"❌ Error saving anonymized data: {e}")

def create_message_statistics(messages):
    """
    Create comprehensive statistics about the messages.
    
    Args:
        messages: List of parsed messages
        
    Returns:
        Dictionary containing various statistics
    """
    if not messages:
        return {}
    
    try:
        # Count messages per person
        message_counts = Counter(msg['name'] for msg in messages)
        
        # Count by original names for accuracy
        original_counts = Counter(msg.get('original_name', msg['name']) for msg in messages)
        
        # Calculate date range
        timestamps = [msg['timestamp'] for msg in messages]
        date_range = {
            'start': min(timestamps),
            'end': max(timestamps),
            'total_days': (max(timestamps) - min(timestamps)).days + 1
        }
        
        # Messages per day
        dates = [ts.date() for ts in timestamps]
        daily_counts = Counter(dates)
        
        # Most active day
        most_active_day = daily_counts.most_common(1)[0] if daily_counts else None
        
        return {
            'message_counts': message_counts,
            'original_counts': original_counts,
            'total_messages': len(messages),
            'unique_participants': len(message_counts),
            'date_range': date_range,
            'daily_counts': daily_counts,
            'most_active_day': most_active_day,
            'average_per_day': len(messages) / max(date_range['total_days'], 1)
        }
        
    except Exception as e:
        st.error(f"❌ Error creating statistics: {e}")
        return {}

def display_message_statistics(stats):
    """
    Display comprehensive message statistics in the UI.
    
    Args:
        stats: Statistics dictionary from create_message_statistics
    """
    if not stats:
        st.warning("⚠️ No statistics available")
        return
    
    st.subheader("📊 Chat Statistics")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💬 Total Messages", f"{stats['total_messages']:,}")
    
    with col2:
        st.metric("👥 Participants", stats['unique_participants'])
    
    with col3:
        st.metric("📅 Total Days", stats['date_range']['total_days'])
    
    with col4:
        avg_per_day = stats['average_per_day']
        st.metric("📈 Avg/Day", f"{avg_per_day:.1f}")
    
    # Detailed message counts table
    st.subheader("👤 Messages per Participant")
    
    # Create data for better display
    message_data = []
    for name, count in stats['message_counts'].most_common():
        percentage = (count / stats['total_messages']) * 100
        message_data.append({
            'Participant': name,
            'Messages': f"{count:,}",
            'Percentage': f"{percentage:.1f}%"
        })
    
    # Display as a nice table
    if message_data:
        st.write("**Message Distribution:**")
        
        for i, row in enumerate(message_data, 1):
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"**{i}.** {row['Participant']}")
            with col2:
                st.write(f"📬 {row['Messages']}")
            with col3:
                st.write(f"📊 {row['Percentage']}")
    
    # Most active day
    if stats['most_active_day']:
        most_active_date, most_active_count = stats['most_active_day']
        st.info(f"🔥 **Most Active Day:** {most_active_date.strftime('%B %d, %Y')} with {most_active_count} messages")
    
    # Date range
    date_range = stats['date_range']
    st.info(f"📅 **Chat Period:** {date_range['start'].strftime('%B %d, %Y')} to {date_range['end'].strftime('%B %d, %Y')}")
    
    return message_data

def parse_chat_message(message, name_mappings=None):
    """
    Parses a single message from the JSON and extracts the key data.
    
    Args:
        message: Raw message data from JSON
        name_mappings: Optional dict for name anonymization
        
    Returns:
        Dictionary with parsed message data, or None if it's a system message
    """
    try:
        # Validate message structure
        if not isinstance(message, dict):
            return None
            
        if 'creator' not in message or 'name' not in message['creator']:
            # Skip system messages without a creator
            return None
        
        # Get sender name with optional anonymization
        sender_name = message['creator']['name']
        original_name = sender_name  # Store original for statistics
        
        if name_mappings and sender_name in name_mappings:
            sender_name = name_mappings[sender_name]
        
        # Parse timestamp with error handling
        try:
            date_str = message['created_date']
            # Clean the date string (handle Unicode characters)
            date_str_clean = date_str.replace(" at ", " ").replace("\u202f", " ")
            date_format = "%A, %B %d, %Y %I:%M:%S %p %Z"
            timestamp = datetime.strptime(date_str_clean, date_format)
        except (KeyError, ValueError) as e:
            # If date parsing fails, use a default timestamp
            timestamp = datetime.now()
            print(f"Warning: Could not parse date for message: {e}")
        
        # Get text content with safety check
        text = message.get('text', '')
        if not isinstance(text, str):
            text = str(text) if text is not None else ''
        
        # Apply anonymization to text content if mappings provided
        if name_mappings and text:
            # Sort mappings by length (longest first) for better replacement
            sorted_mappings = sorted(name_mappings.items(), key=lambda x: len(x[0]), reverse=True)
            for original, replacement in sorted_mappings:
                if original.lower() in text.lower():
                    # Multiple replacement strategies
                    # 1. Word boundaries for names
                    word_pattern = r'\b' + re.escape(original) + r'\b'
                    text = re.sub(word_pattern, replacement, text, flags=re.IGNORECASE)
                    
                    # 2. Quoted names or names with punctuation
                    punct_pattern = r'(?<=["\'\s])' + re.escape(original) + r'(?=["\'\s\.,!?])'
                    text = re.sub(punct_pattern, replacement, text, flags=re.IGNORECASE)
                    
                    # 3. Exact match for multi-word terms (companies, projects)
                    if len(original.split()) > 1:
                        exact_pattern = re.escape(original)
                        text = re.sub(exact_pattern, replacement, text, flags=re.IGNORECASE)

        # Process attachments with error handling
        attachment_md = ""
        try:
            if 'attached_files' in message and isinstance(message['attached_files'], list):
                for f in message['attached_files']:
                    if isinstance(f, dict):
                        name = f.get('original_name', 'Attached File')
                        # Sanitize filename for display
                        name = str(name)[:100]  # Limit length
                        attachment_md += f"\n\n> 📎 **Attachment:** `{name}`"
        except Exception as e:
            print(f"Warning: Error processing attachments: {e}")
        
        # Process reactions with error handling
        reactions_md = ""
        try:
            if 'reactions' in message and isinstance(message['reactions'], list):
                reaction_list = []
                for reaction in message['reactions']:
                    if isinstance(reaction, dict):
                        emoji = reaction.get('emoji', {}).get('unicode', '▫️')
                        count = len(reaction.get('reactor_emails', []))
                        if count > 0:  # Only show reactions with count > 0
                            reaction_list.append(f"{emoji} {count}")
                if reaction_list:
                    reactions_md = "\n\n" + " ".join(reaction_list)
        except Exception as e:
            print(f"Warning: Error processing reactions: {e}")
        
        # Process quoted messages with error handling
        quote_md = ""
        try:
            if 'quoted_message_metadata' in message:
                quoted_msg = message['quoted_message_metadata']
                if isinstance(quoted_msg, dict):
                    quote_author = quoted_msg.get('creator', {}).get('name', 'Someone')
                    quote_text = quoted_msg.get('text', '...')
                    
                    # Apply anonymization to quoted author
                    if name_mappings and quote_author in name_mappings:
                        quote_author = name_mappings[quote_author]
                    
                    # Sanitize and apply anonymization to quote text
                    if isinstance(quote_text, str) and quote_text.strip():
                        quote_text = quote_text.strip()
                        
                        # Apply anonymization to quoted text content
                        if name_mappings:
                            sorted_mappings = sorted(name_mappings.items(), key=lambda x: len(x[0]), reverse=True)
                            for original, replacement in sorted_mappings:
                                if original.lower() in quote_text.lower():
                                    # Apply same anonymization strategies as main text
                                    word_pattern = r'\b' + re.escape(original) + r'\b'
                                    quote_text = re.sub(word_pattern, replacement, quote_text, flags=re.IGNORECASE)
                                    
                                    punct_pattern = r'(?<=["\'\s])' + re.escape(original) + r'(?=["\'\s\.,!?])'
                                    quote_text = re.sub(punct_pattern, replacement, quote_text, flags=re.IGNORECASE)
                                    
                                    if len(original.split()) > 1:
                                        exact_pattern = re.escape(original)
                                        quote_text = re.sub(exact_pattern, replacement, quote_text, flags=re.IGNORECASE)
                        
                        # Truncate after anonymization
                        if len(quote_text) > 100:
                            quote_text = quote_text[:100] + "..."
                        quote_md = f"> **{quote_author} said:**\n> {quote_text}\n\n"
        except Exception as e:
            print(f"Warning: Error processing quoted message: {e}")

        return {
            'name': sender_name,
            'timestamp': timestamp,
            'full_text': f"{quote_md}{text}{attachment_md}{reactions_md}",
            'original_name': original_name  # Keep original for stats
        }

    except KeyError as e:
        # Skip messages with missing required fields
        print(f"Skipping message with missing field: {e}")
        return None
    except Exception as e:
        print(f"Error parsing message: {e}")
        return None

def main() -> None:
    """
    Main Streamlit application entry point.
    
    Orchestrates the complete Google Chat Viewer workflow:
    1. UI initialization and configuration
    2. File selection and validation
    3. Data loading and processing
    4. Anonymization configuration
    5. Statistics generation and display
    6. Message visualization with pagination
    7. Export functionality
    
    Features:
        - Responsive wide layout for better data visualization
        - Comprehensive error handling and user feedback
        - Progress tracking for long-running operations
        - Clean separation of concerns with helper functions
    """
    # === APPLICATION INITIALIZATION ===
    _initialize_streamlit_config()
    _render_application_header()
    _render_usage_instructions()
    
    # === FILE PROCESSING ===
    selected_file, display_name = select_json_file()
    if not selected_file:
        st.info("👆 Please select a JSON file to continue")
        st.stop()
    
    # Load and validate chat data
    data = _load_and_validate_chat_data(selected_file, display_name)
    if not data:
        return  # Error already displayed in load function
    
    # === DATA PROCESSING ===
    _process_chat_data(data, selected_file)

def _initialize_streamlit_config() -> None:
    """Initialize Streamlit page configuration and styling."""
    st.set_page_config(
        layout="wide", 
        page_title=f"{APP_TITLE} v{APP_VERSION}",
        page_icon="💬",
        initial_sidebar_state="auto"
    )

def _render_application_header() -> None:
    """Render the application header with title and attribution."""
    st.title(f"💬 {APP_TITLE}")
    
    # Version and author info
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"*Version {APP_VERSION} - Created by {APP_AUTHOR}* ✨")
    
    # Application description
    st.markdown("""
    **A comprehensive tool for viewing and analyzing Google Chat data with advanced privacy features.**
    
    Upload your `messages.json` file from Google Takeout to explore chat statistics, 
    anonymize sensitive information, and export processed data.
    """)
    
    # Legal disclaimer
    with st.expander("⚠️ Legal Disclaimer - READ BEFORE USE", expanded=False):
        st.warning("""
        **IMPORTANT**: By using this application, you acknowledge that:
        
        🚫 **Author Disclaimer**: The author takes NO responsibility for:
        - Data privacy or security breaches
        - Legal compliance with local or international laws
        - Consequences of data processing or sharing
        - Loss, corruption, or misuse of your data
        
        ✅ **Your Responsibility**: You are solely responsible for:
        - Ensuring you have proper authorization to process the chat data
        - Compliance with applicable privacy laws (GDPR, CCPA, etc.)
        - Obtaining consent from all parties whose data appears in your exports
        - Securing your data during processing and storage
        
        🔒 **Best Practices**:
        - Only process data you are legally authorized to access
        - Use in secure, private environments only
        - Delete processed files when no longer needed
        - Review your organization's data policies before use
        
        **This software is provided "AS IS" without warranty. Use at your own risk.**
        """)

def _render_usage_instructions() -> None:
    """Render expandable instructions for obtaining Google Takeout data."""
    with st.expander("📋 How to get your Google Chat data from Google Takeout", expanded=False):
        st.markdown("""
        ### 🚀 Quick Setup Guide
        
        **Prerequisites:** 
        - Google account with Chat access
        - Note: Regular users can only export their own data
        
        **Step-by-Step Process:**
        
        1. **🌐 Visit Google Takeout**
           - Go to [takeout.google.com](https://takeout.google.com)
        
        2. **🔄 Configure Export**
           - Click **"Deselect all"** to clear all services
           - Scroll down and check **"Chat"** ☑️
           - Click **"Next step"**
        
        3. **� Export Settings**
           - Delivery method: **Send download link via email** (recommended)
           - File type: **ZIP** (default)
           - Click **"Create export"**
        
        4. **📧 Download & Extract**
           - Check your email for the download link
           - Extract the ZIP file
           - Look for `messages.json` file(s)
        
        **💡 Pro Tips:**
        - Export may take several minutes to hours depending on data size
        - Multiple `messages.json` files = multiple chat rooms/groups
        - Each file represents one conversation or group
        
        **� Official Documentation:** [Google Takeout Help](https://support.google.com/accounts/answer/3024190)
        """)

def _load_and_validate_chat_data(file_path: str, display_name: str) -> Optional[Dict[str, Any]]:
    """
    Load and validate Google Chat JSON data.
    
    Args:
        file_path: Path to the JSON file
        display_name: User-friendly name for display
        
    Returns:
        Optional[Dict[str, Any]]: Parsed JSON data or None if error occurred
    """
    st.info(f"📄 Loading: **{display_name}**")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate data structure
        if not isinstance(data, dict):
            st.error("❌ Invalid file format: Expected JSON object")
            return None
        
        if 'messages' not in data:
            st.error("❌ Invalid Google Chat file: No 'messages' field found")
            return None
        
        messages = data.get('messages', [])
        if not isinstance(messages, list):
            st.error("❌ Invalid data structure: 'messages' should be a list")
            return None
        
        if len(messages) == 0:
            st.warning("⚠️ No messages found in this file")
            return None
        
        st.success(f"✅ Successfully loaded {len(messages)} messages")
        return data
        
    except FileNotFoundError:
        st.error(f"❌ File not found: `{display_name}`")
        return None
    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid JSON format: {str(e)}")
        return None
    except UnicodeDecodeError:
        st.error("❌ File encoding error. Please ensure the file is UTF-8 encoded")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error loading file: {str(e)}")
        return None

def _process_chat_data(data: Dict[str, Any], file_path: str) -> None:
    """
    Process loaded chat data through the complete workflow.
    
    Args:
        data: Parsed JSON chat data
        file_path: Original file path for reference
    """
    # === ANONYMIZATION WORKFLOW ===
    should_anonymize, custom_mappings, save_option, anonymization_mode = anonymize_data_interface()
    
    # Create name mappings if anonymization is enabled
    name_mappings = {}
    if should_anonymize:
        with st.spinner("� Creating anonymization mappings..."):
            name_mappings = create_anonymization_mappings(data, custom_mappings, anonymization_mode)
            
        if name_mappings:
            st.success(f"✅ Created {len(name_mappings)} anonymization mappings")
        else:
            st.info("ℹ️ No anonymization mappings created")
    
    # === STATISTICS GENERATION ===
    with st.spinner("📊 Generating statistics..."):
        stats = create_message_statistics(data)
    
    # Display statistics
    display_message_statistics(stats)
    
    # === MESSAGE DISPLAY ===
    # Apply anonymization if enabled
    display_data = data
    if should_anonymize and name_mappings:
        with st.spinner("🔄 Applying anonymization..."):
            display_data = apply_anonymization(data, name_mappings)
        
        # Save anonymized data if requested
        if save_option != "Don't save (view only)":
            save_anonymized_data(display_data, Path(file_path).name, save_option)
    
    # === MESSAGE PROCESSING & DISPLAY ===
    _display_processed_messages(display_data, name_mappings)

def _display_processed_messages(data: Dict[str, Any], name_mappings: Dict[str, str]) -> None:
    """
    Process and display chat messages with optional anonymization.
    
    Args:
        data: Chat data (original or anonymized)  
        name_mappings: Anonymization mappings applied (for reference)
    """
    # Process messages with progress tracking
    parsed_messages = []
    progress_bar = st.progress(0)
    total_messages = len(data.get('messages', []))
    
    if total_messages == 0:
        st.warning("⚠️ No messages found in the data.")
        return
    
    with st.spinner("� Processing messages..."):
        for i, msg in enumerate(data['messages']):
            parsed_msg = parse_chat_message(msg, name_mappings)
            if parsed_msg:
                parsed_messages.append(parsed_msg)
            
            # Update progress every 100 messages for performance
            if i % 100 == 0:
                progress_bar.progress((i + 1) / total_messages)
    
    progress_bar.progress(1.0)
    
    # Validate processed messages
    if not parsed_messages:
        st.warning("⚠️ No valid chat messages found in the JSON file.")
        return

    # Sort messages by timestamp
    sorted_messages = sorted(parsed_messages, key=lambda x: x['timestamp'])
    
    # Display success message
    st.success(f"🎉 Successfully processed **{len(sorted_messages):,}** messages!")
    
    st.divider()
    
    # Display messages with chat interface
    st.subheader("💬 Chat Messages")
    
    # Add pagination for better performance with large datasets
    messages_per_page = MESSAGES_PER_PAGE
    total_pages = (len(sorted_messages) - 1) // messages_per_page + 1
    
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.number_input(
                f"Page (1-{total_pages})", 
                min_value=1, 
                max_value=total_pages, 
                value=1,
                help=f"Showing {messages_per_page} messages per page"
            )
        
        start_idx = (page - 1) * messages_per_page
        end_idx = min(start_idx + messages_per_page, len(sorted_messages))
        page_messages = sorted_messages[start_idx:end_idx]
        
        st.info(f"Displaying messages {start_idx + 1}-{end_idx} of {len(sorted_messages)}")
    else:
        page_messages = sorted_messages
    
    # Display messages using Streamlit's chat interface
    for msg in page_messages:
        with st.chat_message(name=msg['name']):
            st.markdown(msg['full_text'], unsafe_allow_html=True)
            st.caption(msg['timestamp'].strftime("%b %d, %Y at %I:%M %p"))

# ===== APPLICATION ENTRY POINT =====
if __name__ == "__main__":
    main()