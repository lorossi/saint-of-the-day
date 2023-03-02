"""This module takes care of the auto-posting of saints to instagram."""
import logging

from modules.instagram_poster import InstagramPoster


def main() -> None:
    """Main function."""
    logfile = __file__.replace(".py", ".log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename=logfile,
        filemode="w",
    )

    logging.info("Starting instagram poster")
    poster = InstagramPoster()
    poster.start()


if __name__ == "__main__":
    main()
