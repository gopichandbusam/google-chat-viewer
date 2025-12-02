"""
Google Chat Viewer - UI Components Module

This module contains all Streamlit UI components and rendering functions
for the Google Chat Viewer application.

Author: Gopichand Busam <gopichand.busam@nyu.edu>
Version: 2.0
License: MIT
"""

import json
import re
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, List, Pattern
from datetime import datetime
from collections import Counter

import streamlit as st # type: ignore

# Import configuration constants from app
from app import (
    APP_TITLE, APP_VERSION, APP_AUTHOR,
    DEFAULT_MAX_FILE_SIZE_MB, DEFAULT_SUPPORTED_FILE_TYPES,
    DEFAULT_TARGET_FILENAME, DEFAULT_MESSAGES_PER_PAGE,
    DEFAULT_MAX_PREVIEW_LENGTH, DEFAULT_EMAIL_DOMAIN
)


# ===== HELPER FUNCTIONS =====

def compile_mappings(name_mappings: Dict[str, str]) -> List[Tuple[str, str, Pattern, Pattern, Pattern]]:
    """
    Pre-compile regex patterns for all mappings to improve performance.
    Returns a list of tuples: (original, replacement, word_pattern, punct_pattern, exact_pattern)
    """
    if not name_mappings:
        return []
        
    # Sort by length (longest first) to prevent partial replacements
    sorted_mappings = sorted(name_mappings.items(), key=lambda x: len(x[0]), reverse=True)
    
    compiled = []
    for original, replacement in sorted_mappings:
        # 1. Word boundaries
        word_pattern = re.compile(r'\b' + re.escape(original) + r'\b', flags=re.IGNORECASE)
        # 2. Punctuation-aware
        punct_pattern = re.compile(r'(?<=["\'\s])' + re.escape(original) + r'(?=["\'\s\.,!?])', flags=re.IGNORECASE)
        # 3. Exact match (for multi-word)
        exact_pattern = re.compile(re.escape(original), flags=re.IGNORECASE)
        
        compiled.append((original, replacement, word_pattern, punct_pattern, exact_pattern))
        
    return compiled


