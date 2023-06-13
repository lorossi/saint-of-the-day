"""Module containing a simple test for the email client."""
import logging

from modules.email_client import EmailClient


def main():
    """Script entry point."""
    e = EmailClient()
    found = e.fetchRelevant()
    logging.info(f"Found {found} relevant emails")
    logging.info(f"Security code: {e.security_code}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
