from modules.email_client import EmailClient
import logging


def main():
    e = EmailClient()
    found = e.fetchRelevant()
    logging.info(f"Found {found} relevant emails")
    logging.info(f"Security code: {e.security_code}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
