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
    _settings: dict
    _security_code: str

    def __init__(self) -> EmailClient:
        """Initialize the bot.

        Returns:
            Email
        """
        logging.info("Initializing Email")
        self._settings = self._loadSettings("settings.toml")

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

    def _fetchRelevantEmails(self) -> list[EmailMessage]:
        """Fetch relevant emails.

        Returns:
            list[EmailMessage]: List of relevant emails.
        """
        if not self._client:
            logging.error("Client not initialized")
            return 0

        logging.info("Loading emails from today")
        logging.info(f"Query: ({self._today_query} {self._sender_query})")
        _, data = self._client.search(
            None, f"({self._today_query} {self._sender_query})"
        )
        loaded_emails = data[0].split()
        logging.info(f"Found {len(loaded_emails)} emails")

        relevant_emails = []

        for msg_id in loaded_emails:
            _, data = self._client.fetch(msg_id, "(RFC822)")
            msg = BytesParser(policy=default).parsebytes(data[0][1])
            relevant_emails.append(msg)

        logging.info(f"Loaded {len(relevant_emails)} emails")
        return relevant_emails

    def _extractEmailContent(self, email: EmailMessage) -> str:
        """Extract the content of an email.

        Args:
            email (EmailMessage): Email to extract the content from.

        Returns:
            str: Content of the email.
        """
        logging.info(
            f"Extracting content from email {email['Subject']} by {email['From']}"
        )
        if email.is_multipart():
            return self._extractEmailContent(email.get_payload(0))
        else:
            return email.get_payload(None, True).decode("utf-8")

    def getInstagramSecurityCode(self) -> str:
        """Extract the security code from the emails.

        Returns:
            str: Security code. If multiple codes are found,
                the one found in the most recent email is returned.
        """
        last_date = datetime.min
        last_code = None

        self._login()
        relevant_emails = self._fetchRelevantEmails()

        if len(relevant_emails) == 0:
            logging.error("No relevant emails found")
            return None

        for email in relevant_emails:
            content = self._extractEmailContent(email)
            if m := re.findall(r">(\d{6})<", content, flags=re.MULTILINE):
                date = datetime.strptime(email["Date"][:-6], "%a, %d %b %Y %H:%M:%S")
                if date > last_date:
                    logging.info(f"Found security code {m[0]}, date {date}")
                    last_date = date
                    last_code = m[0]

        if last_code is None:
            logging.info("No security code found")
            return None

        return last_code

    @property
    def _today_query(self) -> str:
        return f"ON {datetime.today().strftime('%d-%b-%Y')}"

    @property
    def _sender_query(self) -> str:
        return f"FROM {self._settings['sender']}"
