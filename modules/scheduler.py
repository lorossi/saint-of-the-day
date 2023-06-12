"""This module contains the class handling the logic of the scheduler.

The scheduler is a class inherited by other classes that need to schedule
a task once a day. It uses the schedule library to schedule the task and \
the time is loaded from a settings file, in format HH:MM.
"""
from __future__ import annotations

import logging
from datetime import datetime
from time import sleep

import pytz
import schedule
import toml


class Scheduler:
    """Class handling the logic of the scheduler."""

    _timezone: pytz.timezone = pytz.timezone("Europe/Rome")

    def __init__(self) -> Scheduler:
        """Initialize the scheduler."""
        self._settings = self._loadSettings()

    def _loadSettings(self, path: str = "settings.toml", key: str = None) -> dict:
        """Load settings from a toml file.

        Args:
            settings_path (str): Path to the settings file

        Returns:
            dict: Settings
        """
        logging.info("Loading settings")
        with open(path, "r") as settings_file:
            settings = toml.load(settings_file)

        logging.info("Settings loaded")

        if key is None and self.__class__.__name__ in settings:
            return settings[self.__class__.__name__]

        if key is not None:
            return settings[key]

        return settings

    def loadScheduleTime(self, key: str) -> datetime:
        """Load the time the image was generated.

        Returns:
            datetime: Time the image was generated.
        """
        return datetime.strptime(self._settings[key], "%H:%M").replace(
            tzinfo=self._timezone
        )

    def _schedule(self, key: str, function: callable) -> None:
        """Schedule a function to run at a specific time once a day.

        Args:
            key (str): key containing the run time in format %H:%M
            function (callable): function to run
        """
        schedule_time = self.loadScheduleTime(key)
        schedule_time_str = schedule_time.strftime("%H:%M")
        schedule.every().day.at(schedule_time_str).do(function)

    def tryFunction(self, f: callable) -> bool:
        """Try to run a function."""
        tries = 0
        max_tries = self._settings["max_tries"]
        retry_delay = self._settings["retry_delay"]
        while tries < max_tries:
            try:
                f()
                return True
            except Exception as e:
                logging.error(f"Error while running function: {f.__name__}")
                logging.error(f"Error raised: {e}")
                logging.error(f"Error type: {type(e)}")
                tries += 1
                logging.info(
                    f"Trying again in {retry_delay} second ({tries}/{max_tries})"
                )
                sleep(retry_delay)

        logging.error("Max tries reached. Exiting...")
        return False

    def start(self, key: str, function: callable) -> None:
        """Loop the creator."""
        self._schedule(key, function)
        logging.info(f"Function {function.__name__} scheduled for {self.next_run}")
        while True:
            try:
                schedule.run_pending()
                sleep(1)
            except KeyboardInterrupt:
                logging.warning("Keyboard interrupt called. Exiting...")
                return

    @property
    def next_run(self) -> str:
        """Get the next run time.

        Returns:
            str: run time, iso format
        """
        return schedule.next_run().isoformat()
