"""Email client module."""
from __future__ import annotations

import imaplib
import logging
import re
from datetime import datetime
from email.message import EmailMessage
from email.parser import BytesParser
from email.policy import default

import toml


class EmailClientException(Exception):
    """Base class for exceptions in this module."""

    pass


class EmailClient:
    """Class handling the logic of the email client."""

    _client: imaplib.IMAP4_SSL
    _emails: list[EmailMessage]
    _settings: dict
    _security_code: str

    def __init__(self) -> EmailClient:
        """Initialize the bot.

        Returns:
            Email
        """
        logging.info("Initializing Email")
        self._settings = self._loadSettings("settings.toml")
        if not self._login():
            logging.error("Error logging in to email")

    def _login(self) -> bool:
        """Login to the email account.

        Returns:
            bool: True if the login was successful, False otherwise.
        """
        logging.info("Logging in to email")
        self._security_code = None
        try:
            self._client = imaplib.IMAP4_SSL(self._settings["imap_server"])
            self._client.login(self._settings["username"], self._settings["password"])
            logging.info(
                f"Logged in to email with username {self._settings['username']}"
            )
        except Exception as e:
            logging.error(f"Error logging in to email: {e}")
            return False

        logging.info("Selecting INBOX")
        self._client.select("INBOX")

        return True

    def _loadSettings(self, path: str) -> dict:
        """Load settings from a TOML file.

        Args:
            path (str): Path to the TOML file.

        Returns:
            dict: Settings.
        """
        with open(path, "r") as f:
            return toml.load(f)[self.__class__.__name__]

    def fetchRelevant(self) -> int:
        """Fetch relevant emails.

        Returns:
            int: Number of emails fetched.
        """
        if not self._client:
            logging.error("Client not initialized")
            return 0

        logging.info("Loading emails from today")
        _, data = self._client.search(
            None, f"({self._today_query} {self._sender_query})"
        )
        loaded_emails = data[0].split()
        logging.info(f"Found {len(loaded_emails)} emails")

        self._emails = []

        for msg_id in loaded_emails:
            _, data = self._client.fetch(msg_id, "(RFC822)")
            msg = BytesParser(policy=default).parsebytes(data[0][1])
            self._emails.append(msg)

        logging.info(f"Loaded {len(self._emails)} emails")
        return len(self._emails)

    def _extractEmailContent(self, email: EmailMessage) -> str:
        """Extract the content of an email.

        Args:
            email (EmailMessage): Email to extract the content from.

        Returns:
            str: Content of the email.
        """
        if email.is_multipart():
            return self._extractEmailContent(email.get_payload(0))
        else:
            return email.get_payload(None, True).decode("utf-8")

    def _extractSecurityCode(self) -> bool:
        """Extract the security code from the emails.

        Returns:
            bool: True if the security code was found, False otherwise.
        """
        for email in self._emails:
            content = self._extractEmailContent(email)
            if m := re.findall(r"^\d{6}", content, flags=re.MULTILINE):
                self._security_code = m[0]
                return True

        return False

    @property
    def _today_query(self) -> str:
        return f"ON {datetime.today().strftime('%d-%b-%Y')}"

    @property
    def _sender_query(self) -> str:
        return f"FROM {self._settings['sender']}"

    @property
    def security_code(self) -> str:
        """Get the security code from the email."""
        if not self._security_code:
            if not self._extractSecurityCode():
                raise EmailClientException("No security code found")

        return self._security_code


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    email = EmailClient()
    email.fetchRelevant()
    print(email.security_code)
