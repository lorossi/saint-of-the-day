"""This module contains the logic of the telegram bot."""
from __future__ import annotations
from typing import Any

import datetime
import logging
import os
import sys
import traceback

import pytz
import toml
from telegram import Update, constants
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    ContextTypes,
)

from modules.saint_factory import SaintFactory


class TelegramBot:
    """Class handling the logic of the telegram bot."""

    _timezone: pytz.timezone = pytz.timezone("Europe/Rome")

    def __init__(self, settings_path: str = "settings.toml") -> TelegramBot:
        """Initialize the bot.

        Returns:
            TelegramBot
        """
        logging.info("Initializing bot")
        self._factory = SaintFactory()
        self._settings = self._loadSettings(settings_path)
        self._post_time = self._loadPostTime()
        self._application = ApplicationBuilder().token(self._settings["token"]).build()
        self._job_queue = self._application.job_queue

        self._job_queue.run_daily(
            self._postSaint,
            time=self._post_time,
            days=(0, 1, 2, 3, 4, 5, 6),
        )
        self._job_queue.run_once(
            self._botStarted,
            when=0,
        )

        self._application.add_error_handler(self._errorHandler)

        self._application.add_handlers(
            [
                CommandHandler("santodelgiorno", self._startCommandHandler),
                CommandHandler("postnow", self._postSaint),
                CommandHandler("start", self._startCommandHandler),
                CommandHandler("reset", self._resetCommandHandler),
                CommandHandler("ping", self._pingCommandHandler),
            ]
        )
        logging.info("Bot initialized")

    def _loadSettings(self, path: str) -> dict[str, str]:
        """Load settings from a TOML file.

        Args:
            path (str): Path to the TOML file.

        Returns:
            dict[str, str]: Settings.
        """
        with open(path) as f:
            return toml.load(f)[self.__class__.__name__]

    def _loadPostTime(self) -> datetime.time:
        """Load the time at which the bot posts the saint.

        Returns:
            datetime.time: Time at which the bot posts the saint.
        """
        return datetime.datetime.strptime(self._settings["post_time"], "%H:%M").replace(
            tzinfo=self._timezone
        )

    def _loadGenerateTime(self) -> datetime.time:
        """Load the time at which the bot generates the saint.

        Returns:
            datetime.time: Time at which the bot generates the saint.
        """
        return datetime.datetime.strptime(
            self._settings["generate_time"], "%H:%M"
        ).replace(tzinfo=self._timezone)

    async def _startCommandHandler(self, update: Update, context: ContextTypes) -> None:
        logging.info("Received /start command")
        chat_id = update.effective_chat.id
        text = (
            "*Benvenuto nel bot del Santino Quotidiano!*\n\n"
            f"Vieni a trovarci su {self._settings['channel_name']}\n"
            f"Link di invito: {self._settings['channel_url']}\n"
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=constants.ParseMode.MARKDOWN,
        )

    async def _resetCommandHandler(self, update: Update, context: ContextTypes) -> None:
        logging.info("Received /reset command")
        chat_id = update.effective_chat.id
        if chat_id != self._settings["admin_chat_id"]:
            logging.warning("Unauthorized access to /reset command")
            return

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="*Riavvio...*",
            parse_mode=constants.ParseMode.MARKDOWN,
        )

        logging.info("Bot restarted")
        os.execl(sys.executable, sys.executable, *sys.argv)

    async def _pingCommandHandler(self, update: Update, context: ContextTypes) -> None:
        logging.info("Received /ping command")
        chat_id = update.effective_chat.id
        await context.bot.send_message(
            chat_id=chat_id,
            text="🏓* PONG *🏓",
            parse_mode=constants.ParseMode.MARKDOWN,
        )

    async def _errorHandler(self, _: Update, context: ContextTypes) -> None:
        logging.error(f"Exception while handling an update: {context.error}")
        tb_list = traceback.format_exception(
            None, context.error, context.error.__traceback__
        )
        await context.bot.send_message(
            chat_id=self._settings["admin_chat_id"],
            text=f"Exception while handling an update: {context.error}",
        )
        logging.error(f"Traceback: {''.join(tb_list)}")

    async def _postSaint(self, **_: Any) -> None:
        logging.info("Posting saint")
        saint = self._factory.generateSaint()
        image_path = saint.image_path
        await self._application.bot.send_photo(
            chat_id=self._settings["channel_name"],
            photo=open(image_path, "rb"),
            caption=saint.bio,
        )

    async def _botStarted(self, _: CallbackContext) -> None:
        logging.info("Bot started")
        await self._application.bot.send_message(
            chat_id=self._settings["admin_chat_id"],
            text="*Bot avviato!*",
            parse_mode=constants.ParseMode.MARKDOWN,
        )

    def start(self) -> None:
        """Start the bot."""
        logging.info("Starting bot")
        self._application.run_polling()