def parse_chat_message(message, name_mappings=None, compiled_mappings=None):
    """Parse a single message from JSON and extract key data."""
    try:
        if not isinstance(message, dict):
            return None
            
        if 'creator' not in message or 'name' not in message['creator']:
            return None
        
        sender_name = message['creator']['name']
        original_name = sender_name
        
        # Extract email from creator if available
        creator_email = message['creator'].get('email')
        
        if name_mappings and sender_name in name_mappings:
            sender_name = name_mappings[sender_name]
        
        # Parse timestamp
        try:
            date_str = message['created_date']
            if " at " in date_str:
                date_str = date_str.replace(" at ", " ").replace("\u202f", " ")
            timestamp = datetime.strptime(date_str, "%A, %B %d, %Y %I:%M:%S %p %Z")
        except (KeyError, ValueError) as e:
            timestamp = datetime.now()
        
        text = message.get('text', '')
        if not isinstance(text, str):
            text = str(text) if text is not None else ''
        
        # Apply anonymization to text
        if compiled_mappings and text:
            for original, replacement, word_pattern, _, _ in compiled_mappings:
                if original.lower() in text.lower():
                    if '@' in original:
                        text = re.sub(re.escape(original), replacement, text, flags=re.IGNORECASE)
                    else:
                        text = word_pattern.sub(replacement, text)
        elif name_mappings and text:
            # Fallback for backward compatibility
            sorted_mappings = sorted(name_mappings.items(), key=lambda x: len(x[0]), reverse=True)
            for original, replacement in sorted_mappings:
                if original.lower() in text.lower():
                    word_pattern = r'\b' + re.escape(original) + r'\b'
                    text = re.sub(word_pattern, replacement, text, flags=re.IGNORECASE)

        # Process attachments
        attachment_md = ""
        try:
            if 'attached_files' in message and isinstance(message['attached_files'], list):
                for f in message['attached_files']:
                    if isinstance(f, dict):
                        name = f.get('original_name', 'Attached File')
                        name = str(name)[:100]
                        attachment_md += f"\n\n> 📎 **Attachment:** `{name}`"
        except Exception:
            pass
        
        # Process reactions
        reactions_md = ""
        try:
            if 'reactions' in message and isinstance(message['reactions'], list):
                reaction_list = []
                for reaction in message['reactions']:
                    if isinstance(reaction, dict):
                        emoji = reaction.get('emoji', {}).get('unicode', '▫️')
                        count = len(reaction.get('reactor_emails', []))
                        if count > 0:
                            reaction_list.append(f"{emoji} {count}")
                if reaction_list:
                    reactions_md = "\n\n" + " ".join(reaction_list)
        except Exception:
            pass
        
        # Process quoted messages
        quote_md = ""
        try:
            if 'quoted_message_metadata' in message:
                quoted_msg = message['quoted_message_metadata']
                if isinstance(quoted_msg, dict):
                    quote_author = quoted_msg.get('creator', {}).get('name', 'Someone')
                    quote_text = quoted_msg.get('text', '...')
                    
                    if name_mappings and quote_author in name_mappings:
                        quote_author = name_mappings[quote_author]
                    
                    if isinstance(quote_text, str) and quote_text.strip():
                        quote_text = quote_text.strip()
                        
                        if compiled_mappings:
                            for original, replacement, word_pattern, _, _ in compiled_mappings:
                                if original.lower() in quote_text.lower():
                                    if '@' in original:
                                        quote_text = re.sub(re.escape(original), replacement, quote_text, flags=re.IGNORECASE)
                                    else:
                                        quote_text = word_pattern.sub(replacement, quote_text)
                        elif name_mappings:
                            sorted_mappings = sorted(name_mappings.items(), key=lambda x: len(x[0]), reverse=True)
                            for original, replacement in sorted_mappings:
                                if original.lower() in quote_text.lower():
                                    word_pattern = r'\b' + re.escape(original) + r'\b'
                                    quote_text = re.sub(word_pattern, replacement, quote_text, flags=re.IGNORECASE)
                        
                        if len(quote_text) > 100:
                            quote_text = quote_text[:100] + "..."
                        quote_md = f"> **{quote_author} said:**\n> {quote_text}\n\n"
        except Exception:
            pass

        return {
            'name': sender_name,
            'timestamp': timestamp,
            'full_text': f"{quote_md}{text}{attachment_md}{reactions_md}",
            'original_name': original_name,
            'email': creator_email
        }

    except Exception as e:
        print(f"Error parsing message: {e}")
        return None


# ===== INITIALIZATION & SETTINGS =====

def initialize_streamlit_config() -> None:
    """Initialize Streamlit page configuration and styling."""
    st.set_page_config(
        layout="wide", 
        page_title=f"{APP_TITLE} v{APP_VERSION}",
        page_icon="💬",
        initial_sidebar_state="auto"
    )


def initialize_app_settings():
    """
    Initialize application settings in Streamlit session state.
    
    Sets up customizable configuration values with defaults that can be
    modified through the UI settings panel.
    """
    if 'settings_initialized' not in st.session_state:
        # File handling settings
        st.session_state['max_file_size_mb'] = DEFAULT_MAX_FILE_SIZE_MB
        st.session_state['supported_file_types'] = DEFAULT_SUPPORTED_FILE_TYPES
        st.session_state['target_filename'] = DEFAULT_TARGET_FILENAME
        
        # Display settings
        st.session_state['messages_per_page'] = DEFAULT_MESSAGES_PER_PAGE
        st.session_state['max_preview_length'] = DEFAULT_MAX_PREVIEW_LENGTH
        
        # Anonymization settings
        st.session_state['email_domain'] = DEFAULT_EMAIL_DOMAIN
        
        st.session_state['settings_initialized'] = True


