"""This module handles the auto creation of saints at a given time."""
import logging

from modules.saint_creator import SaintCreator


def main() -> None:
    """Main function."""
    logfile = __file__.replace(".py", ".log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename=logfile,
        filemode="w",
    )

    logging.info("Starting saint creator")
    creator = SaintCreator()
    creator.start()


if __name__ == "__main__":
    main()
