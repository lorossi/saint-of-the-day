"""Module handling the logic to post images to Instagram."""
from __future__ import annotations

import logging
import os
from time import sleep
from typing import Any

import toml
import ujson
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from instagrapi.mixins.challenge import ChallengeChoice
from PIL import Image

from modules.email_client import EmailClient, EmailClientException


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

    def _tryLoadInstagramSettings(self) -> bool:
        if not os.path.exists(self._settings["instagram_settings_path"]):
            return False

        try:
            with open(self._settings["instagram_settings_path"], "r") as f:
                self._client.settings = ujson.load(f)
            return True
        except Exception as e:
            logging.error(f"Error loading Instagram settings: {e}")
            return False

    def _deleteInstagramSettings(self) -> bool:
        if not os.path.exists(self._settings["instagram_settings_path"]):
            return False

        os.remove(self._settings["instagram_settings_path"])
        return True

    def _challengeCodeHandler(self, _: ChallengeChoice, *__: Any) -> str:
        logging.info("Challenge code required.")
        tries = 0
        max_tries = 4
        sleep_time = 5
        while True:
            try:
                self._email_client.fetchRelevant()
                return self._email_client.security_code
            except EmailClientException:
                logging.info(
                    f"No relevant email found. Retrying in {sleep_time} seconds. "
                    f"Attempt {tries+1}/{max_tries}"
                )
                tries += 1
                if tries >= max_tries:
                    raise Exception("Too many attempts")
                sleep(sleep_time)

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

    def login(self, use_proxy: bool = False) -> None:
        """Login to Instagram."""
        logging.info("Logging in to Instagram")
        self._client = Client()
        self._client.challenge_code_handler = self._challengeCodeHandler

        if use_proxy:
            self._client.set_proxy(self.proxy)

        settings_exist = self._tryLoadInstagramSettings()
        if settings_exist:
            logging.info("Instagram settings loaded from file")
            self._client.load_settings(self._settings["instagram_settings_path"])
        else:
            logging.info("Instagram settings not found. Creating new ones")
            self._client.set_locale("it_IT")
            self._client.set_country("IT")
            self._client.set_country_code(39)
            self._client.set_timezone_offset(7200)

        logging.info("Logging in to Instagram API")
        self._client.login(self._settings["username"], self._settings["password"])

        try:
            account_info = self._client.account_info()
            logging.info(f"Logged in to Instagram with account info: {account_info}")
        except LoginRequired:
            logging.warning("login required, using clean session")
            # log out from the current session
            self.logout()
            # delete the previous settings
            self._deleteInstagramSettings()
            # log in again
            self.login()

        logging.info("Saving Instagram settings to file")
        self._client.dump_settings(self._settings["instagram_settings_path"])

        logging.info("Log in procedure completed")

        return True

    def logout(self) -> None:
        """Logout from Instagram."""
        logging.info("Logging out from Instagram")
        self._client.logout()
        logging.info("Logged out from Instagram")

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

    @property
    def proxy(self) -> str:
        """Return the proxy URL representation."""
        url = self._settings["proxy_host"]
        port = self._settings["proxy_port"]
        username = self._settings["proxy_username"]
        password = self._settings["proxy_password"]

        if not username or not password:
            return f"http://{url}:{port}"

        return f"http://{username}:{password}@{url}:{port}"
