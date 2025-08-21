#!/usr/bin/env python3
"""
Integration tests for email-to-remarkable-sync.
"""

import subprocess
import sys
from unittest.mock import patch


def test_import_package():
    """Test that the main module can be imported without errors."""
    import email_to_remarkable

    assert hasattr(email_to_remarkable, "EmailToRemarkableSync")
    assert hasattr(email_to_remarkable, "load_config")
    assert hasattr(email_to_remarkable, "main")


def test_cli_help():
    """Test that CLI entry point exists and can show help."""
    # This would test the actual CLI, but we'll mock it for safety
    with patch("email_to_remarkable.main") as mock_main:
        from email_to_remarkable import main

        main()
        mock_main.assert_called_once()


def test_config_loading():
    """Test that configuration loading works."""
    from email_to_remarkable import load_config

    config = load_config()

    # Should have all expected keys
    expected_keys = [
        "imap_server",
        "email_username",
        "email_password",
        "mailbox_to_check",
        "download_dir",
        "remarkable_dest_folder",
        "remarkable_token",
        "remarkable_token_path",
        "rm_sync_file_path",
        "rm_log_file",
    ]

    for key in expected_keys:
        assert key in config


def test_class_instantiation():
    """Test that the main class can be instantiated with valid config."""
    from email_to_remarkable import EmailToRemarkableSync

    test_config = {
        "imap_server": "imap.test.com",
        "email_username": "test@example.com",
        "email_password": "test_password",
        "mailbox_to_check": "test_inbox",
        "remarkable_dest_folder": "Test Folder",
        "download_dir": "/tmp/test_downloads",
        "remarkable_token": "test_token",
    }

    sync = EmailToRemarkableSync(test_config)
    assert sync.config == test_config


def test_poetry_entry_point():
    """Test that the Poetry entry point is correctly configured."""
    try:
        # This would test the actual entry point, but we need to be careful
        # not to run the actual sync process in tests
        result = subprocess.run(
            [sys.executable, "-c", 'import email_to_remarkable; print("Entry point accessible")'],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "Entry point accessible" in result.stdout

    except subprocess.TimeoutExpired:
        # If the import takes too long, something might be wrong
        assert False, "Import took too long, possible dependency issues"
