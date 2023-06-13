"""Module to quickly post an image to Instagram."""
from __future__ import annotations

import logging

from modules.instagram import Instagram
from modules.saint_factory import SaintFactory


class InstagramQuickPost:
    """Class handling the logic of the instagram quick poster."""

    def __init__(self) -> InstagramQuickPost:
        """Initialize the poster."""
        logging.info("Initializing instagram quick poster")
        self._instagram = Instagram()
        self._factory = SaintFactory()

    def _uploadImage(self) -> None:
        """Upload the image."""
        logging.info("Uploading image")
        saint = self._factory.generateSaint()
        caption = saint.bio + "\n\n#santodelgiorno #santinoquotidiano"
        self._instagram.uploadImage(image_path=saint.image_path, image_caption=caption)

    def start(self) -> None:
        """Publish a post."""
        logging.info("Starting instagram quick poster")
        if not self._instagram.login():
            return

        logging.info("Logged in")
        self._uploadImage()

        logging.info("Logging out")
        self._instagram.logout()

        logging.info("Upload done")


def main():
    """Script entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s "
            "(%(lineno)d) - %(message)s"
        ),
    )
    logging.info("Starting instagram quick poster")
    poster = InstagramQuickPost()
    poster.start()


if __name__ == "__main__":
    main()
