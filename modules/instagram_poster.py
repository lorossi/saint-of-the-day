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

    def upload(self) -> None:
        """Publish a post."""
        if not self._tryLogin():
            return

        self._tryUpload()
        logging.info("Upload done")
        next_run = schedule.next_run().isoformat()
        logging.info(f"Next post scheduled for {next_run}")

    def start(self) -> None:
        """Loop the poster."""
        logging.info("Starting instagram poster")

        post_time_str = self._post_time.strftime("%H:%M")
        schedule.every().day.at(post_time_str).do(self.upload)
        next_run = schedule.next_run().isoformat()
        logging.info(f"Posts scheduled for {next_run}")
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logging.warning("Keyboard interrupt called. Exiting...")
                return

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

    def _tryLogin(self) -> bool:
        """Try to login to Instagram.

        Returns:
            bool: True if the login was successful, False otherwise
        """
        logging.info("Logging into Instagram...")
        tries = 0
        while tries < self._settings["max_tries"]:
            try:
                self._instagram.login()
                logging.info("Logged")
                return True
            except Exception as e:
                logging.error(f"Error while logging in: {e}")
                tries += 1
                logging.info(
                    f"Retrying in 10 seconds... ({tries}/"
                    f"{self._settings['max_tries']})"
                )
                time.sleep(10)

        logging.error("Aborting login after failed amounts.")
        return False

    def _tryUpload(self) -> bool:
        tries = 0
        logging.info("Posting image....")
        while tries < self._settings["max_tries"]:
            try:
                saint = self._factory.generateSaint()
                caption = saint.bio + "\n\n#santodelgiorno #santinoquotidiano"
                self._instagram.uploadImage(
                    image_path=saint.image_path, image_caption=caption
                )
                logging.info("Image posted")
                return True
            except Exception as e:
                logging.error(f"Error while posting: {e}")
                tries += 1
                logging.info(
                    f"Retrying in 10 seconds... ({tries}/"
                    f"{self._settings['max_tries']})"
                )
                time.sleep(10)

        logging.error("Aborting post after failed amounts.")
        return False
