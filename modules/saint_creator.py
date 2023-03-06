"""This module contains the class handling the logic of the saint creator."""
from __future__ import annotations

import logging


from .scheduler import Scheduler
from .saint_factory import SaintFactory


class SaintCreator(Scheduler):
    """Class handling the logic of the saint creator."""

    def __init__(self) -> SaintCreator:
        """Initialize the creator."""
        super().__init__()
        self._generate_time = self.loadScheduleTime("generate_time")
        self._factory = SaintFactory()

    def start(self) -> None:
        """Start the scheduler."""
        logging.info("Starting saint scheduler loop")
        super().start("generate_time", self._generate)

    def _generate(self) -> None:
        """Generate a saint."""
        self._factory.generateSaint()
        logging.info("Saint generated")
