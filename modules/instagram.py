from __future__ import annotations

import os
import logging

import toml
from instagrapi import Client
from PIL import Image


class Instagram:
    def __init__(self, path="settings.toml") -> Instagram:
        """Initialize the bot.

        Returns:
            Instagram
        """
        logging.info("Initializing Instagram")
        self._settings = self._loadSettings(path)
        self._login()

    def _loadSettings(self, path: str) -> dict:
        """Load settings from a TOML file.

        Args:
            path (str): Path to the TOML file.

        Returns:
            dict: Settings.
        """
        with open(path, "r") as f:
            return toml.load(f)[self.__class__.__name__]

    def _login(self) -> None:
        """Login to Instagram."""
        logging.info("Logging in to Instagram")
        self._client = Client()
        self._client.login(self._settings["username"], self._settings["password"])
        logging.info(
            f"Logged in to Instagram with username {self._settings['username']}"
        )

    def _convertToJPEG(self, image_path: str) -> str:
        """Convert a PNG image to JPEG.

        Args:
            image_path (str): Path to the PNG image.

        Returns:
            str: Path to the JPEG image.
        """
        logging.info(f"Converting {image_path} to JPEG")
        image = Image.open(image_path)
        image = image.convert("RGB")
        new_image_path = image_path.replace(".png", ".jpg")
        image.save(new_image_path, "JPEG")
        logging.info(f"Image converted to {new_image_path}")
        return new_image_path

    def uploadImage(self, image_path: str, image_caption: str) -> None:
        """Upload an image to Instagram."""
        logging.info(f"Uploading image {image_path} to Instagram")

        delete_after = False
        if image_path.endswith(".png"):
            delete_after = True
            image_path = self._convertToJPEG(image_path)

        self._client.photo_upload(image_path, image_caption)
        logging.info(f"Image {image_path} uploaded to Instagram")

        if delete_after:
            logging.info("Deleting temporary JPG")
            os.remove(image_path)
