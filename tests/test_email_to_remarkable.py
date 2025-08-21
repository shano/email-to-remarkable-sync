#!/usr/bin/env python3
"""
Tests for email_to_remarkable module.
"""

import os
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from email_to_remarkable import EmailToRemarkableSync, load_config


class TestEmailToRemarkableSync:
    """Test cases for EmailToRemarkableSync class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = {
            "imap_server": "imap.test.com",
            "email_username": "test@example.com",
            "email_password": "test_password",
            "mailbox_to_check": "test_inbox",
            "remarkable_dest_folder": "Test Folder",
            "download_dir": "/tmp/test_downloads",
            "remarkable_token": "test_token",
        }

    def test_init_with_valid_config(self):
        """Test initialization with valid configuration."""
        sync = EmailToRemarkableSync(self.test_config)
        assert sync.config == self.test_config

    def test_init_with_invalid_config(self):
        """Test initialization with invalid configuration."""
        invalid_config = self.test_config.copy()
        del invalid_config["imap_server"]

        with pytest.raises(ValueError, match="Required configuration key 'imap_server' is missing"):
            EmailToRemarkableSync(invalid_config)

    def test_init_with_empty_password(self):
        """Test initialization with empty password."""
        invalid_config = self.test_config.copy()
        invalid_config["email_password"] = ""

        with pytest.raises(ValueError, match="Email password is required but not provided"):
            EmailToRemarkableSync(invalid_config)

    def test_decode_subject_simple(self):
        """Test email subject decoding with simple text."""
        sync = EmailToRemarkableSync(self.test_config)
        result = sync.decode_subject("Simple Subject")
        assert result == "Simple Subject"

    def test_decode_subject_encoded(self):
        """Test email subject decoding with encoded text."""
        sync = EmailToRemarkableSync(self.test_config)

        # Mock decode_header to return encoded content
        with patch("email_to_remarkable.decode_header") as mock_decode:
            mock_decode.return_value = [(b"Encoded Subject", "utf-8")]
            result = sync.decode_subject("=?utf-8?B?RW5jb2RlZCBTdWJqZWN0?=")
            assert result == "Encoded Subject"

    @patch("email_to_remarkable.API")
    def test_setup_remarkable_api_with_token(self, mock_api_class):
        """Test reMarkable API setup with token in config."""
        mock_api = Mock()
        mock_api_class.return_value = mock_api

        sync = EmailToRemarkableSync(self.test_config)

        with patch("builtins.print"):
            result = sync._setup_remarkable_api()

        assert result == mock_api
        mock_api_class.assert_called_once()
        mock_api.get_documents.assert_called_once()

    @patch("email_to_remarkable.API")
    def test_setup_remarkable_api_with_token_file(self, mock_api_class):
        """Test reMarkable API setup with token file."""
        mock_api = Mock()
        mock_api_class.return_value = mock_api

        config = self.test_config.copy()
        del config["remarkable_token"]
        config["remarkable_token_path"] = "/test/token/path"

        sync = EmailToRemarkableSync(config)

        with patch("builtins.open", mock_open(read_data="file_token")):
            with patch("builtins.print"):
                result = sync._setup_remarkable_api()

        assert result == mock_api
        assert mock_api.token == "file_token"

    @patch("email_to_remarkable.API")
    def test_setup_remarkable_api_token_file_not_found(self, mock_api_class):
        """Test reMarkable API setup when token file not found."""
        config = self.test_config.copy()
        del config["remarkable_token"]

        sync = EmailToRemarkableSync(config)

        with patch("builtins.open", side_effect=FileNotFoundError):
            with patch("builtins.print"):
                result = sync._setup_remarkable_api()

        assert result is None

    def test_upload_to_remarkable_success(self):
        """Test successful PDF upload to reMarkable."""
        sync = EmailToRemarkableSync(self.test_config)

        mock_api = Mock()
        mock_collection = Mock()
        mock_collection.metadata.visible_name = "Test Folder"
        mock_collection.uuid = "test_uuid"
        mock_api.document_collections = {"test": mock_collection}

        mock_doc = Mock()
        mock_doc.metadata.visible_name = "test_file"

        with patch("builtins.open", mock_open(read_data=b"pdf_data")):
            with patch("email_to_remarkable.Document") as mock_doc_class:
                mock_doc_class.new_pdf.return_value = mock_doc
                with patch("builtins.print"):
                    result = sync.upload_to_remarkable(mock_api, "/test/file.pdf", "Test Folder")

        assert result is True
        mock_doc_class.new_pdf.assert_called_once()
        mock_api.upload.assert_called_once_with(mock_doc)
        assert mock_doc.parent == "test_uuid"

    def test_upload_to_remarkable_folder_not_found(self):
        """Test PDF upload when destination folder not found."""
        sync = EmailToRemarkableSync(self.test_config)

        mock_api = Mock()
        mock_api.document_collections = {}

        mock_doc = Mock()
        mock_doc.metadata.visible_name = "test_file"

        with patch("builtins.open", mock_open(read_data=b"pdf_data")):
            with patch("email_to_remarkable.Document") as mock_doc_class:
                mock_doc_class.new_pdf.return_value = mock_doc
                with patch("builtins.print"):
                    result = sync.upload_to_remarkable(
                        mock_api, "/test/file.pdf", "Nonexistent Folder"
                    )

        assert result is True
        # When folder not found, parent should not be set (stays as Mock default)
        # Since Mock objects have all attributes, we check if parent was explicitly set
        assert mock_doc.parent != "test_uuid"

    def test_upload_to_remarkable_exception(self):
        """Test PDF upload with exception."""
        sync = EmailToRemarkableSync(self.test_config)

        mock_api = Mock()

        with patch("builtins.open", side_effect=Exception("Test error")):
            with patch("builtins.print"):
                result = sync.upload_to_remarkable(mock_api, "/test/file.pdf")

        assert result is False

    @patch("email_to_remarkable.imaplib.IMAP4_SSL")
    @patch("email_to_remarkable.os.makedirs")
    def test_process_emails_no_unread(self, mock_makedirs, mock_imap_class):
        """Test processing emails when no unread emails exist."""
        sync = EmailToRemarkableSync(self.test_config)

        mock_mail = Mock()
        mock_imap_class.return_value = mock_mail
        mock_mail.search.return_value = ("OK", [b""])

        with patch.object(sync, "_setup_remarkable_api", return_value=Mock()):
            with patch("builtins.print"):
                result = sync.process_emails()

        assert result is True
        mock_mail.login.assert_called_once_with("test@example.com", "test_password")
        mock_mail.select.assert_called_once_with("test_inbox")

    @patch("email_to_remarkable.imaplib.IMAP4_SSL")
    @patch("email_to_remarkable.os.makedirs")
    @patch("email_to_remarkable.email.message_from_bytes")
    @patch("email_to_remarkable.os.remove")
    def test_process_emails_with_pdf_attachment(
        self, mock_remove, mock_message_from_bytes, mock_makedirs, mock_imap_class
    ):
        """Test processing emails with PDF attachments."""
        sync = EmailToRemarkableSync(self.test_config)

        # Mock IMAP
        mock_mail = Mock()
        mock_imap_class.return_value = mock_mail
        mock_mail.search.return_value = ("OK", [b"1"])
        mock_mail.fetch.return_value = ("OK", [(None, b"email_data")])

        # Mock email message
        mock_msg = MagicMock()
        mock_msg.__getitem__.return_value = "Test Subject"
        mock_message_from_bytes.return_value = mock_msg

        # Mock email part with PDF attachment
        mock_part = Mock()
        mock_part.get_content_maintype.return_value = "application"
        mock_part.get.return_value = "attachment"
        mock_part.get_content_type.return_value = "application/pdf"
        mock_part.get_filename.return_value = "test.pdf"
        mock_part.get_payload.return_value = b"pdf_data"

        mock_msg.walk.return_value = [mock_part]

        # Mock reMarkable API
        mock_rm_api = Mock()

        with patch.object(sync, "_setup_remarkable_api", return_value=mock_rm_api):
            with patch.object(sync, "upload_to_remarkable", return_value=True) as mock_upload:
                with patch("builtins.open", mock_open()):
                    with patch("builtins.print"):
                        result = sync.process_emails()

        assert result is True
        mock_upload.assert_called_once()
        mock_mail.store.assert_called_once_with(b"1", "+FLAGS", "(\\Seen)")

    def test_process_emails_remarkable_api_failure(self):
        """Test processing emails when reMarkable API setup fails."""
        sync = EmailToRemarkableSync(self.test_config)

        with patch.object(sync, "_setup_remarkable_api", return_value=None):
            result = sync.process_emails()

        assert result is False


class TestLoadConfig:
    """Test cases for load_config function."""

    def test_load_config_defaults(self):
        """Test loading configuration with default values."""
        with patch.dict(os.environ, {}, clear=True):
            config = load_config()

        expected_defaults = {
            "imap_server": "imap.gmail.com",
            "email_username": "",
            "email_password": "",
            "mailbox_to_check": "INBOX",
            "download_dir": "/tmp/downloaded_pdfs",
            "remarkable_dest_folder": "From Email",
            "remarkable_token": "",
            "remarkable_token_path": "/etc/remarkable/token",
            "rm_sync_file_path": "/tmp/rm_api_sync",
            "rm_log_file": "/tmp/rm_api.log",
        }

        assert config == expected_defaults

    def test_load_config_from_environment(self):
        """Test loading configuration from environment variables."""
        env_vars = {
            "IMAP_SERVER": "imap.test.com",
            "EMAIL_USERNAME": "test@example.com",
            "EMAIL_PASSWORD": "secret",
            "MAILBOX_TO_CHECK": "custom_inbox",
            "REMARKABLE_DEST_FOLDER": "Custom Folder",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config()

        assert config["imap_server"] == "imap.test.com"
        assert config["email_username"] == "test@example.com"
        assert config["email_password"] == "secret"
        assert config["mailbox_to_check"] == "custom_inbox"
        assert config["remarkable_dest_folder"] == "Custom Folder"


class TestMain:
    """Test cases for main function."""

    @patch("email_to_remarkable.EmailToRemarkableSync")
    @patch("email_to_remarkable.load_config")
    def test_main_success(self, mock_load_config, mock_sync_class):
        """Test successful main execution."""
        mock_config = {"test": "config"}
        mock_load_config.return_value = mock_config

        mock_sync = Mock()
        mock_sync.process_emails.return_value = True
        mock_sync_class.return_value = mock_sync

        from email_to_remarkable import main

        # Should not raise any exception
        main()

        mock_load_config.assert_called_once()
        mock_sync_class.assert_called_once_with(mock_config)
        mock_sync.process_emails.assert_called_once()

    @patch("email_to_remarkable.EmailToRemarkableSync")
    @patch("email_to_remarkable.load_config")
    def test_main_process_failure(self, mock_load_config, mock_sync_class):
        """Test main execution when process_emails fails."""
        mock_config = {"test": "config"}
        mock_load_config.return_value = mock_config

        mock_sync = Mock()
        mock_sync.process_emails.return_value = False
        mock_sync_class.return_value = mock_sync

        from email_to_remarkable import main

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1

    @patch("email_to_remarkable.load_config")
    def test_main_exception(self, mock_load_config):
        """Test main execution with exception."""
        mock_load_config.side_effect = Exception("Test error")

        from email_to_remarkable import main

        with patch("builtins.print"):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1
