"""Module handling the logic to post images to Instagram."""
from __future__ import annotations

import logging
import os

import toml
from instagrapi import Client
from instagrapi.mixins.challenge import ChallengeChoice
from PIL import Image

from modules.email_client import EmailClient


class Instagram:
    """Class handling the logic to post images to Instagram."""

    def __init__(self, path="settings.toml") -> Instagram:
        """Initialize the bot.

        Returns:
            Instagram
        """
        logging.info("Initializing Instagram")
        self._settings = self._loadSettings(path)
        self._email_client = EmailClient()
        self._createTempFolder()

    def _createTempFolder(self) -> None:
        """Create folder structure."""
        os.makedirs(self._settings["temp_folder"], exist_ok=True)

    def _cleanTempFolder(self) -> None:
        """Clean the temporary folder."""
        for file in os.listdir(self._settings["temp_folder"]):
            os.remove(os.path.join(self._settings["temp_folder"], file))

    def _loadSettings(self, path: str) -> dict:
        """Load settings from a TOML file.

        Args:
            path (str): Path to the TOML file.

        Returns:
            dict: Settings.
        """
        with open(path, "r") as f:
            return toml.load(f)[self.__class__.__name__]

    def _challengeCodeHandler(self, _: ChallengeChoice) -> str:
        self._email_client.fetchRelevant()
        return self._email_client.security_code

    def login(self) -> None:
        """Login to Instagram."""
        logging.info("Logging in to Instagram")
        self._client = Client()
        self._client.challenge_code_handler = self._challengeCodeHandler
        self._client.login(self._settings["username"], self._settings["password"])
        logging.info(
            f"Logged in to Instagram with username {self._settings['username']}"
        )

    def _convertToJPEG(self, image_path: str, destination: str) -> str:
        """Convert an image to JPEG.

        Args:
            image_path (str): Path to the source image.

        Returns:
            str: Path to the JPEG image.
        """
        logging.info(f"Converting {image_path} to JPEG")

        filename = image_path.split("/")[-1].split(".")[0]
        image = Image.open(image_path).convert("RGB")
        jpeg_path = os.path.join(destination, f"{filename}.jpg")
        image.save(jpeg_path, "JPEG")
        logging.info(f"Image converted to {jpeg_path}")
        return jpeg_path

    def uploadImage(self, image_path: str, image_caption: str) -> None:
        """Upload an image to Instagram.

        Args:
            image_path (str): path of the image to upload
            image_caption (str): caption of the image
        """
        logging.info(f"Uploading image {image_path} to Instagram")

        delete_after = False
        if not image_path.endswith(".jpg"):
            delete_after = True
            image_path = self._convertToJPEG(image_path, self._settings["temp_folder"])

        self._client.photo_upload(image_path, image_caption)
        logging.info(f"Image {image_path} uploaded to Instagram")

        if delete_after:
            logging.info("Cleaning temporary folder")
            self._cleanTempFolder()
