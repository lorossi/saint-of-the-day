"""This module handles the auto creation of saints at a given time."""
import logging

from modules.saint_creator import SaintCreator


def main() -> None:
    """Main function."""
    logging.info("Starting saint creator")
    creator = SaintCreator()
    creator.start()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        filename=__file__.replace(".py", ".log"),
        filemode="w",
        format=(
            "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s "
            "(%(lineno)d) - %(message)s"
        ),
    )
    main()
