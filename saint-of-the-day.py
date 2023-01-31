"""This module starts the bot and sets up the logging module."""
import logging

from modules.telegrambot import TelegramBot


def main():
    """Start the bot."""
    filename = __file__.replace(".py", ".log")
    logging.basicConfig(
        level=logging.INFO,
        filename=filename,
        filemode="w",
        format="%(name)s - %(levelname)s - %(message)s",
    )
    t = TelegramBot()
    t.start()


if __name__ == "__main__":
    main()
