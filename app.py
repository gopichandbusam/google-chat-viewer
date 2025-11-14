"""
Google Chat Viewer and Anonymizer - Core Logic Module

This module contains all core data processing logic for the Google Chat Viewer application.
UI components are separated in ui.py for better maintainability.

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
"""

# Standard library imports
import json
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
DEFAULT_MAX_FILE_SIZE_MB = 200
DEFAULT_SUPPORTED_FILE_TYPES = ['json']
DEFAULT_TARGET_FILENAME = "messages.json"

# Display configuration
DEFAULT_MESSAGES_PER_PAGE = 50
DEFAULT_MAX_PREVIEW_LENGTH = 100

# Anonymization configuration
DEFAULT_EMAIL_DOMAIN = "example.com"
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Google Drive link patterns
DRIVE_LINK_PATTERNS = {
    'docs': r'https://docs\.google\.com/document/d/([a-zA-Z0-9-_]+)',
    'sheets': r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)', 
    'slides': r'https://docs\.google\.com/presentation/d/([a-zA-Z0-9-_]+)',
    'forms': r'https://docs\.google\.com/forms/d/([a-zA-Z0-9-_]+)',
    'drive': r'https://drive\.google\.com/(?:file/d/|open\?id=)([a-zA-Z0-9-_]+)'
}
# =====================================


# ===== FILE HANDLING =====

def get_json_files() -> List[str]:
    """
    Discover and prioritize JSON files in the current directory.
    
    Returns:
        List[str]: Sorted list of JSON filenames with messages.json first
    """
    try:
        current_dir = Path.cwd()
        json_files = list(current_dir.glob("*.json"))
        
        if not json_files:
            return []
        
        target_filename = st.session_state.get('target_filename', DEFAULT_TARGET_FILENAME)
        
        # Prioritize messages.json files
        messages_files = [f.name for f in json_files if f.name.lower() == target_filename.lower()]
        other_files = sorted([f.name for f in json_files if f.name.lower() != target_filename.lower()])
        
        return messages_files + other_files
        
    except (OSError, PermissionError) as e:
        st.error(f"❌ Error accessing directory: {e}")
        return []


# ===== ANONYMIZATION CORE LOGIC =====

def create_anonymization_mappings(data: Dict[str, Any], custom_mappings: Optional[Dict[str, str]] = None, 
                                mode: str = "manual") -> Dict[str, str]:
    """
    Generate anonymization mappings for names and emails.
    
    Manual mode only - only user-specified mappings are created.
    
    Args:
        data: Parsed JSON data containing Google Chat messages
        custom_mappings: User-defined mappings (already a dict of original->replacement)
        mode: Anonymization strategy (only "manual" supported)
        
    Returns:
        Dict[str, str]: Mapping dictionary
    """
    if mode != "manual":
        st.warning("⚠️ Only manual mode is supported. Using manual mode.")
        mode = "manual"
    
    if custom_mappings is None:
        custom_mappings = {}
    
    try:
        names, emails = _extract_entities_from_messages(data)
        
        # Manual mode: return custom mappings as-is
        # custom_mappings is already a dict of {original: replacement}
        all_mappings = dict(custom_mappings)
        
        # Log statistics
        print(f"Anonymization Statistics:")
        print(f"  Mode: {mode}")
        print(f"  Names found: {len(names)}")
        print(f"  Emails found: {len(emails)}")
        print(f"  Total entities: {len(names) + len(emails)}")
        print(f"  Entities mapped: {len(all_mappings)}")
        
        return all_mappings
        print(f"  Entities mapped: {len(all_mappings)}")
        
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
        # Extract names
        if 'creator' in message and 'name' in message['creator']:
            creator_name = message['creator']['name'].strip()
            if creator_name:
                names.add(creator_name)
        
        # Extract emails
        if 'text' in message and message['text']:
            text = message['text']
            found_emails = re.findall(EMAIL_PATTERN, text)
            valid_emails = {email.strip().lower() for email in found_emails if '@' in email and '.' in email.split('@')[1]}
            emails.update(valid_emails)
    
    return names, emails


