# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Added
- Initial release of email-to-remarkable-sync
- Email monitoring via IMAP for PDF attachments
- Automatic upload to reMarkable cloud storage
- Configurable destination folders on reMarkable
- Environment variable based configuration
- Comprehensive error handling and logging
- Email marking as read after successful processing
- Support for multiple email providers (Gmail, FastMail, etc.)
- Command-line interface via `email-to-remarkable` command
- Programmatic API for integration into other applications
- Comprehensive test suite with pytest
- Type hints and mypy support
- Code formatting with black and isort
- Development tooling with Makefile
- MIT license for open source usage

### Features
- **Email Integration**: Connect to any IMAP-compatible email server
- **PDF Processing**: Automatically extract and process PDF attachments
- **reMarkable Sync**: Upload documents directly to reMarkable cloud
- **Smart Organization**: Organize files into folders automatically
- **Reliability**: Only mark emails as read after successful upload
- **Security**: Environment variable configuration for sensitive data
- **Extensibility**: Clean, well-documented codebase for contributions

### Documentation
- Comprehensive README with setup instructions
- Configuration guide for various email providers
- Troubleshooting section for common issues
- Development guide for contributors
- API documentation with examples
- Security best practices