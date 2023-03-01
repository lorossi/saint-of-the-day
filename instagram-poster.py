import logging
import sys
import time

import schedule

from modules.instagram import Instagram
from modules.saint_factory import SaintFactory


def publish():
    logging.info("Publishing post")
    s = SaintFactory()
    saint = s.generateSaint()
    caption = saint.bio + "\n\n#santodelgiorno #santinoquotidiano"
    i = Instagram()
    i.uploadImage(image_path=saint.image_path, image_caption=caption)
    logging.info("Post published")


def main():
    logging.info("Starting instagram poster")
    schedule.every().day.at("08:00").do(publish)
    logging.info("Posts scheduled")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    if sys.argv[1] == "now":
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        publish()
    else:
        filename = __file__.replace(".py", ".log")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            filename=filename,
            filemode="w",
        )
        main()
