"""Module containing the instagram poster class."""
from __future__ import annotations

import datetime
import logging
import time

import pytz
import schedule
import toml

from modules.instagram import Instagram
from modules.saint_factory import SaintFactory


class InstagramPoster:
    """Class handling the logic of the instagram poster."""

    _timezone: pytz.timezone = pytz.timezone("Europe/Rome")

    def __init__(self, settings_path: str = "settings.toml") -> InstagramPoster:
        """Initialize the poster."""
        logging.info("Initializing instagram poster")
        self._factory = SaintFactory()
        self._instagram = Instagram()
        self._settings = self._loadSettings(settings_path)
        self._post_time = self._loadPostTime()

    def publish(self) -> None:
        """Publish a post."""
        logging.info("Publishing post")
        saint = self._factory.generateSaint()
        caption = saint.bio + "\n\n#santodelgiorno #santinoquotidiano"
        self._instagram.uploadImage(image_path=saint.image_path, image_caption=caption)
        logging.info("Post published")

    def start(self) -> None:
        """Loop the poster."""
        logging.info("Starting instagram poster")
        post_time_str = self._post_time.strftime("%H:%M")
        schedule.every().day.at(post_time_str).do(self.publish)
        logging.info("Posts scheduled")
        while True:
            schedule.run_pending()
            time.sleep(1)

    def _loadSettings(self, settings_path: str) -> dict:
        """Load settings from a toml file.

        Args:
            settings_path (str): Path to the settings file

        Returns:
            dict: Settings
        """
        logging.info("Loading settings")
        with open(settings_path, "r") as f:
            settings = toml.load(f)[self.__class__.__name__]
        return settings

    def _loadPostTime(self) -> datetime.time:
        """Load the time at which the bot posts the saint.

        Returns:
            datetime.time: Post time
        """
        return datetime.datetime.strptime(self._settings["post_time"], "%H:%M").replace(
            tzinfo=self._timezone
        )
