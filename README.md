# Email to reMarkable Sync

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python tool that monitors an email mailbox for PDF attachments and automatically uploads them to your reMarkable cloud storage. Perfect for sending articles, documents, and papers directly to your reMarkable tablet via email.

## Features

- 📧 **Email Integration**: Monitors any IMAP-compatible email account
- 📁 **Smart Organization**: Upload PDFs to specific folders on your reMarkable
- 🔄 **Automatic Processing**: Only processes unread emails and marks them as read after successful upload
- 🛡️ **Reliable**: Comprehensive error handling and logging
- 🧪 **Well Tested**: Extensive test coverage
- ⚙️ **Configurable**: Environment variable configuration for security
- 📦 **Easy Install**: Pip installable package

## Quick Start

### Prerequisites

This project uses [Poetry](https://python-poetry.org/) for dependency management. Install Poetry first:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Installation

#### From GitHub:
```bash
pip install git+https://github.com/shano/email-to-remarkable-sync.git
```

#### From source:
```bash
git clone https://github.com/shano/email-to-remarkable-sync.git
cd email-to-remarkable-sync
poetry install
```

#### Development setup:
```bash
git clone https://github.com/shano/email-to-remarkable-sync.git
cd email-to-remarkable-sync
make setup  # This runs poetry install and sets up pre-commit hooks
```

### Configuration

Set up your environment variables:

```bash
export IMAP_SERVER="imap.gmail.com"
export EMAIL_USERNAME="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
export MAILBOX_TO_CHECK="remarkable"  # Optional: defaults to INBOX
export REMARKABLE_DEST_FOLDER="From Email"  # Optional: folder name on reMarkable
export REMARKABLE_TOKEN="your-remarkable-device-token"
```

### Usage

#### Command Line

If installed globally:
```bash
email-to-remarkable
```

If using Poetry (recommended for development):
```bash
poetry run email-to-remarkable
```

Or activate the Poetry shell first:
```bash
poetry shell
email-to-remarkable
```

#### Programmatic Usage

```python
from email_to_remarkable import EmailToRemarkableSync, load_config

config = load_config()
sync = EmailToRemarkableSync(config)
success = sync.process_emails()
```

## Configuration Options

All configuration is done via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `IMAP_SERVER` | IMAP server hostname | `imap.gmail.com` |
| `EMAIL_USERNAME` | Email username/address | *Required* |
| `EMAIL_PASSWORD` | Email password or app password | *Required* |
| `MAILBOX_TO_CHECK` | Mailbox/folder to monitor | `INBOX` |
| `DOWNLOAD_DIR` | Temporary download directory | `/tmp/downloaded_pdfs` |
| `REMARKABLE_DEST_FOLDER` | Destination folder on reMarkable | `From Email` |
| `REMARKABLE_TOKEN` | reMarkable device token | *Required* |
| `REMARKABLE_TOKEN_PATH` | Path to token file (alternative to token env var) | `/etc/remarkable/token` |
| `RM_SYNC_FILE_PATH` | reMarkable API sync file path | `/tmp/rm_api_sync` |
| `RM_LOG_FILE` | reMarkable API log file path | `/tmp/rm_api.log` |

## Getting Your reMarkable Token

1. Install the reMarkable API package: `pip install rm-api`
2. Run the registration process:
   ```bash
   python -c "from rm_api import API; api = API(); print('Token saved!')"
   ```
3. Follow the prompts to connect to your reMarkable account
4. Your token will be saved and you can extract it for use in this tool

## Email Provider Setup

### Gmail

1. Enable 2-factor authentication on your Google account
2. Generate an App Password:
   - Go to Google Account settings → Security → App passwords
   - Generate a password for "Mail"
   - Use this app password (not your regular password) for `EMAIL_PASSWORD`

### Other Providers

Most IMAP-compatible email providers work. Common IMAP servers:

- **FastMail**: `imap.fastmail.com`
- **Yahoo**: `imap.mail.yahoo.com`
- **Outlook/Hotmail**: `outlook.office365.com`
- **Apple iCloud**: `imap.mail.me.com`

## How It Works

1. **Connect**: Connects to your email account via IMAP
2. **Scan**: Looks for unread emails in the specified mailbox
3. **Extract**: Downloads any PDF attachments from those emails
4. **Upload**: Uploads PDFs to your reMarkable cloud storage
5. **Organize**: Places files in the specified folder (creates if needed)
6. **Mark**: Marks emails as read only after successful upload
7. **Cleanup**: Removes temporary files

## Development

This project uses **Poetry** for dependency management and packaging.

### Setup Development Environment

```bash
git clone https://github.com/shano/email-to-remarkable-sync.git
cd email-to-remarkable-sync
make setup  # Installs dependencies and pre-commit hooks
```

Or manually:
```bash
poetry install
poetry run pre-commit install
```

### Available Commands

```bash
make help          # Show all available commands
make install       # Install dependencies with Poetry
make test          # Run tests
make test-coverage # Run tests with coverage
make lint          # Check code style
make format        # Format code
make type-check    # Run type checking
make all-checks    # Run all quality checks
make pre-commit    # Run pre-commit hooks
make build         # Build package
make shell         # Activate Poetry shell
make update        # Update dependencies
make quick-start   # Setup and test in one command
```

### Running Tests

```bash
make test
# or
poetry run pytest tests/ -v
# or (in Poetry shell)
poetry shell
pytest tests/ -v
```

### Working with Poetry

```bash
# Activate Poetry shell (recommended for development)
poetry shell

# Add new dependency
poetry add requests

# Add development dependency  
poetry add --group dev pytest-xdist

# Update dependencies
poetry update

# Show dependency tree
poetry show --tree

# Build package
poetry build
```

### Code Style

This project uses:
- **Poetry** for dependency management
- **Black** for code formatting  
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **pre-commit** for git hooks

Run `make format` to automatically format code, or `make all-checks` to verify everything.

## Docker Usage

You can also run this as a Docker container. Create a `.env` file:

```env
IMAP_SERVER=imap.gmail.com
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
REMARKABLE_TOKEN=your-token
REMARKABLE_DEST_FOLDER=From Email
```

## Troubleshooting

### Common Issues

**"Authentication failed"**
- Check your email credentials
- For Gmail, ensure you're using an App Password, not your regular password
- Verify IMAP is enabled in your email account settings

**"reMarkable token not found"**
- Ensure you have a valid reMarkable device token
- Check that the token file path is correct or the environment variable is set

**"Destination folder not found"**
- The folder will be created automatically on first upload
- Check that the folder name matches exactly (case-sensitive)

**"No PDF attachments found"**
- Ensure emails contain PDF attachments (not just links to PDFs)
- Check that the MIME type is correctly set as `application/pdf`

### Debug Mode

Set environment variable for verbose logging:

```bash
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from email_to_remarkable import EmailToRemarkableSync, load_config
sync = EmailToRemarkableSync(load_config())
sync.process_emails()
"
```

## Security Notes

- Store sensitive configuration (passwords, tokens) in environment variables, not in code
- Use app passwords instead of your main email password when possible
- Regularly rotate your reMarkable device token
- Be careful with file permissions on token files

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the test suite (`make all-checks`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [rm-api](https://github.com/subutux/rm-api) for reMarkable cloud API access
- The reMarkable team for creating an amazing device
- All contributors who help improve this tool

## Related Projects

- [reMarkable API](https://github.com/subutux/rm-api) - Python API for reMarkable cloud
- [rmscene](https://github.com/ricklupton/rmscene) - Tools for reading reMarkable files
- [remarkable-fs](https://github.com/nick8325/remarkable-fs) - FUSE filesystem for reMarkable

---

**Note**: This is an unofficial tool and is not affiliated with reMarkable AS.