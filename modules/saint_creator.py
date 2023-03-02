from __future__ import annotations

import logging
import time
from datetime import datetime

import pytz
import schedule
import toml

from .saint_factory import SaintFactory


class SaintCreator:
    """Class handling the logic of the saint creator."""

    _timezone: pytz.timezone = pytz.timezone("Europe/Rome")

    def __init__(self) -> SaintCreator:
        self._settings = self._loadSettings()
        self._generate_time = self._loadGenerateTime()
        self._factory = SaintFactory()

    def _loadSettings(self, path: str = "settings.toml") -> dict:
        """Load settings from a toml file.

        Args:
            settings_path (str): Path to the settings file

        Returns:
            dict: Settings
        """
        logging.info("Loading settings")
        with open(path, "r") as settings_file:
            settings = toml.load(settings_file)[self.__class__.__name__]
        logging.info("Settings loaded")
        return settings

    def _loadGenerateTime(self) -> datetime:
        """Load the time the image was generated.

        Returns:
            datetime: Time the image was generated.
        """
        return datetime.strptime(self._settings["generate_time"], "%H:%M").replace(
            tzinfo=self._timezone
        )

    def start(self) -> None:
        """Loop the creator."""
        logging.info("Starting saint creator loop")
        generate_time_str = self._generate_time.strftime("%H:%M")
        schedule.every().day.at(generate_time_str).do(self._generate)
        logging.info("Saints generation scheduled")
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logging.warning("Keyboard interrupt called. Exiting...")
                return

    def _generate(self) -> None:
        self._factory.generateSaint()