def render_settings_panel():
    """
    Render the settings configuration panel in the sidebar.
    
    Allows users to customize application behavior including:
    - File upload limits
    - Display preferences
    - Anonymization settings
    """
    with st.sidebar:
        st.header("⚙️ Settings")
        
        with st.expander("📁 File Settings", expanded=False):
            st.session_state['max_file_size_mb'] = st.number_input(
                "Max file size (MB)",
                min_value=1,
                max_value=500,
                value=st.session_state.get('max_file_size_mb', DEFAULT_MAX_FILE_SIZE_MB),
                help="Maximum allowed file size for uploads"
            )
            
            st.session_state['target_filename'] = st.text_input(
                "Target filename",
                value=st.session_state.get('target_filename', DEFAULT_TARGET_FILENAME),
                help="Primary filename to look for (from Google Takeout)"
            )
        
        with st.expander("🖥️ Display Settings", expanded=False):
            st.session_state['messages_per_page'] = st.number_input(
                "Messages per page",
                min_value=10,
                max_value=500,
                value=st.session_state.get('messages_per_page', DEFAULT_MESSAGES_PER_PAGE),
                step=10,
                help="Number of messages to display per page"
            )
            
            st.session_state['max_preview_length'] = st.number_input(
                "Max preview length",
                min_value=50,
                max_value=500,
                value=st.session_state.get('max_preview_length', DEFAULT_MAX_PREVIEW_LENGTH),
                step=10,
                help="Maximum characters for message preview"
            )
        
        with st.expander("🔒 Anonymization Settings", expanded=False):
            st.session_state['email_domain'] = st.text_input(
                "Anonymized email domain",
                value=st.session_state.get('email_domain', DEFAULT_EMAIL_DOMAIN),
                help="Domain to use for anonymized emails (e.g., example.com)"
            )
        
        # Reset to defaults button
        st.divider()
        if st.button("🔄 Reset to Defaults", help="Reset all settings to default values"):
            st.session_state['max_file_size_mb'] = DEFAULT_MAX_FILE_SIZE_MB
            st.session_state['supported_file_types'] = DEFAULT_SUPPORTED_FILE_TYPES
            st.session_state['target_filename'] = DEFAULT_TARGET_FILENAME
            st.session_state['messages_per_page'] = DEFAULT_MESSAGES_PER_PAGE
            st.session_state['max_preview_length'] = DEFAULT_MAX_PREVIEW_LENGTH
            st.session_state['email_domain'] = DEFAULT_EMAIL_DOMAIN
            st.success("✅ Settings reset to defaults")
            st.rerun()


# ===== FILE SELECTION UI =====

def select_json_file() -> Tuple[Optional[str], Optional[str]]:
    """
    Provide user interface for selecting Google Chat JSON files.
    
    Offers two methods for file selection:
    1. File upload widget for remote files
    2. Local file selection from current directory
    
    Returns:
        Tuple[Optional[str], Optional[str]]: (file_path, display_name) or (None, None)
    """
    from app import get_json_files
    
    st.subheader("📁 Select Google Chat JSON File")
    
    # Get settings
    target_filename = st.session_state.get('target_filename', DEFAULT_TARGET_FILENAME)
    supported_file_types = st.session_state.get('supported_file_types', DEFAULT_SUPPORTED_FILE_TYPES)
    
    # Informational guidance for users
    with st.container():
        st.info(f"💡 **Google Takeout Instructions**: Look for `{target_filename}` file in your Google Chat export")
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
        f"Upload your Google Chat JSON file ({target_filename} recommended):",
        type=supported_file_types,
        help=f"Select the {target_filename} file from your Google Takeout export"
    )
    
    if uploaded_file is not None:
        return handle_uploaded_file(uploaded_file)
    
    # Method 2: Local File Selection
    return handle_local_file_selection()


def handle_uploaded_file(uploaded_file) -> Tuple[Optional[str], Optional[str]]:
    """
    Process uploaded file with validation (no temp file created).
    
    Args:
        uploaded_file: Streamlit file upload object
        
    Returns:
        Tuple[Optional[str], Optional[str]]: (uploaded_file, original_name) or (None, None)
    """
    # Get settings
    max_file_size_mb = st.session_state.get('max_file_size_mb', DEFAULT_MAX_FILE_SIZE_MB)
    supported_file_types = st.session_state.get('supported_file_types', DEFAULT_SUPPORTED_FILE_TYPES)
    
    # File size validation
    max_size_bytes = max_file_size_mb * 1024 * 1024
    if uploaded_file.size > max_size_bytes:
        st.error(f"⚠️ File too large! Maximum size: {max_file_size_mb}MB (Your file: {uploaded_file.size / 1024 / 1024:.1f}MB)")
        return None, None
    
    # File type validation
    file_extension = Path(uploaded_file.name).suffix.lower()
    if file_extension not in [f".{ext}" for ext in supported_file_types]:
        st.error(f"⚠️ Unsupported file type! Supported: {', '.join(supported_file_types)}")
        return None, None
    
    # Return the uploaded file object directly (Streamlit handles it in memory)
    st.success(f"✅ File uploaded successfully: **{uploaded_file.name}**")
    
    # Show file details
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"📦 Size: {uploaded_file.size / 1024:.1f} KB")
    with col2:
        st.caption(f"📤 Source: Uploaded from browser")
    
    st.info(f"ℹ️ **Note:** Uploaded files are processed in memory. No files are saved to disk unless you choose to export anonymized data.")
    
    return uploaded_file, uploaded_file.name


