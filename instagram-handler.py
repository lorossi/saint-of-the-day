"""This module takes care of the auto-posting of saints to instagram."""
import logging

from modules.instagram_poster import InstagramPoster


def main() -> None:
    """Main function."""
    logging.info("Starting instagram poster")
    poster = InstagramPoster()
    poster.start()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        filename= __file__.replace(".py", ".log"),
        filemode="w",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    main()
