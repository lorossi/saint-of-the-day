"""This module starts the bot and sets up the logging module."""
import logging

from modules.telegrambot import TelegramBot


def main() -> None:
    """Start the bot."""
    t = TelegramBot()
    t.start()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        filename= __file__.replace(".py", ".log"),
        filemode="w",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    main()
