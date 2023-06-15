"""Simple login test for the instagram client."""
import logging


from modules.instagram import Instagram


def main() -> None:
    """Script entry point."""
    logging.info("Starting Instagram test")
    instagram = Instagram()
    instagram.login()
    instagram.logout()
    logging.info("Instagram test complete")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s "
            "(%(lineno)d) - %(message)s"
        ),
    )
    main()
