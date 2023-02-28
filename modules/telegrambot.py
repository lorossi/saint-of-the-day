"""This module contains the logic of the telegram bot."""
from __future__ import annotations

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
    def __init__(self, settings_path: str = "settings.toml") -> TelegramBot:
        """Initialize the bot.

        Returns:
            TelegramBot
        """
        logging.info("Initializing bot")
        self._factory = SaintFactory()
        self._settings = self._loadSettings(settings_path)

        self._application = ApplicationBuilder().token(self._settings["token"]).build()
        self._job_queue = self._application.job_queue
        # add job to run at midnight
        timezone = pytz.timezone("UTC")
        midnight = datetime.time(0, 0, 0, tzinfo=timezone)

        self._job_queue.run_daily(
            self._generateSaint,
            time=midnight,
            days=(0, 1, 2, 3, 4, 5, 6),
        )
        self._job_queue.run_once(
            self._generateSaint,
            when=0,
        )
        self._job_queue.run_once(
            self._botStarted,
            when=0,
        )

        self._application.add_error_handler(self._errorHandler)

        self._application.add_handlers(
            [
                CommandHandler("santodelgiorno", self._saintOfTheDayHandler),
                CommandHandler("start", self._startCommandHandler),
                CommandHandler("reset", self._resetCommandHandler),
                CommandHandler("ping", self._pingCommandHandler),
            ]
        )
        logging.info("Bot initialized")

    def _loadSettings(self, path: str) -> dict[str, str]:
        with open(path) as f:
            return toml.load(f)[self.__class__.__name__]

    async def _startCommandHandler(self, update: Update, context: ContextTypes) -> None:
        logging.info("Received /start command")
        chat_id = update.effective_chat.id
        text = (
            "*Benvenuto nel bot del santo del giorno!*\n"
            "Premi /santodelgiorno per conoscere il santo del giorno."
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

    async def _errorHandler(self, _: Update, context: ContextTypes):
        logging.error(f"Exception while handling an update: {context.error}")
        tb_list = traceback.format_exception(
            None, context.error, context.error.__traceback__
        )
        await context.bot.send_message(
            chat_id=self._settings["admin_chat_id"],
            text=f"Exception while handling an update: {context.error}",
        )
        logging.error(f"Traceback: {''.join(tb_list)}")

    async def _generateSaint(self, _: CallbackContext) -> None:
        logging.info("Generating new saint")
        self._factory.generateSaint()

    async def _botStarted(self, _: CallbackContext) -> None:
        logging.info("Bot started")
        await self._application.bot.send_message(
            chat_id=self._settings["admin_chat_id"],
            text="*Bot avviato!*",
            parse_mode=constants.ParseMode.MARKDOWN,
        )

    async def _saintOfTheDayHandler(
        self, update: Update, context: ContextTypes
    ) -> None:
        logging.info("Received /santodelgiorno command")
        chat_id = update.effective_chat.id
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        saint = self._factory.generateSaint()
        image_path = saint.image_path
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=open(image_path, "rb"),
            caption=f"*Santo del giorno:* {saint.bio}",
            parse_mode=constants.ParseMode.MARKDOWN,
        )

    def start(self):
        """Start the bot."""
        logging.info("Starting bot")
        self._application.run_polling()
