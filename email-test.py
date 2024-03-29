"""Module containing a simple test for the email client."""
import logging

from modules.email_client import EmailClient


def main():
    """Script entry point."""
    logging.basicConfig(level=logging.INFO)
    e = EmailClient()
    security_code = e.getInstagramSecurityCode()
    logging.info(f"Security code: {security_code}")


if __name__ == "__main__":
    main()