def anonymize_all_links(text: str, anonymization_level: str = "domain") -> str:
    """
    Anonymize all types of links and URLs in text content.
    
    Args:
        text: Input text that may contain links/URLs
        anonymization_level: "domain" (preserve service type) or "full" (generic)
        
    Returns:
        str: Text with all links anonymized
    """
    if not text or not isinstance(text, str):
        return text
    
    # Comprehensive link patterns
    link_patterns = {
        'google_docs': (r'https://docs\.google\.com/document/d/[a-zA-Z0-9-_]+[^\s]*', '[DOCS_LINK]'),
        'google_sheets': (r'https://docs\.google\.com/spreadsheets/d/[a-zA-Z0-9-_]+[^\s]*', '[SHEETS_LINK]'),
        'google_slides': (r'https://docs\.google\.com/presentation/d/[a-zA-Z0-9-_]+[^\s]*', '[SLIDES_LINK]'),
        'google_forms': (r'https://docs\.google\.com/forms/d/[a-zA-Z0-9-_]+[^\s]*', '[FORMS_LINK]'),
        'google_drive': (r'https://drive\.google\.com/[^\s]*', '[DRIVE_LINK]'),
        'google_meet': (r'https://meet\.google\.com/[^\s]*', '[MEET_LINK]'),
        'github': (r'https://(?:www\.)?github\.com/[^\s]*', '[GITHUB_LINK]'),
        'slack': (r'https://[a-zA-Z0-9.-]+\.slack\.com/[^\s]*', '[SLACK_LINK]'),
        'zoom': (r'https://[a-zA-Z0-9.-]*\.zoom\.us/[^\s]*', '[ZOOM_LINK]'),
        'generic_https': (r'https://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\s]*', '[HTTPS_LINK]'),
        'generic_http': (r'http://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\s]*', '[HTTP_LINK]'),
    }
    
    if anonymization_level == "full":
        generic_replacements = {
            'web_url': (r'https?://[^\s]+', '[LINK]'),
            'email': (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
        }
        
        for pattern_name, (pattern, replacement) in generic_replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    else:
        for service_name, (pattern, replacement) in link_patterns.items():
            if re.search(pattern, text, flags=re.IGNORECASE):
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


def apply_anonymization(data: Dict[str, Any], name_mappings: Dict[str, str]) -> Dict[str, Any]:
    """
    Apply comprehensive anonymization to Google Chat data.
    
    Args:
        data: Original parsed JSON chat data
        name_mappings: Dictionary mapping original terms to replacements
        
    Returns:
        Dict[str, Any]: Fully anonymized copy of the original data
    """
    try:
        anonymized_data = json.loads(json.dumps(data))  # Deep copy
        
        # Sort mappings by length (longest first)
        sorted_mappings = sorted(name_mappings.items(), key=lambda x: len(x[0]), reverse=True)
        
        # Anonymize messages
        for message in anonymized_data.get('messages', []):
            # 1. Anonymize creator names and emails
            if 'creator' in message:
                if 'name' in message['creator']:
                    original_name = message['creator']['name']
                    if original_name in name_mappings:
                        message['creator']['name'] = name_mappings[original_name]
                
                if 'email' in message['creator']:
                    original_email = message['creator']['email']
                    if original_email in name_mappings:
                        message['creator']['email'] = name_mappings[original_email]
            
            # 2. Anonymize quoted messages
            if 'quoted_message_metadata' in message:
                quoted_creator = message['quoted_message_metadata'].get('creator', {})
                if 'name' in quoted_creator:
                    original_name = quoted_creator['name']
                    if original_name in name_mappings:
                        quoted_creator['name'] = name_mappings[original_name]
                
                if 'email' in quoted_creator:
                    original_email = quoted_creator['email']
                    if original_email in name_mappings:
                        quoted_creator['email'] = name_mappings[original_email]
                
                if 'text' in message['quoted_message_metadata']:
                    quoted_text = message['quoted_message_metadata']['text']
                    for original, replacement in sorted_mappings:
                        # Handle emails differently from names
                        if '@' in original:
                            email_pattern = re.escape(original)
                            quoted_text = re.sub(email_pattern, replacement, quoted_text, flags=re.IGNORECASE)
                        else:
                            quoted_text = re.sub(r'\b' + re.escape(original) + r'\b', replacement, quoted_text, flags=re.IGNORECASE)
                    
                    if st.session_state.get('link_anonymization', True):
                        link_level = st.session_state.get('link_level', 'domain')
                        quoted_text = anonymize_all_links(quoted_text, link_level)
                    message['quoted_message_metadata']['text'] = quoted_text
            
            # 3. Anonymize main message text
            if 'text' in message and message['text']:
                text = message['text']
                
                for original, replacement in sorted_mappings:
                    if original.lower() in text.lower():
                        # Check if it's an email address (contains @)
                        if '@' in original:
                            # For emails, use a simpler pattern that doesn't require word boundaries
                            email_pattern = re.escape(original)
                            text = re.sub(email_pattern, replacement, text, flags=re.IGNORECASE)
                        else:
                            # For names, use word boundaries
                            word_pattern = r'\b' + re.escape(original) + r'\b'
                            text = re.sub(word_pattern, replacement, text, flags=re.IGNORECASE)
                            
                            # Punctuation-aware
                            punct_pattern = r'(?<=["\'\s])' + re.escape(original) + r'(?=["\'\s\.,!?])'
                            text = re.sub(punct_pattern, replacement, text, flags=re.IGNORECASE)
                            
                            # Exact match for multi-word
                            if len(original.split()) > 1:
                                exact_pattern = re.escape(original)
                                text = re.sub(exact_pattern, replacement, text, flags=re.IGNORECASE)
                
                # Anonymize links
                if st.session_state.get('link_anonymization', True):
                    link_level = st.session_state.get('link_level', 'domain')
                    text = anonymize_all_links(text, link_level)
                
                message['text'] = text
            
            # 4. Anonymize reactions (reactor emails)
            if 'reactions' in message:
                for reaction in message['reactions']:
                    if 'reactor_emails' in reaction:
                        anonymized_reactor_emails = []
                        for email in reaction['reactor_emails']:
                            if email in name_mappings:
                                anonymized_reactor_emails.append(name_mappings[email])
                            else:
                                anonymized_reactor_emails.append(email)
                        reaction['reactor_emails'] = anonymized_reactor_emails
            
            # 5. Anonymize attachments
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
        return data


def save_anonymized_data(data, original_filename, save_option):
    """Save anonymized data based on user preference."""
    if save_option == "Don't save (view only)":
        return
    
    try:
        name_parts = original_filename.rsplit('.', 1)
        if len(name_parts) == 2:
            anonymized_filename = f"{name_parts[0]}_anonymized.{name_parts[1]}"
        else:
            anonymized_filename = f"{original_filename}_anonymized"
        
        if save_option == "Save to same folder":
            with open(anonymized_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            st.success(f"✅ Anonymized data saved as: `{anonymized_filename}`")
            
        elif save_option == "Ask me where to save":
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            st.info("💾 **Click the button below to download and choose where to save:**")
            st.download_button(
                label="📥 Download Anonymized Data",
                data=json_str,
                file_name=anonymized_filename,
                mime="application/json",
                help="Click to download - your browser will ask where to save the file",
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"❌ Error saving anonymized data: {e}")


# ===== STATISTICS =====

def create_message_statistics(messages):
    """Create comprehensive statistics about the messages."""
    if not messages:
        return {}
    
    try:
        message_counts = Counter(msg['name'] for msg in messages)
        original_counts = Counter(msg.get('original_name', msg['name']) for msg in messages)
        
        # Create name to email mapping (using original names)
        name_to_email = {}
        # Create displayed name to original name mapping
        display_to_original = {}
        
        for msg in messages:
            original_name = msg.get('original_name', msg['name'])
            displayed_name = msg['name']
            email = msg.get('email')
            
            if email and original_name not in name_to_email:
                name_to_email[original_name] = email
            
            if displayed_name != original_name and displayed_name not in display_to_original:
                display_to_original[displayed_name] = original_name
        
        timestamps = [msg['timestamp'] for msg in messages]
        date_range = {
            'start': min(timestamps),
            'end': max(timestamps),
            'total_days': (max(timestamps) - min(timestamps)).days + 1
        }
        
        dates = [ts.date() for ts in timestamps]
        daily_counts = Counter(dates)
        most_active_day = daily_counts.most_common(1)[0] if daily_counts else None
        
        return {
            'message_counts': message_counts,
            'original_counts': original_counts,
            'name_to_email': name_to_email,
            'display_to_original': display_to_original,
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


# ===== MESSAGE PARSING =====

def parse_chat_message(message, name_mappings=None):
    """Parse a single message from JSON and extract key data."""
    try:
        if not isinstance(message, dict):
            return None
            
        if 'creator' not in message or 'name' not in message['creator']:
            return None
        
        sender_name = message['creator']['name']
        original_name = sender_name
        
        # Extract email from creator if available
        creator_email = None
        if 'email' in message['creator']:
            creator_email = message['creator']['email']
        
        if name_mappings and sender_name in name_mappings:
            sender_name = name_mappings[sender_name]
        
        # Parse timestamp
        try:
            date_str = message['created_date']
            date_str_clean = date_str.replace(" at ", " ").replace("\u202f", " ")
            date_format = "%A, %B %d, %Y %I:%M:%S %p %Z"
            timestamp = datetime.strptime(date_str_clean, date_format)
        except (KeyError, ValueError) as e:
            timestamp = datetime.now()
            print(f"Warning: Could not parse date: {e}")
        
        text = message.get('text', '')
        if not isinstance(text, str):
            text = str(text) if text is not None else ''
        
        # Apply anonymization to text
        if name_mappings and text:
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
        except Exception as e:
            print(f"Warning: Error processing attachments: {e}")
        
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
        except Exception as e:
            print(f"Warning: Error processing reactions: {e}")
        
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
                        
                        if name_mappings:
                            sorted_mappings = sorted(name_mappings.items(), key=lambda x: len(x[0]), reverse=True)
                            for original, replacement in sorted_mappings:
                                if original.lower() in quote_text.lower():
                                    word_pattern = r'\b' + re.escape(original) + r'\b'
                                    quote_text = re.sub(word_pattern, replacement, quote_text, flags=re.IGNORECASE)
                        
                        if len(quote_text) > 100:
                            quote_text = quote_text[:100] + "..."
                        quote_md = f"> **{quote_author} said:**\n> {quote_text}\n\n"
        except Exception as e:
            print(f"Warning: Error processing quoted message: {e}")

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


# ===== MAIN APPLICATION =====

def main() -> None:
    """Main Streamlit application entry point."""
    # Import UI functions
    from ui import (
        initialize_streamlit_config, initialize_app_settings, render_settings_panel,
        render_application_header, render_usage_instructions,
        select_json_file, load_and_validate_chat_data,
        anonymize_data_interface, display_message_statistics,
        display_processed_messages
    )
    
    # Initialize
    initialize_streamlit_config()
    initialize_app_settings()
    render_settings_panel()
    render_application_header()
    render_usage_instructions()
    
    # File selection
    selected_file, display_name = select_json_file()
    if not selected_file:
        st.info("👆 Please select a JSON file to continue")
        st.stop()
    
    # Load data
    data = load_and_validate_chat_data(selected_file, display_name)
    if not data:
        return
    
    # Anonymization
    should_anonymize, custom_mappings, save_option, anonymization_mode = anonymize_data_interface()
    
    name_mappings = {}
    if should_anonymize:
        with st.spinner("🔒 Creating anonymization mappings..."):
            name_mappings = create_anonymization_mappings(data, custom_mappings, anonymization_mode)
            
        if name_mappings:
            st.success(f"✅ Created {len(name_mappings)} anonymization mappings")
        else:
            st.info("ℹ️ No anonymization mappings created")
    
    # Statistics
    with st.spinner("📊 Generating statistics..."):
        # Parse messages first for statistics
        parsed_messages = []
        for msg in data['messages']:
            parsed_msg = parse_chat_message(msg, name_mappings)
            if parsed_msg:
                parsed_messages.append(parsed_msg)
        
        stats = create_message_statistics(parsed_messages)
    
    display_message_statistics(stats)
    
    # Apply anonymization to data
    display_data = data
    if should_anonymize:
        if name_mappings:
            with st.spinner("🔄 Applying anonymization..."):
                display_data = apply_anonymization(data, name_mappings)
            st.success("✅ Anonymization applied successfully!")
        else:
            st.info("ℹ️ No anonymization mappings were created. The downloaded file will match the original data.")
        
        # Prepare filename
        name_parts = display_name.rsplit('.', 1)
        if len(name_parts) == 2:
            anonymized_filename = f"{name_parts[0]}_anonymized.{name_parts[1]}"
        else:
            anonymized_filename = f"{display_name}_anonymized"
        
        # Show download button for current display data
        json_str = json.dumps(display_data, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Download Anonymized Data",
            data=json_str,
            file_name=anonymized_filename,
            mime="application/json",
            help="Download the processed chat data as JSON",
            use_container_width=True,
            type="primary"
        )

        # Preview anonymized data (first 50 lines) with option to expand
        preview_lines = json_str.splitlines()
        preview_snippet = "\n".join(preview_lines[:50]) if preview_lines else ""
        st.write("**📄 Anonymized Data Preview (first 50 lines)**")
        st.code(preview_snippet or "(empty)", language="json")
        if len(preview_lines) > 50:
            with st.expander("Show full anonymized JSON"):
                st.code(json_str, language="json")
        
        # Optional: Also save to same folder if requested (only when data changed)
        if save_option == "Save to same folder" and name_mappings:
            try:
                with open(anonymized_filename, 'w', encoding='utf-8') as f:
                    json.dump(display_data, f, indent=2, ensure_ascii=False)
                st.info(f"💾 Also saved to same folder as: `{anonymized_filename}`")
            except Exception as e:
                st.warning(f"⚠️ Could not save to folder: {e}")
    
    # Display messages
    display_processed_messages(display_data, name_mappings)


if __name__ == "__main__":
    main()