def handle_local_file_selection() -> Tuple[Optional[str], Optional[str]]:
    """
    Handle local file selection from current directory.
    
    Returns:
        Tuple[Optional[str], Optional[str]]: (file_path, display_name) or (None, None)
    """
    from app import get_json_files
    
    # Get settings
    target_filename = st.session_state.get('target_filename', DEFAULT_TARGET_FILENAME)
    
    # Discover local JSON files
    json_files = get_json_files()
    
    if not json_files:
        st.info("ℹ️ No JSON files found in current directory. Use file upload above.")
        return None, None
    
    st.divider()
    st.write("**Option 2: Select Local File**")
    
    # Highlight target file if available
    if target_filename in json_files:
        st.success(f"✅ Found `{target_filename}` - this is typically the correct file!")
    
    selected_file = st.selectbox(
        "Available JSON files:",
        ["Select a file..."] + json_files,
        help=f"JSON files in current directory ({target_filename} recommended)",
        key="local_file_selector"
    )
    
    if selected_file and selected_file != "Select a file...":
        # Validate file exists
        file_path = Path(selected_file)
        if not file_path.exists():
            st.error(f"❌ File not found: {selected_file}")
            return None, None
        
        if not file_path.is_file():
            st.error(f"❌ Path is not a file: {selected_file}")
            return None, None
            
        return str(file_path), selected_file
    
    return None, None


# ===== ANONYMIZATION UI =====

def anonymize_data_interface() -> Tuple[bool, Dict[str, str], Optional[str], Optional[str]]:
    """
    Render the data anonymization configuration interface.
    
    Returns:
        Tuple[bool, Dict[str, str], Optional[str], Optional[str]]: 
        (should_anonymize, custom_mappings, save_option, anonymization_mode)
    """
    st.subheader("🔒 Data Anonymization (Optional)")
    
    # Main anonymization toggle
    anonymize = st.checkbox(
        "Enable data anonymization",
        help="Replace real names, emails, and links with anonymous identifiers for privacy protection",
        key="anonymization_enabled"
    )
    
    if not anonymize:
        return False, {}, None, None
    
    st.info("📝 **Configure your anonymization settings below:**")
    
    # Anonymization capabilities overview
    display_anonymization_features()
    
    # Mode selection interface
    mode = render_mode_selection()
    
    # Mode-specific configuration
    custom_mappings = render_mode_specific_interface(mode)
    
    # Save options
    save_option = render_save_options()
    
    return True, custom_mappings, save_option, mode


