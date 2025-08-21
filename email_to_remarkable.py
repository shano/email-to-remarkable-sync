#!/usr/bin/env python3
"""
Email to reMarkable Sync

Monitors an email mailbox for PDF attachments and uploads them to reMarkable cloud storage.
"""

import email
import imaplib
import os
from email.header import decode_header
from typing import Optional

from rm_api import API
from rm_api.models import Document


class EmailToRemarkableSync:
    """Main class for email to reMarkable synchronization."""

    def __init__(self, config: dict):
        """Initialize with configuration dictionary."""
        self.config = config
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate required configuration keys."""
        required_keys = [
            "imap_server",
            "email_username",
            "email_password",
            "mailbox_to_check",
            "remarkable_dest_folder",
        ]

        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Required configuration key '{key}' is missing")

        if not self.config["email_password"]:
            raise ValueError("Email password is required but not provided")

    def decode_subject(self, raw_subject: str) -> str:
        """Decode email subject headers."""
        decoded_parts = decode_header(raw_subject)
        return "".join(
            part.decode(encoding or "utf-8", errors="replace") if isinstance(part, bytes) else part
            for part, encoding in decoded_parts
        ).strip()

    def upload_to_remarkable(
        self, api: API, pdf_path: str, destination_folder: Optional[str] = None
    ) -> bool:
        """
        Upload a single PDF file to the reMarkable cloud.

        Args:
            api: Authenticated reMarkable API instance
            pdf_path: Path to the PDF file to upload
            destination_folder: Optional folder name on reMarkable to upload to

        Returns:
            True on success, False on failure
        """
        try:
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()

            doc = Document.new_pdf(
                api, name=os.path.splitext(os.path.basename(pdf_path))[0], pdf_data=pdf_data
            )

            if destination_folder:
                parent_collection = None
                for collection in api.document_collections.values():
                    if collection.metadata.visible_name == destination_folder:
                        parent_collection = collection
                        break

                if parent_collection:
                    doc.parent = parent_collection.uuid
                else:
                    print(
                        f"  -> Warning: Destination folder '{destination_folder}' not found. "
                        "Uploading to root."
                    )

            print(f"  -> Uploading '{doc.metadata.visible_name}' to reMarkable...")
            api.upload(doc)
            print("  -> ✅ Upload successful.")
            return True
        except Exception as e:
            print(f"  -> ❌ An error occurred during upload: {e}")
            return False

    def _setup_remarkable_api(self) -> Optional[API]:
        """Set up and authenticate with reMarkable API."""
        try:
            rm_api = API(
                require_token=False,
                sync_file_path=self.config.get("rm_sync_file_path", "/tmp/rm_api_sync"),
                log_file=self.config.get("rm_log_file", "/tmp/rm_api.log"),
            )

            # Load token from file or environment variable
            token = self.config.get("remarkable_token")
            if not token:
                token_path = self.config.get("remarkable_token_path", "/etc/remarkable/token")
                try:
                    with open(token_path, "r") as f:
                        token = f.read().strip()
                except FileNotFoundError:
                    print(f"❌ Error: reMarkable token not found at {token_path}")
                    return None

            rm_api.token = token
            print("Successfully authenticated with reMarkable cloud.")

            # Sync collections to be able to find destination folder
            print("Syncing with reMarkable to get folder structure...")
            rm_api.get_documents()
            print("Sync complete.")

            return rm_api

        except Exception as e:
            print(f"❌ Error connecting to reMarkable: {e}")
            return None

    def process_emails(self) -> bool:
        """
        Main processing function: connects to email, downloads PDFs, uploads to reMarkable.

        Returns:
            True if processing completed successfully, False otherwise
        """
        download_dir = self.config.get("download_dir", "/tmp/downloaded_pdfs")
        os.makedirs(download_dir, exist_ok=True)
        print(f"📥 Temporary downloads will be saved to '{download_dir}'.")

        # Authenticate with reMarkable
        rm_api = self._setup_remarkable_api()
        if not rm_api:
            return False

        # Connect to IMAP
        mail = None
        try:
            print(f"\nConnecting to {self.config['imap_server']}...")
            mail = imaplib.IMAP4_SSL(self.config["imap_server"])
            mail.login(self.config["email_username"], self.config["email_password"])
            mail.select(self.config["mailbox_to_check"])
            print(f"📬 Opened mailbox '{self.config['mailbox_to_check']}'.")

            status, data = mail.search(None, "UNSEEN")
            unread_email_ids = data[0].split()

            if not unread_email_ids:
                print("No unread emails found. Nothing to do.")
                return True

            print(f"Found {len(unread_email_ids)} unread email(s).")

            # Process each unread email
            for email_id in unread_email_ids:
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                raw_msg = msg_data[0][1]  # type: ignore
                if isinstance(raw_msg, bytes):
                    msg = email.message_from_bytes(raw_msg)
                else:
                    continue  # Skip if data format is unexpected
                subject = self.decode_subject(msg["subject"])
                print(f"\nProcessing email: '{subject}'")

                downloaded_files = []
                for part in msg.walk():
                    if (
                        part.get_content_maintype() == "multipart"
                        or part.get("Content-Disposition") is None
                    ):
                        continue
                    if part.get_content_type() == "application/pdf":
                        filename = part.get_filename()
                        if filename:
                            filepath = os.path.join(download_dir, filename)
                            payload = part.get_payload(decode=True)
                            if isinstance(payload, bytes):
                                with open(filepath, "wb") as f:
                                    f.write(payload)
                                downloaded_files.append(filepath)
                                print(f"  -> Downloaded '{filename}'")

                if not downloaded_files:
                    print("  -> No PDF attachments found. Marking email as read.")
                    mail.store(email_id, "+FLAGS", "(\\Seen)")
                    continue

                # Upload attachments and mark email as read on success
                all_uploads_succeeded = True
                for pdf_path in downloaded_files:
                    success = self.upload_to_remarkable(
                        rm_api, pdf_path, self.config["remarkable_dest_folder"]
                    )
                    if success:
                        os.remove(pdf_path)  # Clean up the local file
                    else:
                        all_uploads_succeeded = False

                if all_uploads_succeeded:
                    print(
                        f"✅ All attachments for '{subject}' processed successfully. "
                        "Marking as read."
                    )
                    mail.store(email_id, "+FLAGS", "(\\Seen)")
                else:
                    print(
                        f"⚠️ Some attachments for '{subject}' failed to upload. "
                        "Email will be retried on next run."
                    )

            return True

        except imaplib.IMAP4.error as e:
            print(f"❌ IMAP Error: {e}")
            return False
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
            return False
        finally:
            if mail:
                mail.logout()
                print("\n✅ Connection to mail server closed.")


def load_config() -> dict:
    """Load configuration from environment variables with defaults."""
    config = {
        "imap_server": os.getenv("IMAP_SERVER", "imap.gmail.com"),
        "email_username": os.getenv("EMAIL_USERNAME", ""),
        "email_password": os.getenv("EMAIL_PASSWORD", ""),
        "mailbox_to_check": os.getenv("MAILBOX_TO_CHECK", "INBOX"),
        "download_dir": os.getenv("DOWNLOAD_DIR", "/tmp/downloaded_pdfs"),
        "remarkable_dest_folder": os.getenv("REMARKABLE_DEST_FOLDER", "From Email"),
        "remarkable_token": os.getenv("REMARKABLE_TOKEN", ""),
        "remarkable_token_path": os.getenv("REMARKABLE_TOKEN_PATH", "/etc/remarkable/token"),
        "rm_sync_file_path": os.getenv("RM_SYNC_FILE_PATH", "/tmp/rm_api_sync"),
        "rm_log_file": os.getenv("RM_LOG_FILE", "/tmp/rm_api.log"),
    }
    return config


def main() -> None:
    """Main entry point for command line usage."""
    try:
        config = load_config()
        sync = EmailToRemarkableSync(config)
        success = sync.process_emails()

        if not success:
            exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
