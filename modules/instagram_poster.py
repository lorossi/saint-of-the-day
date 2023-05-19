"""Module containing the instagram poster class."""
from __future__ import annotations

import logging
from datetime import datetime

from modules.instagram import Instagram
from modules.saint_factory import SaintFactory

from .scheduler import Scheduler


class InstagramPoster(Scheduler):
    """Class handling the logic of the instagram poster."""

    _factory: SaintFactory
    _instagram: Instagram
    _post_time: datetime

    def __init__(self) -> InstagramPoster:
        """Initialize the poster."""
        logging.info("Initializing instagram poster")
        super().__init__()
        self._factory = SaintFactory()
        self._instagram = Instagram()
        self._post_time = self.loadScheduleTime("post_time")

    def start(self) -> None:
        """Loop the poster."""
        logging.info("Starting instagram poster loop")
        super().start("post_time", self.upload)

    def upload(self) -> None:
        """Publish a post."""
        if not self.tryFunction(self._instagram.login):
            return

        if not self.tryFunction(self._uploadImage):
            return

        self._instagram.logout()

        logging.info("Upload done")

    def _uploadImage(self) -> None:
        """Upload the image."""
        saint = self._factory.generateSaint()
        caption = saint.bio + "\n\n#santodelgiorno #santinoquotidiano"
        self._instagram.uploadImage(image_path=saint.image_path, image_caption=caption)