def display_anonymization_features() -> None:
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
            **📁 File & Network Paths**
            • File paths anonymized
            • Network shares protected
            • IP addresses masked
            • Attachment filenames
            • Complete privacy coverage
            """)


def render_mode_selection() -> str:
    """
    Render the anonymization mode selection interface.
    
    Returns:
        str: Selected anonymization mode ('automatic', 'manual', 'mixed')
    """
    st.subheader("🎯 Anonymization Mode")
    
    mode_options = [
        "✋ Manual - I'll specify each replacement myself"
    ]
    
    anonymization_mode = st.radio(
        "Select your anonymization strategy:",
        mode_options,
        help="Manual mode: Only names/emails you specify will be anonymized",
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
    
    # Store link settings in session state
    st.session_state['link_anonymization'] = link_anonymization
    st.session_state['link_level'] = "domain" if "Domain-aware" in link_level else "full"
    
    return "manual"  # Only manual mode supported


def render_mode_specific_interface(mode: str) -> Dict[str, str]:
    """
    Render mode-specific configuration interface.
    
    Args:
        mode: Selected anonymization mode
        
    Returns:
        Dict[str, str]: Custom mappings from user input
    """
    # Manual mode - only custom mappings
    with st.expander("🎭 Manual Anonymization Settings", expanded=True):
        st.warning("⚠️ **Manual Mode**: Only names/emails you specify below will be anonymized. All other names will remain unchanged.")
        show_custom_mapping_interface()
    
    # Extract custom mappings from session state
    return get_custom_mappings_from_session()


def render_save_options() -> str:
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
    
    # Provide context
    if save_option == "Don't save (view only)":
        st.info("💡 Data will only be displayed in the app, no file will be saved")
    elif save_option == "Save to same folder":
        st.info("📁 Anonymized file will be saved with '_anonymized' suffix")
    else:
        st.info("📂 You'll be prompted to choose a save location")
    
    return save_option


def show_custom_mapping_interface() -> None:
    """Render the custom mapping interface for user-defined anonymization rules."""
    st.markdown("""
    **📝 Create Custom Text Replacements:**
    - **👥 Names**: Replace in sender fields AND message content
    - **📧 Emails**: Custom email anonymization
    - **🏢 Organizations**: Replace company/project names
    """)
    
    # Initialize session state
    initialize_mapping_session_state()
    
    # Add new mapping section
    render_add_mapping_interface()
    
    # Bulk import section
    render_bulk_import_interface()
    
    # Display existing mappings
    render_existing_mappings()
    
    # Show preview
    render_mapping_preview()


def initialize_mapping_session_state() -> None:
    """Initialize session state for custom mappings."""
    if 'custom_mappings' not in st.session_state:
        st.session_state.custom_mappings = []


def render_add_mapping_interface() -> None:
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
        if st.button("➕ Add", help="Add this mapping"):
            handle_add_mapping(original_text, replacement_text)


def handle_add_mapping(original: str, replacement: str) -> None:
    """Handle adding a new mapping with validation."""
    if not original or not original.strip():
        st.error("❌ Original text cannot be empty")
        return
    
    if not replacement or not replacement.strip():
        st.error("❌ Replacement text cannot be empty")
        return
    
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


def render_bulk_import_interface() -> None:
    """Render the bulk import interface for custom mappings."""
    with st.expander("📥 Bulk Import Mappings (Key-Value Pairs)", expanded=False):
        st.info("Paste multiple mappings (one per line). Supported separators: `->`, `:`, `,`, `=`")
        st.caption("Format: `Original Text -> Replacement Text`")
        
        bulk_text = st.text_area(
            "Paste mappings here:", 
            height=150, 
            placeholder="John Smith -> Person A\njane@example.com : user@anon.com\nProject X, Project Alpha",
            key="bulk_mapping_input"
        )
        
        if st.button("Import Mappings", type="primary", use_container_width=True):
            if not bulk_text.strip():
                st.warning("⚠️ Please enter some text to import")
                return
                
            count = 0
            duplicates = 0
            
            # Get existing originals to check for duplicates
            existing_originals = {m['original'].lower() for m in st.session_state.custom_mappings}
            
            for line in bulk_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Try different separators
                parts = None
                if '->' in line:
                    parts = line.split('->', 1)
                elif ':' in line:
                    parts = line.split(':', 1)
                elif '=' in line:
                    parts = line.split('=', 1)
                elif ',' in line:
                    parts = line.split(',', 1)
                
                if parts and len(parts) == 2:
                    orig = parts[0].strip()
                    repl = parts[1].strip()
                    
                    if orig and repl:
                        if orig.lower() in existing_originals:
                            duplicates += 1
                        else:
                            st.session_state.custom_mappings.append({
                                'original': orig,
                                'replacement': repl
                            })
                            existing_originals.add(orig.lower())
                            count += 1
            
            if count > 0:
                st.success(f"✅ Successfully imported {count} mappings!")
                if duplicates > 0:
                    st.warning(f"⚠️ Skipped {duplicates} duplicate mappings")
                st.rerun()
            elif duplicates > 0:
                st.warning(f"⚠️ All {duplicates} mappings were duplicates and skipped")
            else:
                st.error("❌ No valid mappings found. Please check the format.")


def render_existing_mappings() -> None:
    """Render the list of existing custom mappings."""
    if not st.session_state.custom_mappings:
        st.info("💡 No custom mappings added yet. Add some above to get started!")
        return
    
    st.write("**📋 Your Custom Mappings:**")
    originals = [m['original'] for m in st.session_state.custom_mappings]
    replacements = [m['replacement'] for m in st.session_state.custom_mappings]
    duplicate_originals = {orig for orig, count in Counter(originals).items() if count > 1}
    duplicate_replacements = {rep for rep, count in Counter(replacements).items() if count > 1}

    if duplicate_originals or duplicate_replacements:
        warning_lines = []
        if duplicate_originals:
            warning_lines.append(
                "• Duplicate originals: " + ", ".join(sorted(duplicate_originals))
            )
        if duplicate_replacements:
            warning_lines.append(
                "• Duplicate replacements: " + ", ".join(sorted(duplicate_replacements))
            )
        st.warning(
            "⚠️ Duplicate mappings detected. Please review to avoid conflicting replacements.\n" + "\n".join(warning_lines)
        )
    
    for i, mapping in enumerate(st.session_state.custom_mappings):
        col1, col2, col3 = st.columns([4, 4, 1])
        is_duplicate_original = mapping['original'] in duplicate_originals
        is_duplicate_replacement = mapping['replacement'] in duplicate_replacements
        
        with col1:
            label = mapping['original']
            if is_duplicate_original:
                label += " ⚠️"
            st.write(f"**{label}**")
        
        with col2:
            label = mapping['replacement']
            if is_duplicate_replacement:
                label += " ⚠️"
            st.write(f"→ *{label}*")
        
        with col3:
            if st.button("🗑️", key=f"delete_mapping_{i}", help="Remove this mapping"):
                st.session_state.custom_mappings.pop(i)
                st.success("✅ Mapping removed")
                st.rerun()
    
    # Bulk actions
    if len(st.session_state.custom_mappings) > 1:
        st.write("")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🗑️ Clear All Mappings"):
                st.session_state.custom_mappings = []
                st.success("✅ All mappings cleared")
                st.rerun()


def render_mapping_preview() -> None:
    """Render a preview of replacements."""
    if not st.session_state.custom_mappings:
        return
    
    st.write("**👀 Replacement Preview:**")
    st.caption("These replacements will be applied to chat messages:")
    
    with st.container():
        for mapping in st.session_state.custom_mappings:
            col1, col2, col3 = st.columns([4, 1, 4])
            with col1:
                st.code(mapping['original'], language=None)
            with col2:
                st.write("→")
            with col3:
                st.code(mapping['replacement'], language=None)


def get_custom_mappings_from_session() -> Dict[str, str]:
    """Extract custom mappings from session state."""
    custom_mappings = {}
    
    if 'custom_mappings' in st.session_state and st.session_state.custom_mappings:
        for mapping in st.session_state.custom_mappings:
            if isinstance(mapping, dict) and 'original' in mapping and 'replacement' in mapping:
                original = mapping['original'].strip()
                replacement = mapping['replacement'].strip()
                if original and replacement:
                    custom_mappings[original] = replacement
    
    return custom_mappings


# ===== STATISTICS DISPLAY UI =====

def display_message_statistics(stats):
    """Display comprehensive message statistics in the UI."""
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
    
    # Detailed message counts
    st.subheader("👤 Messages per Participant")
    
    # Get name to email mapping (uses original names)
    name_to_email = stats.get('name_to_email', {})
    # Get displayed name to original name mapping
    display_to_original = stats.get('display_to_original', {})
    
    message_data = []
    for name, count in stats['message_counts'].most_common():
        percentage = (count / stats['total_messages']) * 100
        
        # Get the original name (if anonymized) to lookup email
        original_name = display_to_original.get(name, name)
        email = name_to_email.get(original_name, 'N/A')
        
        message_data.append({
            'Participant': name,
            'Email': email,
            'Messages': f"{count:,}",
            'Percentage': f"{percentage:.1f}%"
        })
    
    if message_data:
        st.write("**Message Distribution:**")
        
        for i, row in enumerate(message_data, 1):
            col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
            with col1:
                st.write(f"**{i}.** {row['Participant']}")
            with col2:
                st.write(f"📧 {row['Email']}")
            with col3:
                st.write(f"📬 {row['Messages']}")
            with col4:
                st.write(f"📊 {row['Percentage']}")
    
    # Most active day
    if stats['most_active_day']:
        most_active_date, most_active_count = stats['most_active_day']
        st.info(f"🔥 **Most Active Day:** {most_active_date.strftime('%B %d, %Y')} with {most_active_count} messages")
    
    # Date range
    date_range = stats['date_range']
    st.info(f"📅 **Chat Period:** {date_range['start'].strftime('%B %d, %Y')} to {date_range['end'].strftime('%B %d, %Y')}")
    
    # Quick anonymization interface
    st.divider()
    st.subheader("🎭 Quick Anonymization")
    
    with st.expander("✏️ Add Anonymization Mappings from Participants", expanded=False):
        st.info("💡 Select a participant from the list above and specify what to replace their name and email with")
        
        # Get list of participants for selection
        participant_names = [item['Participant'] for item in message_data]
        participant_emails = [item['Email'] for item in message_data]
        
        # Create selection options with both name and email
        participant_options = ["Select a participant..."] + [
            f"{name} ({email})" for name, email in zip(participant_names, participant_emails)
        ]
        
        col1, col2 = st.columns([3, 3])
        
        with col1:
            selected_participant = st.selectbox(
                "Select participant to anonymize:",
                participant_options,
                key="quick_anon_participant"
            )
        
        # Show input fields only if a participant is selected
        if selected_participant != "Select a participant...":
            # Extract the name and email from "Name (email)" format
            original_name = selected_participant.split(" (")[0]
            original_email = selected_participant.split(" (")[1].rstrip(")")
            name_tokens = [token for token in original_name.split() if token]
            first_initial = name_tokens[0][0] if name_tokens else ""
            last_initial = name_tokens[-1][0] if len(name_tokens) > 1 else ""
            if first_initial and last_initial:
                initials = (first_initial + last_initial).upper()
                suggested_email_local = (first_initial + last_initial).lower()
            elif first_initial:
                initials = first_initial.upper()
                suggested_email_local = first_initial.lower()
            else:
                initials = "ANON"
                suggested_email_local = "anon"
            suggested_name = initials
            suggested_email = f"{suggested_email_local}@email.com" if original_email != 'N/A' else ""
            
            # Reset defaults when participant selection changes
            last_selection = st.session_state.get('quick_anon_last_selection')
            if last_selection != selected_participant:
                st.session_state['quick_anon_last_selection'] = selected_participant
                st.session_state['quick_anon_name'] = suggested_name
                if original_email != 'N/A':
                    st.session_state['quick_anon_email'] = suggested_email
                else:
                    st.session_state['quick_anon_email'] = ""
            
            st.write("**Replace with:**")
            
            col1, col2, col3 = st.columns([3, 3, 1])
            
            with col1:
                replacement_name = st.text_input(
                    "Name:",
                    placeholder="e.g., Person A, User 1, etc.",
                    key="quick_anon_name",
                    label_visibility="visible"
                )
                st.caption(f"Original: `{original_name}`")
            
            with col2:
                replacement_email = st.text_input(
                    "Email:",
                    placeholder="e.g., persona@anon.com",
                    key="quick_anon_email",
                    disabled=original_email == 'N/A',
                    label_visibility="visible"
                )
                if original_email != 'N/A':
                    st.caption(f"Original: `{original_email}`")
                else:
                    st.caption("No email available")
            
            with col3:
                st.write("")  # Spacing
                st.write("")  # Spacing
                add_button = st.button("➕ Add", type="primary", use_container_width=True)
            
            if add_button:
                if replacement_name:
                    # Initialize custom_mappings if not exists
                    if 'custom_mappings' not in st.session_state:
                        st.session_state.custom_mappings = []
                    
                    # Add name mapping
                    st.session_state.custom_mappings.append({
                        'original': original_name,
                        'replacement': replacement_name
                    })
                    
                    # Add email mapping if email is valid and replacement provided
                    if original_email != 'N/A' and replacement_email:
                        st.session_state.custom_mappings.append({
                            'original': original_email,
                            'replacement': replacement_email
                        })
                    
                    st.success(f"✅ Added mapping: `{original_name}` → `{replacement_name}`")
                    if original_email != 'N/A' and replacement_email:
                        st.success(f"✅ Added mapping: `{original_email}` → `{replacement_email}`")
                    
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter a replacement name")
        
        # Show current mappings
        if 'custom_mappings' in st.session_state and st.session_state.custom_mappings:
            st.divider()
            st.write("**Current Mappings:**")
            for idx, mapping in enumerate(st.session_state.custom_mappings):
                col1, col2, col3 = st.columns([4, 4, 1])
                with col1:
                    st.code(mapping['original'])
                with col2:
                    st.code(mapping['replacement'])
                with col3:
                    if st.button("🗑️", key=f"quick_del_{idx}"):
                        st.session_state.custom_mappings.pop(idx)
                        st.rerun()
    
    return message_data


# ===== MESSAGE DISPLAY UI =====

def display_processed_messages(data: Dict[str, Any], name_mappings: Dict[str, str]) -> None:
    """
    Process and display chat messages with pagination.
    
    Args:
        data: Chat data (original or anonymized)  
        name_mappings: Anonymization mappings applied
    """
    
    # Pre-compile mappings for display performance
    compiled_mappings = compile_mappings(name_mappings) if name_mappings else None
    
    # Process messages with progress tracking
    parsed_messages = []
    progress_bar = st.progress(0)
    total_messages = len(data.get('messages', []))
    
    if total_messages == 0:
        st.warning("⚠️ No messages found in the data.")
        return
    
    with st.spinner("📝 Processing messages..."):
        for i, msg in enumerate(data['messages']):
            parsed_msg = parse_chat_message(msg, name_mappings, compiled_mappings)
            if parsed_msg:
                parsed_messages.append(parsed_msg)
            
            # Update progress every 100 messages
            if i % 100 == 0:
                progress_bar.progress((i + 1) / total_messages)
    
    progress_bar.progress(1.0)
    
    if not parsed_messages:
        st.warning("⚠️ No valid chat messages found.")
        return

    # Sort messages by timestamp
    sorted_messages = sorted(parsed_messages, key=lambda x: x['timestamp'])
    
    st.success(f"🎉 Successfully processed **{len(sorted_messages):,}** messages!")
    
    st.divider()
    
    # Display messages with pagination
    st.subheader("💬 Chat Messages")
    
    messages_per_page = st.session_state.get('messages_per_page', DEFAULT_MESSAGES_PER_PAGE)
    
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
    
    # Display messages
    for msg in page_messages:
        with st.chat_message(name=msg['name']):
            st.markdown(msg['full_text'], unsafe_allow_html=True)
            st.caption(msg['timestamp'].strftime("%b %d, %Y at %I:%M %p"))


# ===== APPLICATION HEADER UI =====

def render_application_header() -> None:
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


def render_usage_instructions() -> None:
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
        
        3. **📦 Export Settings**
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
        
        **📖 Official Documentation:** [Google Takeout Help](https://support.google.com/accounts/answer/3024190)
        """)


def load_and_validate_chat_data(file_path, display_name: str) -> Optional[Dict[str, Any]]:
    """
    Load and validate Google Chat JSON data with UI feedback.
    
    Args:
        file_path: Path to JSON file (string) or file object from upload
        display_name: User-friendly name for display
        
    Returns:
        Optional[Dict[str, Any]]: Parsed JSON data or None
    """
    # Show file info
    if isinstance(file_path, str):
        st.info(f"📄 Loading: **{display_name}**")
        st.caption(f"📁 Path: `{Path(file_path).absolute()}`")
    else:
        st.info(f"📄 Loading uploaded file: **{display_name}**")
    
    try:
        # Handle both file paths (strings) and file objects (from upload)
        if isinstance(file_path, str):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            # File object from upload
            data = json.load(file_path)
        
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
        
        # Add clear/reset button
        col1, col2, col3 = st.columns([2, 2, 1])
        with col3:
            if st.button("🗑️ Clear", help="Clear loaded data and reset app", type="secondary", use_container_width=True):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.cache_data.clear()
                st.success("✅ Memory cleared!")
                st.rerun()
        
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
