from __future__ import annotations

import logging
from sys import argv

from modules.saint_factory import SaintFactory


def main(argv: list[str]) -> None:
    """Run the main function.

    Args:
        argv (list[str]): Command line arguments
    """
    logging.basicConfig(level=logging.INFO)
    offline = "online" not in argv

    if offline:
        print("run in online mode by adding 'online' to the command line arguments")

    f = SaintFactory()
    f.generateSaint(offline=offline, force_generation=True)


if __name__ == "__main__":
    main(argv)
