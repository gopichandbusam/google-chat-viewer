# Security Policy

## Reporting Security Vulnerabilities

The Google Chat Viewer team takes security seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report a Security Vulnerability

If you believe you have found a security vulnerability in Google Chat Viewer, please report it to us through coordinated disclosure.

**Please do NOT report security vulnerabilities through public GitHub issues, discussions, or pull requests.**

Instead, please send an email to: **gopichand.busam@nyu.edu**

Please include as much of the information listed below as you can to help us better understand and resolve the issue:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
- **Initial Assessment**: We will provide an initial assessment within 5 business days
- **Updates**: We will keep you informed of our progress throughout the investigation
- **Resolution**: We aim to resolve critical issues within 30 days
- **Credit**: We will credit you in our security advisory (unless you prefer to remain anonymous)

## Security Considerations for Users

### Data Privacy

Google Chat Viewer is designed with privacy in mind:

- **Local Processing**: All data processing happens locally on your machine
- **No Network Requests**: The application doesn't send data to external servers
- **Temporary Files**: Any temporary files are cleaned up after processing
- **Anonymization**: Built-in features to protect sensitive information

### Safe Usage Practices

1. **Verify Data Sources**: Only process Google Takeout files from trusted sources
2. **Check File Contents**: Review uploaded files before processing
3. **Secure Environment**: Use the application in a secure environment
4. **Clean Up**: Remove processed files when no longer needed
5. **Regular Updates**: Keep the application updated to the latest version

### Known Security Limitations

- **File Upload**: The application processes user-uploaded JSON files - ensure files are from trusted sources
- **Regex Processing**: Complex regex patterns may be susceptible to ReDoS attacks with malicious input
- **Local Storage**: Processed data is stored locally - secure your filesystem accordingly

## Security Features

### Input Validation

- **File Type Validation**: Only accepts valid JSON files
- **Content Validation**: Verifies Google Takeout format structure
- **Size Limits**: Reasonable limits on file size and processing time
- **Sanitization**: Input data is sanitized before processing

### Error Handling

- **Graceful Failures**: Errors are handled gracefully without exposing sensitive information
- **Logging**: Minimal logging to avoid sensitive data leakage
- **User Feedback**: Clear error messages without system details

### Dependencies

- **Regular Updates**: Dependencies are regularly updated for security patches
- **Minimal Dependencies**: We keep dependencies to a minimum to reduce attack surface
- **Vulnerability Scanning**: Regular scanning of dependencies for known vulnerabilities

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.0.x   | :warning: Limited  |
| < 1.0   | :x:                |

We strongly recommend using the latest version for the best security posture.

## Security Updates

Security updates will be released as follows:

- **Critical**: Within 24-48 hours
- **High**: Within 1 week
- **Medium**: Next minor release
- **Low**: Next major release

All security updates will be clearly marked in the [CHANGELOG.md](CHANGELOG.md) and GitHub releases.

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Google's Responsible Disclosure](https://security.google.com/)
- [GitHub Security Advisories](https://docs.github.com/en/code-security/security-advisories)

---

Thank you for helping keep Google Chat Viewer and our users safe!