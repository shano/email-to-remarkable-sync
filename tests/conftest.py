#!/usr/bin/env python3
"""
Pytest configuration and fixtures for email-to-remarkable-sync tests.
"""

import tempfile
from unittest.mock import Mock

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_config():
    """Sample configuration for tests."""
    return {
        "imap_server": "imap.test.com",
        "email_username": "test@example.com",
        "email_password": "test_password",
        "mailbox_to_check": "test_inbox",
        "remarkable_dest_folder": "Test Folder",
        "download_dir": "/tmp/test_downloads",
        "remarkable_token": "test_token",
        "remarkable_token_path": "/tmp/test_token",
        "rm_sync_file_path": "/tmp/test_sync",
        "rm_log_file": "/tmp/test_log",
    }


@pytest.fixture
def mock_remarkable_api():
    """Mock reMarkable API instance."""
    api = Mock()
    api.document_collections = {}
    api.documents = {}
    return api


@pytest.fixture
def sample_pdf_data():
    """Sample PDF data for testing."""
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n%%EOF"


@pytest.fixture
def mock_email_message():
    """Mock email message with PDF attachment."""
    message = Mock()
    message.__getitem__.return_value = "Test Email Subject"

    # Mock PDF attachment
    pdf_part = Mock()
    pdf_part.get_content_maintype.return_value = "application"
    pdf_part.get.return_value = "attachment"
    pdf_part.get_content_type.return_value = "application/pdf"
    pdf_part.get_filename.return_value = "test_document.pdf"
    pdf_part.get_payload.return_value = b"fake_pdf_data"

    # Mock text part (should be ignored)
    text_part = Mock()
    text_part.get_content_maintype.return_value = "multipart"
    text_part.get.return_value = None

    message.walk.return_value = [text_part, pdf_part]

    return message
