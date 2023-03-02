import logging
import sys

from modules.instagram_poster import InstagramPoster


def main(argv: list[str]) -> None:
    """Main function.

    Args:
        argv (list[str]): Command line arguments
    """
    logging.info("Starting instagram poster")
    poster = InstagramPoster()

    if len(argv) > 1 and "now" in argv[1]:
        poster.publish()
        return

    poster.start()


if __name__ == "__main__":
    logfile = __file__.replace(".py", ".log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename=logfile,
        filemode="w",
    )
    main(sys.argv)
